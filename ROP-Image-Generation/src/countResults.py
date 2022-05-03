# -*- coding: utf-8 -*-
"""
Program: countResults.py
Description: gather results obtained after ROP-Training into .csv files.
Author: Mathieu Brunner.
"""

#%% Import modules.
import os
import csv
import numpy as np

#%% Utils.

def deleteSuspiciousFile(folderPath, filename) :
    name = folderPath + "/" + filename
    os.remove(name)

#%% Function definition.

# Definition indices for computing Sensibility and Specificity from results files.
TP_Index = -6
FP_Index = -5
TN_Index = -4
FN_Index = -3

def getSeSp(reader, filename, folderPath) :
    """
    Returns Sensibility and Specificity value from content of a result .csv file.

    Parameters :
        reader : list of lists of strings. List of the rows of a result .csv file.
            Each row is a list containing the content of .csv cells.
        filename : string. Name of ROP-Training sample.
        folderPath : string. Location of this file.

    Returns :
        Se, Sp : tuple of floats. Sensibility and Specificity values.
    """
    global TP_Index, FP_Index, TN_Index, FN_Index
    # Initialization nb of True Positive (TP), etc.
    TP = 0 ; FP = 0 ; TN = 0 ; FN = 0
    # Initialization Sensibility and Specificity values.
    Se = 0 ; Sp = 0

    # Getting TN and FN by going through result .csv file content.
    for row in reader :
        if "R" in row :
            TN += int(row[TN_Index])
            FN += int(row[FN_Index])
    # Getting TP and FP.
    TP += int(reader[-2][TP_Index])
    FP += int(reader[-2][FP_Index])
    # Check if Se and Sp are defined.
    if (TP+FN) == 0 or (TN+FP)==0 :
        return 0, 0
    else :
        Se = TP / (TP + FN)
        Sp = TN / (TN + FP)
    return Se, Sp

def getRows(csvFile, filename, folderPath) :
    """
    Returns list of rows of a result .csv file.

    Parameters :
        csvFile : io.TextIOWrapper. Opened result .csv file in read mode (using Python "open").
        filename : string. Name of ROP-Training sample.
        folderPath : string. Location of this file.

    Returns :
        rows : list of lists of strings. List of the rows of a result .csv file.
            Each row is a list containing the content of .csv cells.
    """
    # Reading the result .csv file with ";" delimiter.
    csvReader = csv.reader(csvFile, delimiter = ';')
    res = []
    try :
        for row in csvReader :
            # Handling files with encoding errors.
            if row != [] :
                if len(row) == 1 : # Case where the delimiter is ",". NOT OPTIMAL.
                    res += [row[0].split(",")]
                else :
                    res += [row]
    except :
        print("There is a problem with this file : ", folderPath, " : ", filename)
    return np.array(res)

