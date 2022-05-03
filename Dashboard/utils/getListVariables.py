# -*- coding: utf-8 -*-
"""
Program: getListVariables.py
Description: get list of variables from path of folder containing the ROP-Training
    samples.
Author: Mathieu Brunner.
"""

#%% Import modules.
import glob

#%% Utils.

def getListVariables(path) :
    """
    Returns list of variables contained in the specified folder.

    Parameters :
        path : string. Path for folder containing data for several stratified
            variable.

    Returns :
        list_var : list of int. List of variables' id contained in the
            specified folder.
    """

    list_var = []
    pattern = path + "a*"
    list_folders = glob.glob(pattern)
    for folder in list_folders :
        list_var += [int(folder.split("\\")[-1][1:])]
    list_var.sort()
    return list_var