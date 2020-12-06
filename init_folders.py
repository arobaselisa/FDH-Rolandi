import sys, getopt
import os

def main(argv):
   name = ''
   try:
      opts, args = getopt.getopt(argv,"n:",["name="])
   except getopt.GetoptError:
      print('init_folders.py -n <name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
   if name != '':
       if not os.path.exists('data/' + name):
           try:
                print("Creating folder...")
                os.makedirs('data/' + name)
                os.makedirs('data/' + name + '/0_Images')
                os.makedirs('data/' + name + '/1_Segmentation_results')
                os.makedirs('data/' + name + '/2_OCR_results')
                os.makedirs('data/' + name + '/3_Network')
                print('Successfully created folder ' + name)
           except:
                print('Error occured when creating folder ' + name)
       else:
           print('Folder ' + name + ' already exists !')
   else:
       print('Please add a name : init_folders.py -n <name>')

if __name__ == "__main__":
   main(sys.argv[1:])