def getVarMatrix(folderPath, AP_THRESHOLD) :
    """
    Returns matrix summarizing the results obtained for a ROP-Forest.

    Parameters :
        folderPath : string. Path of folder containing the ROP-Forest.

    Returns :
        varMatrix : list of lists of floats (matrix of floats). Matrix
            summarizing the results obtained for a ROP-Forest. Each row
            corresponds to a variable. See colNames variable for the meaning
            of each column.
    """
    global nbCol
    global bestVar
    os.chdir(folderPath)
    #print("Current working directory : ", os.getcwd())

    # Getting list of files to go through.
    listFiles = os.listdir(folderPath)

    # Initialization.
    varMatrix = np.zeros(nbCol,np.int32)
    NIC_count = np.zeros((len(listFiles),10),np.int32)

    # Check if the specified folder is empty.
    if len(listFiles)==0 :
        print("Empty folder : ", folderPath)
        return varMatrix
    
    # Filling the varMatrix variable by going through each result .csv file.
    for count,filename in enumerate(listFiles) :

        if filename.endswith("_res.csv") :

            try:

                with open(filename, "r", encoding='latin1') as file :
                    reader = getRows(file, filename, folderPath)

                    # Check if file is empty.
                    if reader == [] :
                        print("Empty res : ", folderPath, " : ", filename)
                        file.close()
                        deleteSuspiciousFile(folderPath, filename)
                        print("This file has been deleted.")
                        continue

                    listVar = [] # List variables in tree.
                    listIndex = [] # Column of each variable in tree.

                    # Getting which variables are in the tree.
                    for i, val in enumerate(reader[0]) :
                        if val != "" :
                            if val[0]=="a" :
                                varId = int(val[1:])
                                listVar += [varId]
                                listIndex += [i]
                    varIdx = listIndex[-1]
                    varMatrix[0] += 1 # Increase counter of selected variables.
                    if np.intersect1d(bestVar,listVar) == []:
                        NIC_count[count,9] = 1
                    # Getting Sensibility and Specificity values.
                    Se, Sp = getSeSp(reader, filename, folderPath)

                    if Se == 0 and Sp == 0 :
                        print("Error for Se/Sp computation: ", folderPath, " : ", filename)
                        file.close()
                        deleteSuspiciousFile(folderPath, filename)
                        print("This file has been deleted.")
                        continue

                    # Check if tree is perfect.
                    if Se*Sp  >= AP_THRESHOLD :
                        varMatrix[1] += 1
                        NIC_count[count,0] = 1 # Perfect tree counter. NIC1

                        listCoef = []
                        for i in range(3,len(reader)) :
                            coef = reader[i][varIdx]
                            if coef != "" and coef != "R" :
                                listCoef += [float(coef)]
                        
                        if all(elem != 0 for elem in listCoef) :
                            varMatrix[2] += 1
                            NIC_count[count,1] = 1 # Coeffs != 0 counter. NIC2
                            if not all(elem < 0 for elem in listCoef) and not all(elem > 0 for elem in listCoef) :
                                varMatrix[5] += 1
                                NIC_count[count,4] = 1 # NIC6
                            
                        if all(elem > 0 for elem in listCoef) :
                            varMatrix[3] += 1
                            NIC_count[count,2] = 1 # Coeffs > 0 counter. NIC3
                            
                        if all(elem < 0 for elem in listCoef) :
                            varMatrix[4] += 1
                            NIC_count[count,3] = 1 # Coeffs < 0 counter. NIC4
                            
                        # Nb cycles = 1.
                        if int(reader[-2][0])==1 :
                            varMatrix[6] += 1
                            NIC_count[count,5] = 1 # Nb cycles = 1 counter. NIC7
                            # Nb nodes = 1.
                            if all(elem <= 1 for elem in list(map(int,filter(None,reader[2:-1,1])))) :
                                varMatrix[7] += 1
                                NIC_count[count,6] = 1 # (Nb cycles = 1 + nb nodes = 1) counter. NIC8

                        # Solutions finies.
                        if all(elem != "1" and elem != "4" for elem in list(filter(None,reader[3:,-2]))):
                            varMatrix[8] += 1
                            NIC_count[count,7] = 1 # Solutions != 4 counter. NIC9
                        # Solution unique.
                        if all(elem == "1" for elem in list(filter(None,reader[3:,-2]))) :
                            varMatrix[9] += 1
                            NIC_count[count,8] = 1 # Solutions = 1 counter. NIC10
                file.close()


            except :
                print("Problem with file : ", folderPath, " : ", filename)
                file.close()
    varMatrix[10] = np.sum(NIC_count[:,1]*NIC_count[:,5])                                 # NIC2 et NIC7
    varMatrix[11] = np.sum(NIC_count[:,1]*NIC_count[:,6])                                 # NIC2 et NIC8
    varMatrix[12] = np.sum(NIC_count[:,1]*NIC_count[:,7])                                 # NIC2 et NIC9
    varMatrix[13] = np.sum(NIC_count[:,1]*NIC_count[:,8])                                 # NIC2 et NIC10
    varMatrix[14] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,5])                # (NIC3 ou NIC4) et NIC7
    varMatrix[15] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,6])                # (NIC3 ou NIC4) et NIC8
    varMatrix[16] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,7])                # (NIC3 ou NIC4) et NIC9
    varMatrix[17] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,8])                # (NIC3 ou NIC4) et NIC10
    varMatrix[18] = np.sum(NIC_count[:,5]*NIC_count[:,7])                                 # NIC7 et NIC9
    varMatrix[19] = np.sum(NIC_count[:,5]*NIC_count[:,8])                                 # NIC7 et NIC10
    varMatrix[20] = np.sum(NIC_count[:,6]*NIC_count[:,7])                                 # NIC8 et NIC9
    varMatrix[21] = np.sum(NIC_count[:,6]*NIC_count[:,8])                                 # NIC8 et NIC10
    varMatrix[22] = np.sum(NIC_count[:,1]*NIC_count[:,5]*NIC_count[:,7])                  # NIC2 et NIC7 et NIC9
    varMatrix[23] = np.sum(NIC_count[:,1]*NIC_count[:,5]*NIC_count[:,8])                  # NIC2 et NIC7 et NIC10
    varMatrix[24] = np.sum(NIC_count[:,1]*NIC_count[:,6]*NIC_count[:,7])                  # NIC2 et NIC8 et NIC9
    varMatrix[25] = np.sum(NIC_count[:,1]*NIC_count[:,6]*NIC_count[:,8])                  # NIC2 et NIC8 et NIC10
    varMatrix[26] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,5]*NIC_count[:,7]) # (NIC3 ou NIC4) et NIC7 et NIC9
    varMatrix[27] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,5]*NIC_count[:,8]) # (NIC3 ou NIC4) et NIC7 et NIC10
    varMatrix[28] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,6]*NIC_count[:,7]) # (NIC3 ou NIC4) et NIC8 et NIC9
    varMatrix[29] = np.sum((NIC_count[:,2]+NIC_count[:,3])*NIC_count[:,6]*NIC_count[:,8]) # (NIC3 ou NIC4) et NIC8 et NIC10

    return varMatrix

