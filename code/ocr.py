from google.cloud import vision
import io
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from cv2 import cv2
from PIL import Image
import sys, getopt
import os.path
from os import path


# Path to google private keys on personnal computers
KEY_GONXHE = 'C:/Users/gonxh/Documents/EPFL/Master/MA3/Foundations_of_DH/DH - Rolandi Libretti-a52be57f8f03.json'
KEY_ELISA = '/Users/elisamichelet/Documents/EPFLMaster/FDH/Projet/private_key.json'

def resize_image(file_without_extension, libretto):
    ''' Resizes the image to make it the same size as the segmentation output '''

    #Load npy
    image_path = "./data/" + libretto + "/0_Images/" + file_without_extension + ".jpg"
    segmentation_path = "./data/" + libretto + "/1_Segmentation_results/output/" + file_without_extension + ".npy"
    # Output data
    data = np.load(segmentation_path)
    # Resize original image (test)
    img = cv2.imread(image_path,0)
    img = cv2.resize(img, (np.shape(data)[2], np.shape(data)[1]))
    img = Image.fromarray(img)
    img.save(image_path)


def make_df(texts, filename, libretto):
    ''' Saves a dataframe with the text in the image and its coordinates '''

    df = pd.DataFrame()
    for text in texts[1:]:
        df_row = pd.DataFrame({"Text":[text.description], 
                    "Top_Left_X":[text.bounding_poly.vertices[0].x],
                    "Top_Left_Y":[text.bounding_poly.vertices[0].y],
                    "Bottom_Right_X":[text.bounding_poly.vertices[2].x],
                    "Bottom_Right_Y":[text.bounding_poly.vertices[2].y]}) 
        df = df.append(df_row, ignore_index=True)
    df.to_csv('./data/' + libretto + '/2_OCR_results/annotations_' + filename + '.csv')  



def detect_text(filename, key_path, libretto):
    ''' Performs the OCR on one image '''
    
    # Google client
    client = vision.ImageAnnotatorClient.from_service_account_json(key_path)
    
    # Image to OCR
    with io.open("./data/" + libretto + "/0_Images/" + filename + ".jpg", 'rb') as image_file:
        content = image_file.read()   
    # OCR
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    # Saving result in a dataframe
    make_df(texts, filename, libretto)
    

def OCR(key_path, libretto):
    ''' Performs the OCR on the entire libretto '''
    
    # Going through all the images
    for filename in os.listdir("./data/" + libretto + "/0_Images"):
        if filename.endswith(".jpg"): 
            file_without_extension = os.path.splitext(filename)[0]
            # Resize image
            resize_image(file_without_extension, libretto)
            # OCR
            detect_text(file_without_extension, key_path, libretto)
            continue
        else:
            continue


def main(argv):
   name = ''
   key = ''
   try:
      opts, args = getopt.getopt(argv,"n:k:",["name=", "key="])
   except getopt.GetoptError:
      print('ocr.py -n <name> -k <key>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
      if opt in ("-k", "--key"):
         if arg == 'Elisa':
             key = KEY_ELISA
         elif arg == 'Gonxhe':
             key = KEY_GONXHE
         else:
             key = arg
   if path.isdir('./data/'+ name):
       try: 
          print('Performing OCR on all images, might take a few minutes...')
          OCR(key, name)
          print('Successfully performed the OCR')
       except:
          print('Error occured during the OCR ')
          sys.exit(2)
   else:
       print('Folder ./data/' + name + ' does not exist ! Try to run init_folders.py -n <name>')
       sys.exit(2)
  

if __name__ == "__main__":
   main(sys.argv[1:])
