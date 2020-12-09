import numpy as np
import pandas as pd
import json
import collections
import string
import re
import io 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from difflib import SequenceMatcher as sm
import os
import sys, getopt
import os.path
from os import path
import subprocess
from utils import save_dict_in_json
from utils import load_json_in_dict


def remove_stopwords(text):
    '''
    Outputs text with removed stopwords in all kind of cases 
    :param string text: italian string text extracted from libretto
    '''
    #Create list of italian stopwords in all cases
    stop_words = stopwords.words('italian')+[word.title() for word in stopwords.words('italian')]+[word.upper() for word in stopwords.words('italian')]
    #Tokenize text and remove word if it is a stopword
    text_tokens = word_tokenize(text)
    tokens_without_sw = [word for word in text_tokens if not word in stop_words]
    return tokens_without_sw

def extract_all_attributes(data):
    '''
    Extract all atributes extracted by OCR in order, whithout storing coordinates or pages
    :param list data: extracted italian text of libretto separated by pages and coordinates
    '''
    elements = np.empty(shape=(0,2))
    # for each page of the libretto
    for page in range(len(data)):
        # for each left and/or right page
        for ind in data[page][1].keys():
            # extract elements in the order they appear, without storing coordinates or pages
            elements = np.concatenate((elements, np.array(data[page][1][ind])[:, 1:]), axis = 0)
    return elements

def extract_attribute(elements, attribute):
    '''
    Extract elements in order from specific attribute
    :param numpy.ndarray elements: elements ['Label', 'Text'] stored in the order they appear in 
    :param string attribute: the label/attribute to extract ('Name', 'Description', 'Scene')
    '''
    # Extract text from specific attribute
    text_list = [row[1] for row in elements if attribute in row[0]]
    # Create string
    text = " ".join(text_list)
    # Remove digits
    text = ''.join([i for i in text if not i.isdigit()])
    # Remove punctuations
    text = text.translate(str.maketrans(dict.fromkeys(string.punctuation)))
    # Remove stopwords
    text = remove_stopwords(text)
    return text

def extract_names_abbreviations(names, top_N=15):
    '''
    Extract top-N most common abbreviation names
    :param list names: list of abbreviation names
    :param int top_N, default=15: number of most common abbreviations names to extract
    '''
    #Create the list of abbreviation names to return
    names_abbreviations = []
    #Extract the top_N most common abbreviations names figuring in the list names
    frequent_names = collections.Counter(names).most_common()[:top_N]
    for name, count in frequent_names:
        names_abbreviations.append(name)
    return list(set(names_abbreviations))

def list_patterns(names_abbreviations):
    '''
    Create list of patterns from abbreviation names
    :param list names_abbreviations: list of unique abbreviation names
    '''
    #Create a pattern for each abbreviation name by adding a '.*' after each character
    #This means that the character is followed by 0 or more other characters until it meets the next character 
    #of the pattern.
    patterns = list(map('.*'.join, names_abbreviations))
    #Creat a list of correct patterns to return
    correct_patterns = []
    #For each patter remove the '.*'following the first character of the name
    for pattern in patterns:
        correct_patterns.append(pattern.replace(".*", "", 1) + ".*")
    return correct_patterns

def filter_pattern(pattern, description):
    '''
    Filter list of abbreviations by given pattern
    :param string pattern: a regex pattern
    :param list description: a list of text from which we need to extract words with the given pattern
    '''
    #list of all words from description which matched the pattern
    occurences = [val for val in description if re.search(pattern, val)]
    if len(occurences) > 0:
        return occurences
    else:
        return []

def find_complete_name(pattern, text, abbreviation):
    '''
    Returns most common name who follows the given pattern
    :param string pattern: a regex pattern corresponding to the given abbreviation
    :param string text: a list of text from which we need to extract words with the given pattern
    :param string abbreviation: the abbreviation name for which the complete name is being searched
    '''
    #list of all words from text which matched the pattern
    occurences = filter_pattern(pattern, text)
    #Extract the most common word form the list of occurences
    most_common_name = collections.Counter(occurences).most_common(1)
    #If a name has been extracted from the list of occurences, then return it with all
    #the other words matching the pattern as well as the abbreviation from ehich the pattern
    #has been derived.
    if (len(most_common_name) > 0) and (len(occurences) > 0):
        return most_common_name[0][0], occurences+[abbreviation]
    return  None, None
    
