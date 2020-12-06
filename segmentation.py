import os
import sys, getopt
import os.path
from os import path
import subprocess


def clean_previous():
    HOST="gidrizi@iccluster131.iccluster.epfl.ch"
    COMMAND="cd /dhlabdata4/gonxhe/dhSegment-torch; ls; rm -r 0_Images"
    ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    ssh.stdout.readlines()
   

def seg():
    HOST="gidrizi@iccluster131.iccluster.epfl.ch"
    COMMAND="cd /dhlabdata4/gonxhe/dhSegment-torch; ls; cd output; rm *; cd ..; source activate dh_segment_torch; python './scripts/predict_probas.py' './configs/predict_probas.jsonnet'"
    ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    ssh.stdout.readlines()
    

def main(argv):
   name = ''
   try:
      opts, args = getopt.getopt(argv,"n:",["name="])
   except getopt.GetoptError:
      print('segmentation.py -n <name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
   if path.isdir('./data/'+ name):
       try: 
          print('Cleaning testing directory from cluster.')
          clean_previous()
          print('Done cleaning the directory.')
          print('Importing local data to cluster')
          os.system("scp -r ./data/" + name + "/0_Images "+ " gidrizi@iccluster131.iccluster.epfl.ch:/dhlabdata4/gonxhe/dhSegment-torch/")
          print('Done importing local data to cluster')
          print('Segmentation started. Might take a few minutes.')
          seg()
          print('Segmentation done.')
          print('Importation of results')
          os.system("scp -r gidrizi@iccluster131.iccluster.epfl.ch:/dhlabdata4/gonxhe/dhSegment-torch/output ./data/"+ name +"/1_Segmentation_results")
          print('Importation done.')
       except:
          print('Error occured during the process')
          sys.exit(2)
   else:
       print('Folder ./data/' + name + ' does not exist ! Try to run init_folders.py -n <name>')
       sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
