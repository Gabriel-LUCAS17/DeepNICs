# -*- coding: utf-8 -*-
"""
Program: computeNIC.py
Description: program to automatically compute NICs value and export to .csv file.
Author: Mathieu Brunner.
"""

#%% Import modules.
import numpy as np
import pandas as pd
import os
import csv

#%% Function definition.

def computeNIC(path) :
    """
    Write NIC values into .csv file.
  
    Parameters :
        path : string. Path of .csv file written by countResults.py.
    
    Returns :
        no return.
    """
    
    # Import data.
    data = pd.read_csv(path, sep=";", header=None) #, dtype=np.float32)
    data.drop(labels=0, axis=0, inplace=True) # Drop column names.
    data = data.to_numpy().astype(np.int32)
    
    # Constant definition.
    num_col = 96 # Number of NICs.
    
    # Initialization NIC matrix.
    NICmatrix = np.zeros(num_col)
    
    # Compute NICs for all variables.
    if data[0,0] != 0 and data[0,1] != 0 :
        NICmatrix[0] = data[0,1] / data[0,0]           # NIC1.
        NICmatrix[1] = data[0,2] / data[0,1]           # NIC2.
        NICmatrix[2] = data[0,3] / data[0,1]           # NIC3.
        NICmatrix[3] = data[0,4] / data[0,1]           # NIC4.
        NICmatrix[4] = (NICmatrix[2]*NICmatrix[3])**0.25   # NIC5.
        NICmatrix[5] = 1 - data[0,5] / data[0,1]       # NIC6.
        NICmatrix[6] = data[0,6] / data[0,1]           # NIC7.
        NICmatrix[7] = data[0,7] / data[0,1]           # NIC8.
        NICmatrix[8] = data[0,8] / data[0,1]           # NIC9.
        NICmatrix[9] = data[0,9] / data[0,1]           # NIC10.
        NICmatrix[10] = data[0,10] / data[0,1]         # NIC2.7
        NICmatrix[11] = data[0,11] / data[0,1]         # NIC2.8
        NICmatrix[12] = data[0,12] / data[0,1]         # NIC2.9
        NICmatrix[13] = data[0,13] / data[0,1]         # NIC2.10
        NICmatrix[14] = data[0,14] / data[0,1]         # NIC34.7
        NICmatrix[15] = data[0,15] / data[0,1]         # NIC34.8
        NICmatrix[16] = data[0,16] / data[0,1]         # NIC34.9
        NICmatrix[17] = data[0,17] / data[0,1]         # NIC34.10
        NICmatrix[18] = data[0,18] / data[0,1]         # NIC7.9
        NICmatrix[19] = data[0,19] / data[0,1]         # NIC7.10
        NICmatrix[20] = data[0,20] / data[0,1]         # NIC8.9
        NICmatrix[21] = data[0,21] / data[0,1]         # NIC8.10
        NICmatrix[22] = data[0,22] / data[0,1]         # NIC2.7.9
        NICmatrix[23] = data[0,23] / data[0,1]         # NIC2.7.10
        NICmatrix[24] = data[0,24] / data[0,1]         # NIC2.8.9
        NICmatrix[25] = data[0,25] / data[0,1]         # NIC2.8.10
        NICmatrix[26] = data[0,26] / data[0,1]         # NIC34.7.9
        NICmatrix[27] = data[0,27] / data[0,1]         # NIC34.7.10
        NICmatrix[28] = data[0,28] / data[0,1]         # NIC34.8.9
        NICmatrix[29] = data[0,29] / data[0,1]         # NIC34.8.10
    if data[0,2] != 0:
        NICmatrix[30] = (data[0,3]+data[0,4]) / data[0,2]         # NIC2-34
        NICmatrix[31] = data[0,10] / data[0,2]         # NIC2-7
        NICmatrix[32] = data[0,11] / data[0,2]         # NIC2-8
        NICmatrix[33] = data[0,12] / data[0,2]         # NIC2-9
        NICmatrix[34] = data[0,13] / data[0,2]         # NIC2-10
    if data[0,3]+data[0,4] != 0:
        NICmatrix[35] = data[0,14] / (data[0,3]+data[0,4])         # NIC34-7
        NICmatrix[36] = data[0,15] / (data[0,3]+data[0,4])         # NIC34-8
        NICmatrix[37] = data[0,16] / (data[0,3]+data[0,4])         # NIC34-9
        NICmatrix[38] = data[0,17] / (data[0,3]+data[0,4])         # NIC34-10
    if data[0,6] != 0:
        NICmatrix[39] = data[0,10] / data[0,6]         # NIC7-2
        NICmatrix[40] = data[0,14] / data[0,6]         # NIC7-34
        NICmatrix[41] = data[0,7] / data[0,6]          # NIC7-8
        NICmatrix[42] = data[0,18] / data[0,6]         # NIC7-9
        NICmatrix[43] = data[0,19] / data[0,6]         # NIC7-10
    if data[0,7] != 0:
        NICmatrix[44] = data[0,11] / data[0,7]         # NIC8-2
        NICmatrix[45] = data[0,15] / data[0,7]         # NIC8-34
        NICmatrix[46] = data[0,20] / data[0,7]         # NIC8-9
        NICmatrix[47] = data[0,21] / data[0,7]         # NIC8-10
    if data[0,8] != 0:
        NICmatrix[48] = data[0,12] / data[0,8]         # NIC9-2
        NICmatrix[49] = data[0,16] / data[0,8]         # NIC9-34
        NICmatrix[50] = data[0,18] / data[0,8]         # NIC9-7
        NICmatrix[51] = data[0,20] / data[0,8]         # NIC9-8
    if data[0,9] != 0:
        NICmatrix[52] = data[0,13] / data[0,9]         # NIC10-2
        NICmatrix[53] = data[0,17] / data[0,9]         # NIC10-34
        NICmatrix[54] = data[0,19] / data[0,9]         # NIC10-7
        NICmatrix[55] = data[0,21] / data[0,9]         # NIC10-8
    if data[0,10] != 0:
        NICmatrix[56] = data[0,14] / data[0,10]        # NIC2.7-34
        NICmatrix[57] = data[0,11] / data[0,10]        # NIC2.7-8
        NICmatrix[58] = data[0,22] / data[0,10]        # NIC2.7-9
        NICmatrix[59] = data[0,23] / data[0,10]        # NIC2.7-10
    if data[0,11] != 0:
        NICmatrix[60] = data[0,15] / data[0,11]        # NIC2.8-34
        NICmatrix[61] = data[0,24] / data[0,11]        # NIC2.8-9
        NICmatrix[62] = data[0,25] / data[0,11]        # NIC2.8-10
    if data[0,12] != 0:
        NICmatrix[63] = data[0,16] / data[0,12]        # NIC2.9-34
        NICmatrix[64] = data[0,22] / data[0,12]        # NIC2.9-7
        NICmatrix[65] = data[0,24] / data[0,12]        # NIC2.9-8
    if data[0,13] != 0:
        NICmatrix[66] = data[0,17] / data[0,13]        # NIC2.10-34
        NICmatrix[67] = data[0,23] / data[0,13]        # NIC2.10-7
        NICmatrix[68] = data[0,25] / data[0,13]        # NIC2.7-34
    if data[0,14] != 0:
        NICmatrix[69] = data[0,15] / data[0,14]        # NIC34.7-8
        NICmatrix[70] = data[0,26] / data[0,14]        # NIC34.7-9
        NICmatrix[71] = data[0,27] / data[0,14]        # NIC34.7-10
    if data[0,15] != 0:
        NICmatrix[72] = data[0,28] / data[0,15]        # NIC34.8-9
        NICmatrix[73] = data[0,29] / data[0,15]        # NIC34.8-10
    if data[0,16] != 0:
        NICmatrix[74] = data[0,26] / data[0,16]        # NIC34.9-7
        NICmatrix[75] = data[0,28] / data[0,16]        # NIC34.9-8
    if data[0,17] != 0:
        NICmatrix[76] = data[0,27] / data[0,17]        # NIC34.10-7
        NICmatrix[77] = data[0,29] / data[0,17]        # NIC34.10-8
    if data[0,18] != 0:
        NICmatrix[78] = data[0,22] / data[0,18]        # NIC7.9-2
        NICmatrix[79] = data[0,26] / data[0,18]        # NIC7.9-34
        NICmatrix[80] = data[0,20] / data[0,18]        # NIC7.9-8
    if data[0,19] != 0:
        NICmatrix[81] = data[0,23] / data[0,19]        # NIC7.10-2
        NICmatrix[82] = data[0,27] / data[0,19]        # NIC7.10-34
        NICmatrix[83] = data[0,21] / data[0,19]        # NIC7.10-8
    if data[0,20] != 0:
        NICmatrix[84] = data[0,24] / data[0,20]        # NIC8.9-2
        NICmatrix[85] = data[0,28] / data[0,20]        # NIC8.9-34
    if data[0,21] != 0:
        NICmatrix[86] = data[0,25] / data[0,21]        # NIC8.10-2
        NICmatrix[87] = data[0,29] / data[0,21]        # NIC8.10-34
    if data[0,22] != 0:
        NICmatrix[88] = data[0,26] / data[0,22]        # NIC2.7.9-34
        NICmatrix[89] = data[0,24] / data[0,22]        # NIC2.7.9-8
    if data[0,23] != 0:
        NICmatrix[90] = data[0,27] / data[0,23]        # NIC2.7.10-34
        NICmatrix[91] = data[0,25] / data[0,23]        # NIC2.7.10-8
    if data[0,24] != 0:
        NICmatrix[92] = data[0,28] / data[0,24]        # NIC2.8.9-34
    if data[0,25] != 0:
        NICmatrix[93] = data[0,29] / data[0,25]        # NIC2.8.10-34
    if data[0,26] != 0:
        NICmatrix[94] = data[0,28] / data[0,26]        # NIC34.7.9-8
    if data[0,27] != 0:
        NICmatrix[95] = data[0,29] / data[0,27]        # NIC34.7.10-8
        
    
    # Writing on disk.
    res_name = '/'.join(path.split('/')[:-1]) + "/NICmatrix/" + path.split('/')[-1]
    with open(res_name, "w", newline='', encoding='latin1') as file :
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Add row for each variable.
        writer.writerow(NICmatrix)
        
        file.close()    
   
#%% Main.

# Parallelizable function. One processor for each stratified variable.
def computeNICs(var, res_path) :
    """
    Calls computeNIC function for given stratified variable.
    
    Parameters :
        var : string. Id of stratified variable.
        res_path : string. Path of folder containing ROP-Results.
        
    Returns :
        no return.
    """   
    
    path = res_path + "a" + str(var) + "/"
    list_files = os.listdir(path)
    # Going through all .csv files written by countResults.py.
    for file in list_files :
        if file.endswith(".csv") :
            file = path + file
            computeNIC(file)