def extract_complete_names(names, description):
    '''
    Extract dictionnary of characters complete names and their respective similar names
    :param list names: list of abbreviation names
    :param list description: a list of text from which we need to extract words with the given pattern
    '''
    #Extract abbrevations names
    names_abbreviations = extract_names_abbreviations(names)
    #Extract patterns for each of the abreviation names
    patterns = list_patterns(names_abbreviations)

    #A dictionnary which will store for each most common complete name all occurences 
    #of words which come from the same pattern.
    dic = {}
    #For each abbreviation and pattern, we are going to find its most common complete name
    for abbreviation, pattern in zip(names_abbreviations, patterns):
        name, name_mappings = find_complete_name(pattern, description, abbreviation)
        #Check whether a complete name was found in the description list of texts
        if name != None:
            #If the name is already contained in the dictionnary, then it means the pattern 
            #found many names which probably had been misspelled by the OCR and which we
            #therefore need to correct.
            if name in dic:
                dic[name] =dic[name] + name_mappings
            else:
                dic[name] = name_mappings
    return dic, names_abbreviations


def complete_names_to_correct(dic, threshold=0.60):
    '''
    Extract a dictionnary of complete names with their respective similar names and a set 
    complete names to remove if they are similar in the Levenshtein distance metric sense.
    :param dictionnary dic: a dictionnary of characters complete names and their respective similar names
    :param float threshold: the Levenshtein similitude ratio needed to confirm that two words are similar
    '''
    #The dictionnary which will store the similar complete names and their respective similar 
    #wording in the same key.
    dic_new = {}
    names_keys = list(dic.keys())
    names_values = list(dic.values())
    #The set of complete names to remove from the dictionnary as their are similar. Will be replaced correctly.
    keys_to_remove = set()
    #For each pair of complete names, check wether the names are similar
    for i in range(len(names_keys)):
        for j in range(i+1, len(names_keys)):
            if(sm(None, names_keys[i], names_keys[j]).ratio() >= threshold):
                #As the names are similar, check which of the two names has the longest 
                #list of extracted similar words coming from the same pattern. This will then
                #be the correct complete name.
                key_index = j if (len(names_values[i]) < len(names_values[j])) else i
                keys_to_remove.add(names_keys[i])
                keys_to_remove.add(names_keys[j])
                if names_keys[key_index] in dic_new.keys():
                    dic_new[names_keys[key_index]].extend(names_values[i])
                    dic_new[names_keys[key_index]].extend(names_values[j])
                else:
                    dic_new[names_keys[key_index]] = names_values[i]
                    dic_new[names_keys[key_index]].extend(names_values[j])
    #Remove duplicates 
    dic_new = {k:list(set(j)) for k,j in dic_new.items()}
    return dic_new, keys_to_remove

def match_abbrev_with_complete_names(dic, names_to_remove, dic_names_corrected, abbreviations):
    '''
    Output the dictionnary which map abbreviation names with their correct complete name
    :param dictionnary dic: a dictionnary of characters complete names and their respective similar names
    :param set names_to_remove: a set of string complete names to remove as they match other names
    :param dictionnary dic_names_corrected: a dictionnary of aggregated similar complete names
    '''
    #For all key names to remove, remove them from dictionnary of complete names
    for k in names_to_remove :
        dic.pop(k)
    #Update the dictionnary of complete names with the names of the removed keys 
    dic.update(dic_names_corrected)
    #Remove duplicates from the list of similar words for each key complete name 
    #in the dictionnary of complete names
    dic = {k:list(set(j)) for k,j in dic.items()}
    #For each complete name in the dictionnary, keep only the abbreviation names
    for k,v in dic.items():
        dic[k] = list(set(abbreviations) & set(v))
    #Inverse the dictionnary to obtain as keys the abbreviation names and as values the complete name
    #with which it will be replaced
    dic_inv = {}
    for key,list_val in dic.items():
        for val in list_val:
            dic_inv[val] = key
    return dic_inv

def remove_first_scenes(attributes_clean):
    '''
    We need to delete from the list the 'SCENA' related to the 'PRIMA'
    Otherwise it is counted twice
    '''
    mask = np.ones((np.shape(attributes_clean)))
    attributes_clean_lower = np.array([[att[0], att[1].lower().translate(str.maketrans(dict.fromkeys(string.punctuation)))] for att in attributes_clean])
   
    for i, att in enumerate(attributes_clean_lower):
        if (att[0]=='Scene'):
            if (att[1]=='prima'):
                neighbor = i
                distance = -1
                while(attributes_clean_lower[neighbor][0] != 'Scene' or (attributes_clean_lower[neighbor][1]!= 'scena' and attributes_clean_lower[neighbor][1]!= 'scen' and attributes_clean_lower[neighbor][1]!= 'sceno')):
                    neighbor = max(0,neighbor + distance)
                    distance = (distance * -1) - 1 if distance > 0 else (distance * -1) + 1
                mask[neighbor] = 0
    attributes_clean = attributes_clean[mask.astype(np.bool)]
    attributes_clean = attributes_clean.reshape(int(np.shape(attributes_clean)[0]/2), 2)
    return attributes_clean
                    
                
