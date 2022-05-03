# -*- coding: utf-8 -*-
"""
Program: fuseImages.py
Description: fuse NIC-ROP-Images.
Author: Mathieu Brunner.
"""

#%% Modules importation.
import csv
import numpy as np
import os
import pandas as pd

#%% Function definition.

def getNICImage(varId, NIC, imgPath) :
    """
    Imports NIC matrix for given stratified variable and NIC.

    Parameters :
        varId : integer. Variable id.
        NIC : integer. NIC id.
        imgPath : string. Path for image folder.

    Returns :
        data : numpy array. Imported ROP-NIC-Image.
    """

    # Data import.
    filename = imgPath + "NIC" + str(NIC) + "/" + str(varId) + ".csv"
    data = pd.read_csv(filename, sep=";", header=None, dtype=np.float32)
    return data.to_numpy()

def getImageMatrix(varId, imgPath, width, height) :
    """
    Returns Fuse-ROP-Image.

    Parameters :
        varId : integer. Variable id.
        imgPath : string. Path for image folder.
        width, height : integer. Width and height are generated ROP-Images.

    Returns :
        M : numpy array. Fuse-ROP-Image.
    """

    # Initialization of Fuse-ROP-Image.
    M = np.zeros((height*8, width*12))
    coords = np.array(np.meshgrid(np.arange(8),np.arange(12))).T.reshape(-1,2)
    np.random.seed(10)              # Generate fixed random order
    np.random.shuffle(coords)

    # Getting each NIC-ROP-Image.
    for i in range(96):
        NIC = getNICImage(varId,i+1,imgPath)
        M[coords[i,0]*height:(coords[i,0]+1)*height,coords[i,1]*width:(coords[i,1]+1)*width] = NIC

    return M

def fuseImage(varId, imgPath, resPath, width, height) :
    """
    Writes Fuse-ROP-Image as .csv file on disk.

    Parameters :
        varId : integer. Variable id.
        imgPath : string. Path for image folder.
        resPath : string. Path for writing .csv file.
        width, height : integer. Width and height are generated ROP-Images.

    Returns :
        no return.
    """

    # Getting Fuse-ROP-Image.
    M = getImageMatrix(varId, imgPath, width, height)

    # Writing Fuse-ROP-Image into .csv file.
    with open(resPath, "w", newline='', encoding='latin1') as file :
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Writing row for each variable.
        for i in range(len(M)) :
            writer.writerow(M[i])
            
        # Delete return line at the end of the file.
        file.seek(0, os.SEEK_END)
        file.seek(file.tell()-2, os.SEEK_SET) # -2 is platform-dependent. Could be -1 on another one.
        file.truncate()

        file.close()

#%% Main.

# Parallelizable function. One processor for each stratified variable.
def fuseImages(var, width, height, path) :
    """
    Calls fuseImage for given stratified variable.

    Parameters :
        var : integer. Id of stratified variable.
        width, height : integer. Width and height are generated ROP-Images.
        path : string. Path for folder containing ROP-Results.

    Returns :
        no return.
    """

    # Define constants.
    imgPath = path + "a" + str(var) + "/ImagesTransform/"
    resFolder = path + "a" + str(var) + "/Images/" + "Fuse/"

    resPath = resFolder + str(var) + ".csv"
    fuseImage(var, imgPath, resPath, width, height)
