# Project of Foundation of Digital Humanities (DH-405 EPFL)

## Table of content
* [Goal](#goal)
* [Datasets](#datasets)
* [Team Members](#team-members)
* [Link to Website](#link-to-website)
* [Requirements](#requirements)
* [Create Visualization for new libretto](#create-visualization-for-new-libretto)
* [Folders](#folders)
* [Wiki-Report](#wiki-report)

## Goal
The Fondazione Giorgio Cini has digitized 36000 pages from Ulderico Rolandi's opera [http://dl.cini.it/collections/show/1120 libretti collection]. This collection contains contemporary works of 17th- and 18th-century composers. These opera libretti have a diverse content, which offers a large amount of possibilities for analysis.

This project concentrates on a way to illustrate the characters’ interactions in the Rolandi's libretti collection through network visualization as well as the importance of each character in the acts they figure in. To achieve this, we retrieved important information using the DHLAB Deep Learning model [dhSegment-torch](https://github.com/dhlab-epfl/dhSegment-torch) and [Google Vision OCR](https://cloud.google.com/vision/docs/ocr) by focusing on a small subset of libretti.

## Datasets
The libretti's training and testing datasets have all been randomly fetched from the [Fondazione Giorgio Cini website](http://dl.cini.it/collections/show/1120).
For the prediction and network visualizations, we decided to focus on two libretti only:
* [MUS0279827 - Antigona](http://dl.cini.it/collections/show/333)
* [MUS0010824 - Gli americani](http://dl.cini.it/collections/show/435)

## Team members
* Elisa Michelet, 282651
* Gonxhe Idrizi, 275001

## Link to Website
[Our website](https://arobaselisa.github.io/FDH-Rolandi/) of the Interactive Network Visualization.

## Requirements
* Import libraries: run `conda create --name <myenv> --file spec-file.txt`
* Follow the steps to [setup Google-Vision](https://cloud.google.com/vision/docs/setup#billing)

## Create Visualization for new libretto
If someone wants to create a visualization network for a new libretto, they have to follow the following steps:
* **Choose libretto**: Import images of the libretto pages starting from the first scene. You can do this in the [Fondazione Giorgio Cini website](http://dl.cini.it/collections/show/1120).
* **Initialize folder**: `python init_folders.py -n <libretto_name>`
* **Move imported images to correct folder**: This step has to be done manually. You have to move the imported libretto images into the folder "data/<libretto_name>/0_Images".
* **[Optional] Change hyper-parameters**: You can change the hyperparamters in "params/params.json".
* **Create Network Tree of the libretto**: `python make_tree.py -n <libretto_name> -k  <path_to_google_vision_KEY>` During the process, you will be asked to write the password to the cluster where the model is, only Elisa and Gonxhe know it, please contact us if you want to use this.

* **Move newly created network_2.json**: Move manually the network_2.json file from "data/<libretto_name>/3_Network" into "/docs/data"
* **Add network into website**: At line 74 in "/docs/index.html", add `<option value="network_2.json"><libretto_name></option>`
* **Visualize the network**: Go to the [website](https://arobaselisa.github.io/FDH-Rolandi/) and select the <libretto_name> you want to visualize.

## Folders

### code

* **ocr.py**
Contains the methods making use of the Google Vision API for the detection and extraction of the text words with their respective surrounding boxes coordinates.

* **bounds.py**
Contains the methods which permits to segment the images such that they extract the desired attributes in the correct order of appearance and store them in an order dictionary.

* **segmentation.py**
Contains the methods for accessing the DHLAB clusters, for training our deep learning models and for predicting the probabilities of each pixel of an image to belong to a certain class (Scene, Description or Abbreviation name). For one to be able to run these methods, he/she may have to change the clusters paths on which he/she is going to run the model.

* **extraction_and_cleaning.py**
Contains all the methods which clean the variants, errors and unnecessary elements from the extracted attribute values. It also creates a final json tree structure of the elements in a hierarchical fashion:
** the root is the libretto name
** the nodes on level 1 are the acts, the children of the root
** the nodes on level 2 are the scenes, the children of the acts
** the nodes on the leaves are the names of the characters with their respective occurrences in the scene

* **network.py**
Contains the methods which restructure the json tree structure file from **extraction_and_cleaning.py** into another json format suitable for the d3.js and website visualization implementation.

* **evaluation.py**
Contains the evaluation metrics which determine how similar is the predicted tree structure containing the acts, scene and occurrences of characters to the ground truth tree structure extracted manually.

* **utils.py**
Contains the common methods for saving or loading a dictionary from a json file.

### data
* **training_data**
Contains the data we trained the [dh-Segment](https://github.com/dhlab-epfl/dhSegment-torch) model on. Pages of random libretti and their manually segmented pair.
* **libretti**
Contains the folders created by the `init_folders.py` script. One per libretto.
    * **0_Images**:
Contains the different pages of the libretto.
    * **1_Segmentation_results**:
Contains the output of the segmentation model, numpy arrays of dimensions `size_of_the_image * 4`
    * **2_OCR_results**:
Contains the results of the segmentations done by Google Vision API in csv. Also contains a json of the full text.
    * **3_Network**:
Contains network.json : the network representation of the libretto.
network_truth.json : if one made by hand the ground truth of the network.
network_2.json : the network representation used for the website.
    * **4_Evaluation**:
Contains a plot of the error of our algorithm.

### docs
* **code.js**
The JavaScript file containing the methods for implementing the relationship network in d3.js as well as the interactive toolboxes.

* **index.html**
The html file containing the DOM structure of the website and the paths of the libretti for which the relationship networks are plotted.

* **data**
The folder containing the libretti datasets used in the website relationship network plotting.

### draft
Contains everything that we coded throughout this project, but didn't use in the final results

### params
Contains a json of the parameters we use in the bounds and OCR, for the three categories (Name, Scene, Description) :
* **page_0_lower**: for the OCR, where do we start the first page
* **page_0_upper**: for the OCR, where do we end the first page
* **page_1_lower**: for the OCR, where do we start the second page
* **page_1_upper**: for the OCR, where do we end the second page
* **width_box**: for the bounds, how much width do we take of the box returned by the OCR
* **height_box**: for the bounds, how much height do we take off the box returned by the OCR
* **ocr_proba_threshold**: from the results of the OCR, starting from which probability do we consider that a pixel is in a certain category
* **mean_proba_threshold**: when summing all of the pixels from a box, what threshold probability do we set such that higher is a word of interest, and lower is not.

### init_folders
The script that you need to run when starting with a new libretto. Will create all the subfolders needed for the rest of the algorithm.

### make_tree
The script that you need to run to create the tree from the libretto images. Will first run the segmentation on the images, then the OCR, then finding the attributes of interest and order them, and finally create a network out of them.

## Wiki-Report
[Link to our Wiki-Report](http://fdh.epfl.ch/index.php/Opera_Rolandi_archive)

This document contains:
* A description of the path we took to obtain the final result
* An explanation of the challenges that we faced and design decisions that we took
