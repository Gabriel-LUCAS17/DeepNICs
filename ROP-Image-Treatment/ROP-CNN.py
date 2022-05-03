# -*- coding: utf-8 -*-
"""
Program: ROP-CNN.py
Description: process ROP-Images using CNNs.
Author: Mathieu Brunner.
"""

#%% Modules importation.

# Define working directory.
import os
import sys
os.chdir(sys.path[0])

# Scientific computing modules.
import numpy as np
import pandas as pd
import tensorflow as tf

# Plotting modules.
import matplotlib.pyplot as plt
import seaborn as sns

# Utils.
import glob
from keras.utils.np_utils import to_categorical

#%% Setting parameters.

# Setting seed.
from numpy.random import seed
seed(1)

# Plotting parameters.
plt.rcParams["figure.figsize"] = (30,15)

# Tensorflow backend parameters.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Disables the warning, doesn't take advantage of AVX to run faster.
tf.keras.backend.set_floatx('float64')

# GPU device ?
device_name = tf.test.gpu_device_name()
if not device_name:
    print('GPU device not found')
else :
    print('Found GPU at: {}'.format(device_name))

#%% Utilities.

from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(y_true, y_pred, classes, normalize=False, title=None, cmap=plt.cm.Blues):

    if not title:
        if normalize: title = 'Normalized confusion matrix'
        else: title = 'Confusion matrix, without normalization'

    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(cm.shape[1]), yticks=np.arange(cm.shape[0]),
           xticklabels=classes, yticklabels=classes, title=title,
           ylabel='True label', xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt), ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.rcParams["figure.figsize"] = (25,13)
    plt.show()

    return ax

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

#%% Import data.

if __name__ == '__main__':

    def Usage() :
        """
        Prints the Usage of ROP-CNN.py.

        Parameters :
            no parameters.

        Return :
            no return.
        """
        print("\nUsage of ROP-CNN.py : ")
        print("\tThis script must be executed from the Anaconda Prompt.")
        print("\tSeveral command-line arguments must be specified.\n")
        print("Usage : 'python ROP-CNN.py arg1 arg2 arg3 arg4'")
        print("where :")
        print("\t\t arg1 is the minimum range of simulation range (integer)")
        print("\t\t arg2 is the maximum range of simulation range (integer)")
        print("\t\t arg3 is the minimum number of selected variables (integer)")
        print("\t\t arg4 is the maximum number of selected variables (integer)")
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
            ncols  = supR - infR + 1
            nrows = supV - infV + 1
            num_channel = 1
    else :
        print("\nWrong number of arguments. 4 arguments expected.")
        Usage()

    # Import images.
    N = int(input("Enter number of variables: "))
    path = str(input("Enter path of Results-folder: "))
    NUM_EPOCHS = int(input("Enter number of epochs: "))
    list_var = getListVariables(path)
    data = []
    for var in list_var :
        img_path = path + "a" + str(var) + "/Images/NIC1/" + str(var) + ".csv"
        data += [pd.read_csv(img_path, sep=";", header=None, dtype=np.float32).to_numpy()]
    data = np.array(data)
    data = data.reshape(data.shape[0], nrows, ncols, num_channel)

    # Import labels.

    labels_path = path + "KMeansClustering.csv"
    labels = pd.read_csv(labels_path, sep=";", header=None, dtype=np.int32).to_numpy()[:,1]

    print("Size of data : ", data.shape)
    print("Size of labels list : ", labels.shape)

    # Train-test split.
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size = 0.20, random_state=42)

    print("X_train shape : ", X_train.shape)
    print("X_test shape : ", X_test.shape)
    print("Y_train shape : ", y_train.shape)
    print("Y_test shape : ", y_test.shape)

    # Transformation into categorical.
    Y_train = to_categorical(y_train)
    Y_test = to_categorical(y_test)

    # Architecture definition.
    def create_CNN(nb_filters = 10, N = 64, M = 32, dropout_rate = 0.5, batch = True) :
        global nrows, ncols, num_channel
        inputs = tf.keras.Input(shape=(nrows,ncols,num_channel))
        x = tf.keras.layers.Conv2D(filters=nb_filters, kernel_size=(3,3))(inputs)
        if batch : x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.layers.Dense(N, activation='relu')(x)
        x = tf.keras.layers.Dense(M, activation='relu')(x)
        outputs = tf.keras.layers.Dense(2, activation='softmax')(x)
        model = tf.keras.models.Model(inputs=inputs, outputs=outputs)
        opt = tf.keras.optimizers.Adam()
        model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    model = create_CNN()
    history = model.fit(X_train, Y_train, epochs=NUM_EPOCHS, validation_split=0.2, verbose=1)

    plt.title('Loss')
    plt.xlabel('Number epochs')
    plt.plot(history.history['loss'], color='r', label='training loss')
    plt.plot(history.history['val_loss'], color='b', label='validation loss')
    plt.legend(loc='upper right')
    plt.grid()
    plt.show() ;

    y_pred = model.predict(X_test)
    prediction = [np.argmax(y_pred[i]) for i in range(y_pred.shape[0])] # Règle de la majorité.
    classes = ['0', '1']
    plot_confusion_matrix(y_test, prediction, classes)
