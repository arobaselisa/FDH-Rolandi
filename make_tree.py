import os
import sys, getopt
import os.path
from os import path

## Executing all the scripts from segmentation to the resulting json file

def main(argv):
   name = ''
   key = ''
   try:
      opts, args = getopt.getopt(argv,"n:k:",["name=", "key="])
   except getopt.GetoptError:
      print('make_tree.py -n <name> -k <key>') # Key path for google vision API
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
      if opt in ("-k", "--key"):
         key = arg
   if path.isdir('./data/'+ name):
      print('Starting the process...')
      #os.system("python ./code/segmentation.py -n " + name)
      #os.system("python ./code/ocr.py -n " + name + " -k " + key)
      os.system("python ./code/bounds.py -n " + name)
      os.system("python ./code/extraction_and_cleaning.py -n " + name)
      os.system("python ./code/network.py -n " + name)
      
   else:
       print('Folder ./data/' + name + ' does not exist ! Try to run init_folders.py -n <name>')
       sys.exit(2)
  

if __name__ == "__main__":
   main(sys.argv[1:])
