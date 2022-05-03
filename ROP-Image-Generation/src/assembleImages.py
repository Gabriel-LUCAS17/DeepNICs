# -*- coding: utf-8 -*-
"""
Program: assembleImages.py
Description: generate ROP-Images.
Author: Mathieu Brunner.
"""

#%% Import modules.
import csv

#%% Function definition.

def getMatrix(NIC, NIC_Path, width, height) :
    """
    Returns NIC-ROP-Image for specified variable.

    Parameters :
        NIC : integer. NIC for which a ROP-Image is generated.
        NIC_Path : string. Path for NICmatrix folder.
        width, height : integer. Width and height of generated ROP-Images.

    Returns :
        M : list of lists of floats (matrix of floats). NIC-ROP-Image.
    """
    # Initialization of ROP-Image.
    res = [[0 for i in range(width)] for j in range(height)]
    # Filling the image.
    for i in range(3,width+3) : # Range of simulation range.
        for j in range(3,height+3) : # Nb selected variables.
            filename = NIC_Path + "R" + str(i) + "V" + str(j) + "_res.csv"
            # Reading NICmatrix for given configuration.
            with open(filename, "r", encoding='latin1') as file :
                data = csv.reader(file, delimiter = ';')
                # Iterate through .csv rows until the searched one.
                row = data.__next__()
                if len(row) == 1 : res[height-j+2][i-3] = row[0].split(",")[int(NIC)-1]
                else : res[height-j+2][i-3] = row[int(NIC)-1]
                file.close()
    return res

def assembleImage(NIC, imgPath, NIC_Path, width, height) :
    """
    Writes ROP-Image into .csv file.

    Parameters :
        NIC : integer. NIC for which a ROP-Image is generated.
        imgPath : string. Path for written .csv file.
        NIC_Path : string. Path for NICmatrix folder.
        width, height : integer. Width and height of generated ROP-Images.

    Returns :
        no return.
    """

    # Getting image content.
    M = getMatrix(NIC, NIC_Path, width, height)

    # Writing image on disk.
    with open(imgPath, "w", newline='', encoding='latin1') as file :
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Writing row for each variable.
        for i in range(len(M)) :
            writer.writerow(M[i])

        file.close()


#%% Main.

# Parallelizable function. One processor for each stratified variable.
def assembleImages(var, width, height, path) :
    """
    Calls assembleImage for given stratified variable.

    Parameters :
        var : integer. Id of stratified variable.
        width, height : integer. Width and height of generated ROP-Images.
        path : string. Path for folder containing ROP-Results.

    Returns :
        no return.
    """

    # Constant definition.
    resPath = path + "a" + str(var) + "/"
    NIC_Path = resPath + "NICmatrix/"

    # Generation of images for all NIC.
    for NIC in range(1,97) :
        imgFolder = resPath + "Images/NIC" + str(NIC) + "/"
        imgPath = imgFolder + str(var) + ".csv"
        assembleImage(NIC, imgPath, NIC_Path, width, height)


