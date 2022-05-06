# -*- coding: utf-8 -*-
"""
Program: ROP-Image-Generation.py
Description: generation of ROP-Images from ROP-Training samples.
Author: Mathieu Brunner.
"""

#%% Define working directory.
import os
import sys
os.chdir(sys.path[0])

#%% Import modules and functions.
import glob
from multiprocessing import Pool
import subprocess
from src.countResults import countVarResults
from src.computeNIC import computeNICs
from src.assembleImages import assembleImages
from src.saveImages import saveImages, saveImagesByCluster, saveFuseImages
from src.transformImages import transformImages
from src.fuseImages import fuseImages
import time

# Import imageClustering.py.
sys.path.append('../ROP-Image-Clustering/')
from imageClustering import Clustering

#%% Apply clustering on :

APPLY_CLUSTERING_ON = "Fuse"
# Other alternatives are : APPLY_CLUSTERING_ON = "NICx" where x between 1 and 10.

#%% Check number of arguments.

if __name__ == '__main__':

    def Usage() :
        """
        Prints the Usage of ROP-Image-Generation.py.

        Parameters :
            no parameters.

        Return :
            no return.
        """
        print("\nUsage of ROP-Image-Generation.py : ")
        print("\tThis script must be executed from the Anaconda Prompt.")
        print("\tSeveral command-line arguments must be specified.\n")
        print("Usage : 'python ROP-Image-Generation.py arg1 arg2 arg3 arg4'")
        print("where :")
        print("\t\t arg1 is the minimum range of simulation range (integer)")
        print("\t\t arg2 is the maximum range of simulation range (integer)")
        print("\t\t arg3 is the minimum number of selected variables (integer)")
        print("\t\t arg4 is the maximum number of selected variables (integer)")
        exit()

    def Execute_Command(command) :
        """
        Execute specified command using subprocess function.

        Parameters :
            command : string or list of strings. Command to execute.

        Returns :
            no return.
        """

        program = subprocess.run(command)
        if program.returncode == 0 :
            print("Program correctly executed.")
        else :
            print("Failure to execute this program.")
            print("Command was : ", command)
            print(repr(program.stdout))
            print(repr(program.stderr))
            exit()

    def check_int(x) :
        """
        Returns True if the specified argument is an integer, False otherwise.

        Parameters :
            x : string.

        Returns :
            is_integer : bool.
        """
        try :
            int(x)
            return True
        except :
            return False

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

    # Checking number of arguments and arguments' consistency.
    if len(sys.argv) == 5 :
        print("\nList of entered arguments : ", sys.argv[1:])
        print("Checking arguments' consistency.")
        # Are the entered args recognized as integers ?
        for val in sys.argv[1:] :
            if not check_int(val) :
                print("ERROR: the argument ", val, " is not an integer.")
                Usage()
        # Have we : infR < supR and infV < supV ?
        if int(sys.argv[1]) > int(sys.argv[2]) or int(sys.argv[3]) > int(sys.argv[4]) :
            print("ERROR: Entered values are not consistent.")
            Usage()
        else :
            print("Entered arguments are consistent.")
            infR = int(sys.argv[1])
            supR = int(sys.argv[2])
            infV = int(sys.argv[3])
            supV = int(sys.argv[4])
            width  = supR - infR + 1
            height = supV - infV + 1
    else :
        print("\nWrong number of arguments. 4 arguments expected.")
        Usage()

    # Get constants' definition from command-line.
    data_path = str(input("Enter path to folder containing all ROP-Training samples: "))
    results_path = str(input("Enter path to folder containing all ROP-Results: "))
    AP_THRESHOLD = float(input("Enter AP_Threshold: "))
    N_proc = os.cpu_count()
    print("Number of processors to use set to : ", N_proc)

    list_var = getListVariables(data_path)
    print(data_path)
    print(list_var)

    save_path = results_path + "ImagesPNG/"
    save_fuse_path = results_path + "ImagesFusePNG/"
    cluster_path = results_path + "KMeansClustering.csv"

    # Command to delete ROP-Results folder.
    # Check if ROP-Results folder exists.
    if os.path.isdir(results_path) :
        print("Deleting ROP-Results folder.")
        command = [r"utils/Clear-Results.bat ", results_path.replace("/","\\")]
        print("Previous ROP-Results deleted.")
        Execute_Command(command)

    # Generation of ROP-Results filesystem.
    command = [r"utils/Results-FileSystem.bat ", data_path.replace("/","\\"), results_path.replace("/","\\")]
    print("Generation of ROP-Results filesystem.")
    Execute_Command(command)

    # Prepare list of arguments.
    List_Args_Count_Res = [(var, infR, supR, infV, supV, data_path, results_path, AP_THRESHOLD) for var in list_var]
    List_Args_Compute_NIC = [(var, results_path) for var in list_var]
    List_Args_Assemble_Images = [(var, width, height, results_path) for var in list_var]
    List_Args_Save_Images = [(var, results_path, save_path) for var in list_var]
    List_Args_Save_Images_By_Cluster = [(var, results_path, cluster_path) for var in list_var]
    List_Args_Transform_Images = [(var, results_path) for var in list_var]
    List_Args_Fuse_Images = [(var, width, height, results_path) for var in list_var]
    List_Args_Save_Fuse_Images = [(var, results_path, save_fuse_path, width, height) for var in list_var]

    t0 = time.time()
    # Parallel execution.
    with Pool(N_proc) as p:
        print("Counting results.")
        p.starmap(countVarResults, List_Args_Count_Res)
        t1 = time.time()
        print("Computing NICs.")
        p.starmap(computeNICs, List_Args_Compute_NIC)
        t2 = time.time()
        print("Assembling ROP-Images.")
        p.starmap(assembleImages, List_Args_Assemble_Images)
        t3 = time.time()
        print("Transforming ROP-Images.")
        p.starmap(transformImages, List_Args_Transform_Images)
        t4 = time.time()
        print("Fusing NIC-ROP-Images.")
        p.starmap(fuseImages, List_Args_Fuse_Images)
        t5 = time.time()

    # Creating .txt file containing path for each image.
    filename= results_path + "listNames.txt"
    print("Creating listNames.txt at : ", filename)
    with open(filename, "w", newline='', encoding='latin1') as file :
        for var in list_var :
            imgPath = results_path + "a" + str(var) + "/Images/" + APPLY_CLUSTERING_ON + "/" + str(var) + ".csv"
            file.write(imgPath)
            file.write('\n')

    # Clustering.
    #print("Launching Clustering Algorithm on generated ROP-Images.")
    #Clustering(results_path, cluster_path)

    # Parallel execution.
    with Pool(N_proc) as p:
        print("Saving generated ROP-Images.")
        p.starmap(saveImages, List_Args_Save_Images)
        #p.starmap(saveImagesByCluster, List_Args_Save_Images_By_Cluster)
        print("Saving Fuse-Images.")
        p.starmap(saveFuseImages, List_Args_Save_Fuse_Images)
    t6 = time.time()
    print("Counting time :","{:.2f}".format(t1-t0),'s')
    print("Computing time :","{:.2f}".format(t2-t1),'s')
    print("Assembling time :","{:.2f}".format(t3-t2),'s')
    print("Transforming time :","{:.2f}".format(t4-t3),'s')
    print("Fusing time :","{:.2f}".format(t5-t4),'s')
    print("Saving time :","{:.2f}".format(t6-t5),'s')
    print("Total time :","{:.2f}".format(t6-t0),'s')