def clean_attributes(all_attributes, dic_names):
    ''' 
    Adds the acts in the attributes and stores the scenes as numbers 
    :param list attributes: the list containing all attributes
    :param dictionnary dic_names: the dictionnary which maps abbreviations with complete names
    '''
    attributes_clean = all_attributes.copy()

    attributes_clean = remove_first_scenes(attributes_clean)

    count_scene = 0
    mask = np.ones((np.shape(attributes_clean)))
    # Goes through all the list
    for i, att in enumerate(attributes_clean):
        # through all the text that has the 'Scene' tag
        if (att[0]=='Scene'):
            # Remove punctuation and case
            word = att[1].lower().translate(str.maketrans(dict.fromkeys(string.punctuation)))
            # If a scene is the first one, we add the begining of an act
            if (word=='prima'):
                count_scene = 1
                attributes_clean[i] = ['Scene', count_scene]
            # Detects the scene, stores its number
            elif (word=='scena' or word=='scen' or word=='sceno'):
                count_scene += 1
                attributes_clean[i] = ['Scene', count_scene]
            else:
            # Otherwise, we will delete this row
                mask[i] = 0
        if (att[0]=='Name'):
            # Remove punctuation and case
            word = att[1].translate(str.maketrans(dict.fromkeys(string.punctuation)))
            if (word in dic_names.keys()):
                attributes_clean[i] = ['Name', dic_names[word]]
            else: 
                mask[i] = 0
        if (att[0]=='Description'):
            mask[i] = 0
    # Delete rows that we don't need anymore
    attributes_clean = attributes_clean[mask.astype(np.bool)]
    attributes_clean = attributes_clean.reshape(int(np.shape(attributes_clean)[0]/2), 2)
   
   # Add acts
    ind_prima = np.array(np.where(attributes_clean[:,1]=='1')).ravel()
    count_act = np.shape(ind_prima)[0]
    for i in ind_prima[::-1]:
        attributes_clean = np.insert(attributes_clean, i, ["Act", count_act], axis=0)
        count_act -= 1
        
    return attributes_clean


def create_tree(attributes_clean):
    ''' 
    Create the tree structure of our libretto 
    :param numpy.ndarray attributes_clean: the list containing all attributes in the order of appearance
    '''
    #Creat dictionnary which will store the tree
    final_dic = {}
    #Loop through all cleaned attributes
    for i, att in enumerate(attributes_clean):
        #If attribute is 'Act' tag, create empty dictionnary to store the Scenes
        if (att[0]=='Act'):
            final_dic[int(att[1])] = {}
        #If attribute is 'Scene' tag, stay in the least added Act and add an empty dictionnary to store the Names
        if (att[0]=='Scene'):
            dic_act = final_dic[list(final_dic.keys())[-1]]
            dic_act[int(att[1])] = {}
        #If attribute is 'Name' tag, stay in the least added Scene and add the Name in the dictionnary 
        #with a counter == 1. Each time the name reappers, add 1 to the counter. The counter represents the
        #occurences of the name in the scene
        if (att[0]=='Name'):
            dic_act = final_dic[list(final_dic.keys())[-1]]
            dict_scene = dic_act[list(dic_act.keys())[-1]]
            if att[1] in dict_scene.keys():
                dict_scene[att[1]] += 1
            else:
                dict_scene[att[1]] = 1
    return final_dic



def main(argv):
   name = ''
   try:
      opts, args = getopt.getopt(argv,"n:",["name="])
   except getopt.GetoptError:
      print('extraction_and_cleaning.py -n <name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
   if path.isdir('./data/'+ name):
       #try: 
        print('Loading json tree data...')
        data = load_json_in_dict("./data/" + name + "/2_OCR_results/" + name + ".json")
        print("Extracting attributes from the libretto...")
        all_attributes = extract_all_attributes(data)

        #Lists of text from the defined attribute
        description = extract_attribute(all_attributes, 'Description')
        names = extract_attribute(all_attributes, 'Name')
        print("Attributes found")
        
        print("Finding complete names...")
        dic, abbreviations = extract_complete_names(names, description)
        dic_names_corrected, names_to_remove = complete_names_to_correct(dic)
        print("Matching with abbreviations...")
        dic_names = match_abbrev_with_complete_names(dic, names_to_remove, dic_names_corrected, abbreviations)
        print("Making a clear list...")
        attributes_clean = clean_attributes(all_attributes, dic_names)
        tree = create_tree(attributes_clean)
        save_dict_in_json(tree, "./data/" + name + "/3_Network/network.json")
        print('Json tree saved.')
      # except:
       #   print('Error occured during the process')
        #  sys.exit(2)
   else:
       print('Folder ./data/' + name + ' does not exist ! Try to run init_folders.py -n <name>')
       sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
