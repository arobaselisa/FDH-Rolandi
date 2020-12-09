import json

def save_dict_in_json(dictionnary, path):
    ''' Saves ordered dictionnary of bounds per pages and per coordinates in a json file'''
    with open(path, "w") as outfile:  
        json.dump(dictionnary, outfile) 


def load_json_in_dict(path):
    ''' Loads ordered dictionnary of bounds per pages and per coordinates from a json file'''
    with open(path) as json_file: 
        return json.load(json_file)
