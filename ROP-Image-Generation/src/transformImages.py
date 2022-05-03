# -*- coding: utf-8 -*-
"""
Program: transformImages.py
Description: apply normalization and transformation on ROP-Images.
Author: Mathieu Brunner.
"""

#%% Modules importation.
import pandas as pd
import numpy as np
import csv

#%% List of transformations.
def Sigmoid(data) : # Bijection R -> [0,1]
    """
    Applies sigmoid function on input data.
    
    Parameters :
        data : numpy array. Normalized ROP-Image content.
    
    Returns :
        result : numpy array. Sigmoid(data).
    """
    return 1 / (1 + np.exp(-data))


#%% Function definition.

def normalization(data) :
    """
    Applies normalization on input data.
    
    Parameters :
        data : numpy array. ROP-Image content.
        
    Returns :
        result : numpy array. Normalized input.
    """
    # Check undefined case.
    if np.std(data) == 0.0 : return data
    else : return (data - np.mean(data)) / np.std(data)

def normalization2(data):

    data = data - data.min()
    if data.max() != 0:
        data = data / data.max()
    return data

def writeIntoCsv(data, savePath) :
    """
    Writes normalized and transformed data into .csv file.
    
    Parameters :
        data : numpy array. Data to write into .csv file.
        savePath : string. Path for .csv file to write.
        
    Returns :
        no return.
    """
    
    # Writing .csv file.
    with open(savePath, "w", newline='', encoding='latin1') as file :
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Writing row for each variable.
        for i in range(np.shape(data)[0]) :
            writer.writerow(data[i,:])
        
        file.close()

def dataTransform(path, savePath) :
    """
    Applies above functions on data.
    
    Parameters :
        path : string. Path for data to import.
        savePath : string. Path for .csv file to write.
        
    Returns :
        no return.
    """
    
    data = pd.read_csv(path, sep=";", header=None, dtype=np.float32) # Data importation.
    data = data.to_numpy() # Convert pandas dataframe into numpy array.
    data = normalization(data)
    data = normalization2(data) # Data normalization.
    # Applying transformation.
    #data = Sigmoid(data)

    # Writing results into .csv file.
    writeIntoCsv(data, savePath)

#%% Main function.
   
# Parallelizable function. One processor for each stratified variable. 
def transformImages(var, path) :
    """
    Calls dataTransform for given stratified variable.
    
    Parameters :
        var : integer. Id of stratified variable.
        path : string. Path for folder containing ROP-Results.
        
    Returns :
        no return.
    """
    
    # Apply transformation for all NIC-ROP-Images.
    for NIC in range(1,97) :
        resPath = path + "a" + str(var) + "/"
        # Apply transformation for all ROP-Images for a given NIC.
        imgPath = resPath + "Images/NIC" + str(NIC) + "/" + str(var) + ".csv"
        savePath = resPath + "ImagesTransform/NIC" + str(NIC) + "/"  + str(var) + ".csv"
        dataTransform(imgPath, savePath)

