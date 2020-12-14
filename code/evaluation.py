from zss import simple_distance, Node
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_json_in_dict
import io
import os
import sys, getopt
import os.path
from os import path


def create_tree(libretto, gt = False):
    ''' 
    Creates a tree structure of the desired libretto for the computation of the later similarity distance
    :param string libretto: the name of the libretto we want to process
    :param boolean gt, default=False: if gt==True, we select the ground_truth dataset, else we select the predicted one.
    '''
    # Load data
    data = ""
    if gt:
        data = load_json_in_dict("../data/"+libretto+"/3_Network/network_truth.json")
    else:
        data = load_json_in_dict("../data/"+libretto+"/3_Network/network.json")
    
    # Create tree root
    tree = Node(libretto)
    # Create nodes
    for act in data.keys():
        node_act = Node(act)
        for scene in data[act].keys():
            node_scene = Node(scene)
            for char in data[act][scene].keys():
                # Create leaves
                for i in range(data[act][scene][char]):
                    node_scene.addkid(Node(char))
            node_act.addkid(node_scene)
        tree.addkid(node_act)
    return (tree)


def compute_similarity(libretto):
    ''' 
    Computes the similarity distance of one libretto, based on its ground-truth and predicted data
    :param string libretto: the name of the libretto we want to process
    '''
    # Create the tree from the ground-truth data
    gt_tree = create_tree(libretto, gt = True)
    # Create the tree from the predicted data
    predicted_tree = create_tree(libretto, gt = False)
    return simple_distance(gt_tree, predicted_tree)


def create_subtree(act, scene, data):
    ''' 
    Creates a sub-tree structure of the desired libretto for the computation of the later similarity distance.
    It creates a sub-tree where the root is a predefined scene in a predefined act.
    :param string act: the act of the libretto we want to process
    :param string scene: the scene of the libretto we want to process
    :param dict data: the json data file of the libretto we want to process
    '''
    # Create root
    node_scene = Node(scene)
    for char in data[act][scene].keys():
        # Create leaves
        for i in range(data[act][scene][char]):
            node_scene.addkid(Node(char))
    return node_scene


def distance_scenes(data_gt, data_predict, act, scene):
    ''' 
    Compute the similarity distance for the sub-tree structures of the desired libretto.
    The sub-tree has as the root a predefined scene from a predefined act.
    :param zss.Node data_gt: the ground-truth tree
    :param zss.Node data_predict: the predicted tree
    :param string act: the act of the libretto we want to process
    :param string scene: the scene of the libretto we want to process
    '''
    # Create sub-trees
    node_scene_gt = create_subtree(act, scene, data_gt)
    node_scene_predict = create_subtree(act, scene, data_predict)
    
    dist = simple_distance(node_scene_gt, node_scene_predict) 
    return dist


def plot_distances(libretto, data_gt, data_predict, total_error): 
    ''' 
    Plot the similarity distance for the sub-tree structures of the desired libretto.
    This will permit to get the number of errors encountered per scene and per act
    :param string libretto: the name of the libretto we want to process
    :param zss.Node data_gt: the ground-truth tree
    :param zss.Node data_predict: the predicted tree
    :param int total_error: the error on the whole libretto
    '''
    dist_act = list()
    #Compute distance plot only for acts in two subtrees
    for act in data_gt.keys():
        if (act in data_predict.keys()):
            dist_scene = list()
            #Compute distance plot only for scenes in two subtrees
            for scene in data_gt[act].keys():
                if (scene in data_predict[act].keys()):
                    dist_scene.append(distance_scenes(data_gt, data_predict, act, scene))
            dist_act.append(dist_scene)
            
    # Set style
    sns.set_style("darkgrid")

    # color palette
    colors = ['tab:orange', 'tab:blue', 'tab:red', 'tab:green']
    
    # Plot
    df = pd.DataFrame(dist_act).T.reset_index()
    for col in range(1, df.shape[1]):
        df.rename(columns={col-1: str(col)}, inplace=True)
    for i, col in enumerate(df.columns[1:]):
        sns.scatterplot(data=df, x="index", y=col, color=colors[i])
        sns.lineplot(data=df, x="index", y=col, color=colors[i])
        
    # Add Labels and legend
    plt.xlabel(f"Scene")
    plt.ylabel(f"Number of errors")
    plt.title(f'Error plot of "{libretto}" libretto (total error : {total_error})');
    plt.legend(bbox_to_anchor=(0., -0.35, 1., .102), loc='lower center',
               ncol=2, mode="expand", borderaxespad=0., 
               labels = ["Act " + str(i) for i in range(1, df.shape[1])])
    
    # Save image
    plt.savefig("../data/"+ libretto + "/4_Evaluation/error_plot.png", bbox_inches='tight')


def main(argv):
   name = ''
   try:
      opts, args = getopt.getopt(argv,"n:",["name="])
   except getopt.GetoptError:
      print('evaluation.py -n <name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-n", "--name"):
         name = arg
   if path.isdir('../data/'+ name):
       try: 
          print('Loading networks...')
          data_gt = load_json_in_dict("../data/"+name+"/3_Network/network_truth.json")
          data_predict = load_json_in_dict("../data/"+name+"/3_Network/network.json")
          print('Computing similarity...')
          total_error = compute_similarity(name)
          print('Saving figure...')
          plot_distances(name, data_gt, data_predict, total_error)
          print('Done !')
       except:
          print('Error. Check network.json or network_truth.json in ./3_Network !')
          sys.exit(1)
       
       
   else:
       print('Folder ../data/' + name + ' does not exist ! Try to run init_folders.py -n <name>')
       sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])
