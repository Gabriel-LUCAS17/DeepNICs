# -*- coding: utf-8 -*-
"""
Program: imageClustering.py
Description: cClustering applied to generated-ROP-Images to assign them label.
Author: Mathieu Brunner.
"""

#%% Import modules.
import csv
import numpy as np
import pandas as pd

#%% Functions definition.

def getVariableId(path) :
    """
    Returns variable id for specified path.

    Parameters :
        path : string. Path which contain a variable id.

    Returns :
        id : integer. Variable id.
    """

    return int(path.split("/")[-1][:-4]) # Get last part of path and strip .csv extension.

def getListNames(results_path) :
    """
    Returns list of image names.

    Parameters :
        results_path : string. Path for folder containing ROP-Results.

    Returns :
        listNames : list of strings. List containing image names.
    """

    print("Getting list of image names.")
    filename = results_path + "listNames.txt"
    try :
        with open(filename, "r", encoding='latin1') as file :
            res = []
            line = file.readline()
            while (line != "") :
                res += [line.strip('\n')]
                line = file.readline()
            return res
    except :
        print("Problem when trying to read following file: ", filename)
        exit()
    return None

def getListIds(listNames) :
    """
    Returns list of image ids.

    Parameters :
        listNames : list of strings. List containing image names.

    Returns :
        listIds : list of strings. List containing image ids.
    """

    print("Getting list of image ids.")
    res = []
    for name in listNames :
        res += [getVariableId(name)]
    return res

def ImportImageDataset(listNames) :
    """
    Returns imported image dataset.

    Parameters :
        listNames : list of strings. List containing image names.

    Returns :
        listImages : numpy array. Array containing flattened images.
    """

    print("Importing image dataset.")
    listImages = []
    for name in listNames :
        listImages += [pd.read_csv(name, sep=";", header=None, dtype=np.float32).to_numpy().flatten()]
    return np.array(listImages)

def DoKMeansClustering(listImages) :
    """
    Returns labels obtained after applying KMeans Clustering algorithm.

    Parameters :
        listImages : numpy array. Array containing flattened images.

    Returns :
        labels : list of integers. Labels of each ROP-Image.
    """

    print("Applying KMeans Clustering algorithm to image dataset.")
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2, random_state=0).fit(listImages)
    return kmeans.labels_

def writeResultsIntoCsv(listIds, labels, save_path) :

    print("Writing results into .csv file : ", save_path)

    with open(save_path, "w", newline='', encoding='latin1') as file :
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Writing row for each variable.
        for i in range(len(listIds)) :
            writer.writerow([listIds[i], labels[i]])


#%% Main.

def Clustering(results_path, save_path) :
    listNames = getListNames(results_path)
    listIds = getListIds(listNames)
    listImages = ImportImageDataset(listNames)
    labels = DoKMeansClustering(listImages)
    writeResultsIntoCsv(listIds, labels, save_path)
