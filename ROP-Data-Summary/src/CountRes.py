# -*- coding: utf-8 -*-
"""
Program: CountRes.py
Description: gather results obtained after ROP-Training into a Matrix.
Author: Gabriel LUCAS.
"""

# %% Import modules.
import os
import csv
import numpy as np

def deleteSuspiciousFile(folderPath, filename):
    name = folderPath + "/" + filename
    os.remove(name)

# %% Function definition.


# Definition indices for computing Sensibility and Specificity from results files.
TP_Index = -6
FP_Index = -5
TN_Index = -4
FN_Index = -3


def getSeSp(reader, filename, folderPath):
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
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    # Initialization Sensibility and Specificity values.
    Se = 0
    Sp = 0

    # Getting TN and FN by going through result .csv file content.
    for row in reader:
        if "R" in row:
            TN += int(row[TN_Index])
            FN += int(row[FN_Index])
    # Getting TP and FP.
    TP += int(reader[-2][TP_Index])
    FP += int(reader[-2][FP_Index])
    # Check if Se and Sp are defined.
    if (TP+FN) == 0 or (TN+FP) == 0:
        return 0, 0
    else:
        Se = TP / (TP + FN)
        Sp = TN / (TN + FP)
    return Se, Sp


def getRows(csvFile, filename, folderPath):
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
    csvReader = csv.reader(csvFile, delimiter=';')
    res = []
    try:
        for row in csvReader:
            # Handling files with encoding errors.
            if row != []:
                # Case where the delimiter is ",". NOT OPTIMAL.
                if len(row) == 1:
                    res += [row[0].split(",")]
                else:
                    res += [row]
    except:
        print("There is a problem with this file : ",
              folderPath, " : ", filename)
    return np.array(res)

def getVarMatrix(folderPath, AP_THRESHOLD,nbCol):
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
    os.chdir(folderPath)
    #print("Current working directory : ", os.getcwd())

    # Getting list of files to go through.
    listFiles = os.listdir(folderPath)

    # Initialization.
    varMatrix = np.zeros(nbCol-1, np.int32)
    # Check if the specified folder is empty.
    if len(listFiles) == 0:
        print("Empty folder : ", folderPath)
        return varMatrix

    # Filling the varMatrix variable by going through each result .csv file.
    for count, filename in enumerate(listFiles):
        if filename.endswith("_res.csv"):

            try:

                with open(filename, "r", encoding='latin1') as file:
                    reader = getRows(file, filename, folderPath)

                    # Check if file is empty.
                    if reader == []:
                        print("Empty res : ", folderPath, " : ", filename)
                        file.close()
                        deleteSuspiciousFile(folderPath, filename)
                        print("This file has been deleted.")
                        continue

                    listVar = []  # List variables in tree.
                    listIndex = []  # Column of each variable in tree.

                    # Getting which variables are in the tree.
                    for i, val in enumerate(reader[0]):
                        if val != "":
                            if val[0] == "a":
                                varId = int(val[1:])
                                listVar += [varId]
                                listIndex += [i]
                    varIdx = listIndex[-1]
                    varMatrix[0] += 1  # Increase counter of selected variables.
                    
                    # Getting Sensibility and Specificity values.
                    Se, Sp = getSeSp(reader, filename, folderPath)

                    if Se == 0 and Sp == 0:
                        print("Error for Se/Sp computation: ",
                            folderPath, " : ", filename)
                        file.close()
                        deleteSuspiciousFile(folderPath, filename)
                        print("This file has been deleted.")
                        continue

                    # Check if tree is perfect.
                    if Se*Sp >= AP_THRESHOLD:
                        varMatrix[1] += 1

                        listCoef = []
                        for i in range(3, len(reader)):
                            coef = reader[i][varIdx]
                            if coef != "" and coef != "R":
                                listCoef += [float(coef)]

                        if all(elem != 0 for elem in listCoef):
                            varMatrix[2] += 1
                            if not all(elem < 0 for elem in listCoef) and not all(elem > 0 for elem in listCoef):
                                varMatrix[5] += 1

                        if all(elem > 0 for elem in listCoef):
                            varMatrix[3] += 1

                        if all(elem < 0 for elem in listCoef):
                            varMatrix[4] += 1

                        # Nb cycles = 1.
                        if int(reader[-2][0]) == 1:
                            varMatrix[6] += 1
                            # Nb nodes = 1.
                            if all(elem <= 1 for elem in list(map(int, filter(None, reader[2:-1, 1])))):
                                varMatrix[7] += 1
                                # (Nb cycles = 1 + nb nodes = 1) counter. NIC8

                        # Solutions finies.
                        if all(elem != "1" and elem != "4" for elem in list(filter(None, reader[3:, -2]))):
                            varMatrix[8] += 1
                        # Solution unique.
                        if all(elem == "1" for elem in list(filter(None, reader[3:, -2]))):
                            varMatrix[9] += 1
                file.close()

            except:
                print("Problem with file : ", folderPath, " : ", filename)
                file.close()

    return varMatrix