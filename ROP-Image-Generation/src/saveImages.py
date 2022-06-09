# -*- coding: utf-8 -*-
"""
Program: saveImages.py
Description: save ROP-Images into SavedImages folder.
Author: Mathieu Brunner.
"""

#%% Modules importation.

import numpy as np
import os
import pandas as pd
import cv2

#%% Function definition.

def getClusterId(var, cluster_path) :
    """
    Returns cluster id from stratified variable id.

    Parameters :
        var : string. Stratified variable id.
        cluster_path : string. Path for .csv file containing clustering results.

    Returns :
        no return.
    """

    # Import clustering results.
    clusters = pd.read_csv(cluster_path, sep=";", header=None, dtype=np.int32).to_numpy()
    
    # Get row index corresponding to variable id.
    row = np.where(clusters == int(var))[0]

    # Get cluster id.
    try :
        cluster_id = clusters[int(row)][1]
    except :
        cluster_id = clusters[int(row[0])][1]

    return cluster_id

def saveImage(var, NIC, image_path, save_path) :
    """
    Saves a .csv image file into .png.

    Parameters :
        var : string. Stratified variable id.
        image_path : string. .csv image file's path.
        save_path : string. Path for folder containing saved images.

    Returns :
        no return.
    """

    # Import .csv image file.
    data = pd.read_csv(image_path, sep=";", header=None, dtype=np.float32)
    data = np.array(data)
    # Save image.
    image_name = save_path + "NIC" + str(NIC) + "/" + str(var) + ".jpg"
    cv2.imwrite(image_name,data)

def saveImageByCluster(var, NIC, image_path, res_path, cluster_path) :
    """
    Saves a .csv image file into .png inside the associated class folder.

    Parameters :
        var : string. Stratified variable id.
        image_path : string. .csv image file's path.
        res_path : string. Path for folder containing ROP-Results.
        cluster_path : string. Path for .csv file containing clustering results.

    Returns :
        no return.
    """

    # Import .csv image file.
    data = pd.read_csv(image_path, sep=";", header=None, dtype=np.float32)
    data = np.array(data)
    # Save image.
    cluster_id = getClusterId(var, cluster_path)
    image_name = res_path + "ImagesPNG/NIC" + str(NIC) + "/" + str(cluster_id) + "/" + str(var) + ".jpg"
    cv2.imwrite(image_name,data)
    
def saveFuseImage(var, image_path, save_path, width, height) :
    """
    Saves a .csv Fuse-Image file into .png.

    Parameters :
        var : string. Stratified variable id.
        image_path : string. .csv image file's path.
        save_path : string. Path for folder containing saved images.

    Returns :
        no return.
    """

    # Import .csv image file.
    #data = pd.read_csv(image_path, sep=";", header=None, dtype=np.float32)

    data = np.ones((height*8, width*12,3))
    coords = np.array(np.meshgrid(np.arange(8),np.arange(12))).T.reshape(-1,2)
    np.random.seed(10)              # Generate fixed random order
    np.random.shuffle(coords)

    # Getting each NIC-ROP-Image.
    for i in range(96):
        NIC = pd.read_csv(image_path + "NIC" + str(i+1) + "\\" + str(var) + ".csv",sep=";",header=None,dtype=np.float32)
        if i in range(10):
            data[coords[i,0]*height:(coords[i,0]+1)*height,coords[i,1]*width:(coords[i,1]+1)*width,1] = 1-NIC
            data[coords[i,0]*height:(coords[i,0]+1)*height,coords[i,1]*width:(coords[i,1]+1)*width,2] = 1-NIC
        if i == 0 or i in range(10,30):
            data[coords[i,0]*height:(coords[i,0]+1)*height,coords[i,1]*width:(coords[i,1]+1)*width,0] = 1-NIC
            data[coords[i,0]*height:(coords[i,0]+1)*height,coords[i,1]*width:(coords[i,1]+1)*width,2] = 1-NIC
        if i in range(30,96):
            data[coords[i,0]*height:(coords[i,0]+1)*height,coords[i,1]*width:(coords[i,1]+1)*width,0] = 1-NIC
            data[coords[i,0]*height:(coords[i,0]+1)*height,coords[i,1]*width:(coords[i,1]+1)*width,1] = 1-NIC
    data = 255.0 * (data - data.min())/(data.max() - data.min())
    data = data.astype(np.uint8)
    # Save image.
    image_name = save_path + str(var) + ".png"
    cv2.imwrite(image_name,data)

def deleteImages(path) :
    """
    Deletes all .jpg files in folder given by path variable.

    Parameters :
        path : string. Folder containing the images to delete.

    Returns :
        no return.
    """

    List_Files = os.listdir(path)

    for file in List_Files :
        if file.endswith(".jpg") :
            os.remove(os.path.join(path, file))

#%% Main.

# Parallelizable function. One processor for each stratified variable.
def saveImages(var, res_path, save_path) :
    """
    Calls saveImage for given stratified variable.

    Parameters :
        var : integer. Id of stratified variable.
        res_path : string. Path for folder containing ROP-Results.
        save_path : string. Path for folder containing saved images.

    Returns :
        no return.
    """
    
    for NIC in range(1,97) :
        image_path = res_path + "a" + str(var) + "\\Images\\NIC" + str(NIC) + "\\" + str(var) + ".csv"
        saveImage(var, NIC, image_path, save_path)

# Parallelizable function. One processor for each stratified variable.
def saveImagesByCluster(var, res_path, cluster_path) :
    """
    Calls saveImagebyCluster for given stratified variable.

    Parameters :
        var : integer. Id of stratified variable.
        res_path : string. Path for folder containing ROP-Results.
        cluster_path : string. Path for .csv file containing clustering results.

    Returns :
        no return.
    """
    
    for NIC in range(1,97) :
        image_path = res_path + "a" + str(var) + "\\Images\\NIC" + str(NIC) + "\\" + str(var) + ".csv"
        saveImageByCluster(var, NIC, image_path, res_path, cluster_path)
        
# Parallelizable function. One processor for each stratified variable.
def saveFuseImages(var, res_path, save_path, width, height) :
    """
    Calls saveFuseImage for given stratified variable.

    Parameters :
        var : integer. Id of stratified variable.
        res_path : string. Path for folder containing ROP-Results.
        save_path : string. Path for folder containing saved images.

    Returns :
        no return.
    """

    #image_path = res_path + "a" + str(var) + "\\Images\\Fuse\\" + str(var) + ".csv"
    image_path = res_path + "a" + str(var) + "\\Images\\"
    saveFuseImage(var, image_path, save_path, width, height)











