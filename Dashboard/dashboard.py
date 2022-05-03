# -*- coding: utf-8 -*-
"""
Program: dashboard.py
Description: dashboard to visualize ROP-Results.
Author: Mathieu Brunner.
"""

#%% Define working directory.
import os
import sys
os.chdir(sys.path[0])

#%% Import modules and functions.
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px

from multiprocessing import Pool
import numpy as np
import pandas as pd

from utils.countTrainingSamples import computeTrainingSamples
from utils.getListVariables import getListVariables

#%% App build.

# Define app.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
optionStyle = {'margin-left': '10px', 'margin-bottom' : '10px'}

# Define input list.
input_list=[]
input_list.append(Input(component_id="transformation", component_property='value'))
input_list.append(Input(component_id="stratVariable", component_property='value'))
input_list.append(Input(component_id="NIC", component_property='value'))
input_list.append(Input(component_id="clustering", component_property='value'))

# Define app layout.
app.layout = html.Div([


    dbc.Row([ dbc.Col(html.H1("ROP-results Analysis", style={'textAlign':'center'}), width=9) ]),
    dbc.Row([ dbc.Col(html.H2("Options"), width=9) ]),
    # Transformation used.
    dbc.Row([ dbc.Col(html.H5("Apply transformation ? "), width=3),
              dbc.Col(dcc.RadioItems( id="transformation", value='N',
                                      options=[{'label': 'No transformation', 'value': 'N'},
                                               {'label': 'Transformation applied', 'value': 'Y'}] ) , width=9) ],
            style=optionStyle),
    # Stratified variable choice.
    dbc.Row([ dbc.Col(html.H5("Stratified variable choice : "), width=3),
              dbc.Col(dcc.Input( id="stratVariable", placeholder='Enter stratified variable index...',
                                 type='text', value='1' ), width=9) ],
            style=optionStyle),
    # NIC choice.
    dbc.Row([ dbc.Col(html.H5("NIC choice : "), width=3),
              dbc.Col(dcc.Input( id="NIC", placeholder='Enter NIC index...',
                                type='text', value='1' ), width=9) ],
            style={'margin-left': '10px', 'margin-bottom' : '10px'}),
    # Clustering algorithm applied.
    dbc.Row([ dbc.Col(html.H5("Clustering algorithm applied : "), width=3),
             dbc.Col(dcc.Dropdown( id="clustering", value='KMeans',
                                   options=[ {'label': 'KMeans', 'value': 'KMeans'},
                                             {'label': 'Spectral', 'value': 'Spectral'}] ), width=4) ],
            style=optionStyle),
    # Printing class number.
    dbc.Row([ dbc.Col( dcc.Markdown(children=[], id="cluster"), width=4) ],
            style=optionStyle),
    ##### Graphs. #####
    # NIC-ROP-Image.
    dbc.Row([ dbc.Col(dcc.Graph(id='NIC-ROP-Image', figure={}, config={'displayModeBar':False}), width="auto") ], align="center"),
    # Rate of missing data.
    dbc.Row([ dbc.Col(dcc.Graph(id='MissingData', figure={}, config={'displayModeBar':False}), width="auto")], align="center"),
    # Fuse-ROP-Image data.
    dbc.Row([ dbc.Col(dcc.Graph(id='Fuse-ROP-Image', figure={}, config={'displayModeBar':False}), width="auto")], align="center")


])

def getClusterId(var, clusteringAlgorithm) :
    """
    Returns label of a ROP-Image.

    Parameters :
        var : string. Variable id.
        clusteringAlgorithm : string. Name of the clustering algorithm.

    Returns :
        label : integer. Label of the specified ROP-Image.
    """

    global RES_PATH

    # Dataset choice.

    path = RES_PATH
    if clusteringAlgorithm == "KMeans" : path += "KMeansClustering.csv"
    elif clusteringAlgorithm == "Spectral" : path += "SpectralClustering.csv"
    else :
        print("File doesn't exist : ", clusteringAlgorithm)
        return -1
    try :
        clustering_results = pd.read_csv(path, sep=";", header=None, dtype=np.int32)
        return clustering_results.iloc[int(var)-1][1]
    except :
        print("Issue with file : ", path)
        return -1

