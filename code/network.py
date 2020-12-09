import numpy as np
import pandas as pd
import json
import collections
import string
import io
import os
import sys, getopt
import os.path
from os import path
import subprocess
from cv2 import cv2
import string
import re
from utils import save_dict_in_json
from utils import load_json_in_dict




def making_json(libretto):
    # Load data
    data = load_json_in_dict("./data/"+libretto+"/3_Network/network.json")

    # Create links
    network_array_links = pd.DataFrame(columns=['source', 'target'])
    network_array_nodes = pd.DataFrame(columns=['id'])
    for act in data.keys():
        name= "act"+act
        network_array_links[name] = 0
        network_array_nodes[name] = 0
        for scene_i in data[act].keys():
            characters = sorted(list(data[act][scene_i].keys()))
            for i, character_i in enumerate(characters):
                if not network_array_nodes['id'][network_array_nodes['id'].isin([character_i])].empty:
                    network_array_nodes.loc[network_array_nodes['id']==character_i, name] += 1
                else:
                    network_array_nodes = network_array_nodes.append({"id":character_i, name:1}, ignore_index=True)

                for character_j in characters[i+1:]:
                    if not network_array_links['source'][network_array_links['source'].isin([character_i])].empty:
                        char_i = network_array_links['source']==character_i
                        if not network_array_links[char_i]['target'][network_array_links[char_i]['target'].isin([character_j])].empty:
                            char_j = network_array_links['target']==character_j
                            network_array_links.loc[char_i & char_j, name] += 1
                        else:
                            network_array_links = network_array_links.append({"source":character_i, "target":character_j, name:1}, ignore_index=True)
                    else:
                        network_array_links = network_array_links.append({"source":character_i, "target":character_j, name:1}, ignore_index=True)
    network = {"nodes": network_array_nodes.to_dict('records'), "links": network_array_links.to_dict('records')}
    # Save data
    save_dict_in_json(network, "./data/"+libretto+"/3_Network/network_2.json")

def main(argv):
   name = ''
   try:
      opts, args = getopt.getopt(argv,"n:",["name="])
   except getopt.GetoptError:
      print('network.py -n <name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
   if path.isdir('./data/'+ name):
       try: 
          print('Ordering the json in a nice way for the graph visualisation...')
          making_json(name)
          print('Json saved.')
       except:
          print('Error occured during the process')
          sys.exit(2)
   else:
       print('Folder ./data/' + name + ' does not exist ! Try to run init_folders.py -n <name>')
       sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])