def countResults(folderPath, resName, AP_THRESHOLD) :
    """
    Generates a .csv file summarizing the results obtained for a ROP-Forest.

    Parameters :
        folderPath : string. Path of folder containing the ROP-Forest.
        resName : string. Path of .csv file to write.

    Returns :
        no return.
    """
    global colNames
    #print("Processing : ", folderPath.split("/")[-3:])

    # Getting the matrix which will be written on disk.
    varMatrix = getVarMatrix(folderPath, AP_THRESHOLD)

    # Write varMatrix content on disk.
    with open(resName, "w", newline='', encoding='latin1') as file :
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Add columns names.
        writer.writerow(colNames)

        # Add row for each variable.
        writer.writerow(varMatrix)

        file.close()

#%% Main function.

# Define hard-wire constants.
colNames = ['Nb tirages au sort', 'Nb AP Trees', 'Coeffs != 0', 'Coeffs > 0',
            'Coeffs < 0', 'Autres cas', 'Nb cycles = 1', 'Nb cycles = 1 et Nb etapes = 1',
            'Toutes solutions != 4', 'Toutes solutions = 1','NIC2 et 7', 'NIC2 et 8',
            'NIC2 et 9', 'NIC2 et 10', 'NIC34 et 7', 'NIC34 et 8',
            'NIC34 et 9','NIC34 et 10','NIC7 et 9','NIC7 et 10',
            'NIC8 et 9','NIC8 et 10','NIC2 et 7 et 9','NIC2 et 7 et 10',
            'NIC2 et 8 et 9','NIC2 et 8 et 10','NIC34 et 7 et 9','NIC34 et 7 et 10',
            'NIC34 et 8 et 9','NIC34 et 8 et 10']
nbCol = len(colNames)
bestVar = [28657,24209,30923,19615,19421,50609,10921,17223,37637,34294,36931,36718,14811,37308,32527,10429]

# Parallelizable function. One processor for each stratified variable.
def countVarResults(var, infR, supR, infV, supV, data_path, count_path, AP_THRESHOLD) :
    """
    Calls countResults function for given stratified variable for all configurations.

    Parameters :
        COULD CHANGE.

    Returns :
        no return.
    """

    # Defining reference path and result path.
    refPath = data_path + "a" + str(var) + "/"
    resPath = count_path + "a" + str(var) + "/"

    # Summing up results for all configurations of range of simulation and nb of selected variables.
    for i in range(infR,supR+1) :
        for j in range(infV,supV+1) :
            folderPath = refPath + "R" + str(i) + "/V" + str(j)
            resName = resPath + "R" + str(i) + "V" + str(j) + "_res.csv"
            countResults(folderPath, resName, AP_THRESHOLD)

