import os
import sys, getopt
import os.path
from os import path
from cv2 import cv2
import numpy as np
import os
import pandas as pd
import json
import collections
import string
import re


#Define attributes to extract in images as well as their parameters
dict_attribute = {'Name': {'page_0_lower': 0, 
                            'page_0_upper':4/10, 
                            'page_1_lower':4/10, 
                            'page_1_upper':7/10,
                            'width_box': 0.4,
                            'height_box':0.4,
                            'ocr_proba_threshold':0.2, 
                            'mean_proba_threshold':0.7},
                   'Scene': {'page_0_lower': 0, 
                             'page_0_upper':4/10, 
                             'page_1_lower':5/10, 
                             'page_1_upper':8/10, 
                             'width_box': 0.4,
                             'height_box':0.4,
                             'ocr_proba_threshold':0.1, 
                             'mean_proba_threshold':0.7},
                   'Description': {'page_0_lower': 0, 
                                   'page_0_upper':1/2, 
                                   'page_1_lower':1/2, 
                                   'page_1_upper':1,
                                   'width_box': 0,
                                   'height_box':0,
                                   'ocr_proba_threshold':0.1, 
                                   'mean_proba_threshold':0.5}
                  }


def define_range(path, attribute):
    ''' Defining the ranges of the first and second pages '''
    # Original image
    shape = cv2.imread(path,0).shape
    
    # Range of x_0
    x_0_lower = shape[1]*dict_attribute[attribute]['page_0_lower']
    x_0_upper = shape[1]*dict_attribute[attribute]['page_0_upper']
    # Range of x_1
    x_1_lower = shape[1]*dict_attribute[attribute]['page_1_lower'] 
    x_1_upper = shape[1]*dict_attribute[attribute]['page_1_upper']  

    return x_0_lower, x_0_upper, x_1_lower, x_1_upper



def change_x(coord, x_0_lower, x_0_upper, x_1_lower, x_1_upper):  
    ''' Returns the page where the word is
        0 in the first page
        1 in the second page
        -1 if not in the range 
    '''
    if coord >= x_0_lower and coord <= x_0_upper:
        return 0
    elif coord >= x_1_lower and coord <= x_1_upper:
        return 1
    else:
        return -1



def find_bounds(text, dict_bounds, mask, x_0_lower, x_0_upper, x_1_lower, x_1_upper, attribute):
    ''' Finds the names and bounds in the image '''
    proba = np.array([])
    
    # Defining the portion of the height of the box we want to keep
    ratio_y = int((text['Bottom_Right_Y'] - text['Top_Left_Y'])*dict_attribute[attribute]['width_box'])
    # Defining the portion of the width of the box we want to keep
    ratio_x = int((text['Bottom_Right_X'] - text['Top_Left_X'])*dict_attribute[attribute]['height_box'])
    
    # Going through every pixel of the reduced box
    for y in range(text['Top_Left_Y'] + ratio_y, text['Bottom_Right_Y'] - ratio_y):
        for x in range(text['Top_Left_X'] + ratio_x, text['Bottom_Right_X'] - ratio_x):
            # Find their associated probability of being a name
            proba = np.append(proba, mask[y][x])
            
    # Finding the mean probability of being the corresponding attribute for all the pixels in the reduced box        
    mean = proba.mean()
    if mean > dict_attribute[attribute]['mean_proba_threshold']:
        # Depending on coord_x, append extracted text and bounds on page 0 (left) or 1 (right) 
        coord_x = change_x(text['Top_Left_X'], x_0_lower, x_0_upper, x_1_lower, x_1_upper)
        if coord_x != -1:
            if coord_x in dict_bounds:
                dict_bounds[coord_x].append((text['Top_Left_Y'], attribute, text['Text']))
            else:    
                dict_bounds[coord_x] = [(text['Top_Left_Y'], attribute, text['Text'])]



def find_attributes_one_image(page, libretto):
    ''' Returns the attributes and bounds in one image '''
    
    # Data from segmentation
    segmentation_path = "./data/" + libretto + "/1_Segmentation_results/output/" + page + ".npy"
    data = np.load(segmentation_path)
    
    dict_bounds = dict()
    for i, attribute in enumerate(dict_attribute.keys()):
        # Create x ranges
        x_0_lower, x_0_upper, x_1_lower, x_1_upper = define_range("./data/" + libretto + "/0_Images/" + page + ".jpg", attribute)
        
        # Threshold for attributes segmentation
        mask = np.where(data[i+1]>dict_attribute[attribute]['ocr_proba_threshold'],1,0).astype(np.uint8)

        # Load results from OCR
        image_df = pd.read_csv("./data/" + libretto + "/2_OCR_results/annotations_" + page + ".csv", index_col=0)

        # Find the attributes and bounds
        image_df.apply(lambda row: find_bounds(row, dict_bounds, mask, x_0_lower, x_0_upper, x_1_lower, x_1_upper, attribute), axis=1)
    return dict_bounds
                



def order_dict(dictionnary):
    ''' Returns ordered dictionnary of bounds per pages and per coordinates '''
    for pages in dictionnary.values():
        for ind in [0,1]:
            if ind in pages.keys():
                pages[ind].sort(key=lambda x: x[0])
    return sorted(dictionnary.items(), key = lambda kv:(int(kv[0][1:]), kv[1]))


def save_dict_in_json(dictionnary, path):
    ''' Saves ordered dictionnary of bounds per pages and per coordinates in a json file'''
    with open(path, "w") as outfile:  
        json.dump(dictionnary, outfile) 


def load_json_in_dict(path):
    ''' Loads ordered dictionnary of bounds per pages and per coordinates from a json file'''
    with open(path) as json_file: 
        return json.load(json_file)


def find_attributes(libretto):
    attributes_bounds = []
    pages = []
    # Going through all the images
    for filename in os.listdir("./data/"+libretto+"/0_Images/"):
        if filename.endswith(".jpg"): 
            file_without_extension = os.path.splitext(filename)[0]
            #print(file_without_extension)
            pages.append(file_without_extension)
            # Find attribute in the image
            dict_bounds = find_attributes_one_image(file_without_extension, libretto)
            attributes_bounds.append(dict_bounds)
            #print(dict_bounds)
            continue
        else:
            continue
    return order_dict(dict(zip(pages, attributes_bounds)))

def main(argv):
   name = ''
   try:
      opts, args = getopt.getopt(argv,"n:",["name="])
   except getopt.GetoptError:
      print('bounds.py -n <name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
   if path.isdir('./data/'+ name):
       try: 
          print("Finding the intersection of the bounds from OCR and segmentation...")
          dictionnary = find_attributes(name)
          print("Saving the results in the file ./2_OCR_results/"+name+".json")
          save_dict_in_json(dictionnary, "./data/" + name + "/2_OCR_results/"+name+".json")
       except:
          print('Error occured during the process')
          sys.exit(2)
   else:
       print('Folder ./data/' + name + ' does not exist ! Try to run init_folders.py -n <name>')
       sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
