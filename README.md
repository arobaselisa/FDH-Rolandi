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


## Datasets
The libretti' training and testing datasets have all been randomly fetched from the [Fondazione Giorgio Cini website](http://dl.cini.it/collections/show/1120).
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
* **Create Network Tree of the libretto**: `python make_tree.py -n <libretto_name> -k  <path_to_google_vision_KEY>`
* **Move newly created network_2.json**: Move manually the network_2.json file from "data/<libretto_name>/3_Network" into "/docs/data"
* **Add network into website**: At line 74 in "/docs/index.html", add `<option value="network_2.json"><libretto_name></option>`
* **Visualize the netwoek**: Go to the [website](https://arobaselisa.github.io/FDH-Rolandi/) and select the <libretto_name> you want to visualize.

## Folders (TODO)

### code
### data
### docs
### draft
### params
### ressources
### init_folders
### make_tree

## Wiki-Report
[Link to our Wiki-Report](http://fdh.epfl.ch/index.php/Opera_Rolandi_archive)

This document contains:
* A description of the path we took to obtain the final result
* An explanation of the challenges that we faced and design decisions that we took