# App callbacks.
@app.callback(
    Output(component_id='cluster', component_property='children'),
    Output(component_id='NIC-ROP-Image', component_property='figure'),
    Output(component_id='MissingData', component_property='figure'),
    Output(component_id='Fuse-ROP-Image', component_property='figure'),
    input_list
)
def update_graph(transformChoice, var, NIC, clusteringAlgorithm) :
    """
    Update app's graphs. This function is called automatically when the app is launched.

    Parameters :
        transformChoice : string. Apply a transformation ?
        var : string. Variable id.
        NIC : string. NIC id.
        clusteringAlgorithm : string. Name of the clustering algorithm.

    Returns :
        no return.
    """

    global DATA_PATH, RES_PATH, PATH_COUNT

    # Print arguments value.
    print("Printing transformation choice : ", transformChoice)
    print("Printing variable choice : ",       var)
    print("Printing NIC choice : ",            NIC)
    print("Printing Clustering Algorithm : ",  clusteringAlgorithm)

    # Get image label.
    cluster_id = getClusterId(var, clusteringAlgorithm)
    cluster_id = str(cluster_id)
    print("Cluster id : ", cluster_id)

    # Setting default values for Input parameters.
    if var == "" or int(var) <= 0 or int(var) > 30 : var = 1
    if NIC == "" or int(NIC) <= 0 or int(NIC) > 10 : NIC = 1

    # Import data for graph plotting.


    # Defining ROP-Image path.
    imgPath = RES_PATH + "/a" + str(var) + "/Images/"
    if transformChoice == "Y" : imgPath = imgPath[:-1] + "Transform/"
    imgPath = imgPath + "NIC" + str(NIC) + "/" + str(var) + ".csv"
    # Defining Missing Data path.
    missingDataPath = PATH_COUNT + "a" + str(var) + ".csv"
    # Defining Fuse-ROP-Image-Path
    fusePath = RES_PATH + "/a" + str(var) + "/Images/Fuse/" + str(var) + ".csv"

    # Importing data.
    try :
        fuseImg        = pd.read_csv(fusePath, sep=";", header=None, dtype=np.float32)
        data           = pd.read_csv(imgPath, sep=";", header=None, dtype=np.float32)
        missingDataCsv = pd.read_csv(missingDataPath, sep=";", header=None, dtype=np.float32)
    except :
        print("One of the file was not found.")

    try :
        n,p = missingDataCsv.shape
        # Plot Missing Data graph.
        fig_Missing_Data = px.imshow(missingDataCsv, labels=dict(x="Range of range of simulation",
                                                                 y="Number of selected variables",
                                                                 color="Rate of trained data"),
                                      x=[str(i) for i in range(3,p+3)],
                                      y=[str(i) for i in range(n+2,2,-1)],
                                      zmin=0, zmax=1, color_continuous_scale='gray_r')
        fig_Missing_Data.update_layout( title={ 'text': f"Stratified variable {var} - Rate of trained data",
                                                'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
        n,p = data.shape
        # Plot NIC-ROP-Image graph.
        fig_ROP_Image = px.imshow(data, labels=dict(x="Range of range of simulation",
                                                    y="Number of selected variables",
                                                    color=f"NIC{NIC} value"),
                                  x=[str(i) for i in range(3,p+3)],
                                  y=[str(i) for i in range(n+2,2,-1)],
                                  zmin=0, zmax=1, color_continuous_scale='gray_r')
        fig_ROP_Image.update_layout( title={ 'text': f"Variable {var} -  NIC {NIC}",
                                             'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
        # Plot Fuse-ROP-Image graph.
        fig_Fuse_ROP_Image = px.imshow(fuseImg, labels=dict(color="NIC value"),
                                       zmin=0, zmax=1, color_continuous_scale='gray_r')
        fig_Fuse_ROP_Image.update_layout( title={ 'text': f"Fuse ROP Image. Variable {var}",
                                                  'y':0.95, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                                          xaxis={ 'showticklabels':False}, yaxis={ 'showticklabels':False})
    except :
        print("Variables not defined for the time being.")
        fig_Missing_Data, fig_ROP_Image, fig_Fuse_ROP_Image = None, None, None

    return cluster_id, fig_ROP_Image, fig_Missing_Data, fig_Fuse_ROP_Image



#%% App run.

# Run app.
if __name__ == '__main__' :
    # Define constants.
    DATA_PATH  = str(input("Enter name of ROP-Training Samples Folder : "))
    RES_PATH   = str(input("Enter name of Results Folder : "))
    PATH_COUNT = str(input("Enter name of Folder with Samples Count : "))
    N          = int(input("Enter number of variables: "))
    infR       = int(input("Enter minimum range of simulation range: "))
    supR       = int(input("Enter maximum range of simulation range: "))
    infV       = int(input("Enter minimum number of selected variables: "))
    supV       = int(input("Enter maximum number of selected variables: "))
    width      = supR - infR + 1
    height     = supV - infV + 1
    
    # Get list of variables.
    list_var = getListVariables(DATA_PATH)

    # Prepare list of args.
    args = [(var, DATA_PATH, PATH_COUNT, width, height) for var in list_var]
    
    # Define number of processors to use.
    N_proc = os.cpu_count()
    with Pool(N_proc) as p:
        print("Computing number of trained ROP samples.")
        p.starmap(computeTrainingSamples, args)
    print("Launching app.")
    app.run_server(debug=False)
