# DeepNICs.

## Project description.

The use of Random Forest of Perfect Trees (RFPT) and Nguyen’s Information Criterions (NICs) allow the association of any variable with a 2D or 3D-image which can be processed using Deep Learning computer vision methods. The patterns identified in such images can allow the inference of which variables contain the most predictive information about a classification target (e.g. respondant or not to a treatment).

## Project organisation.

The project is organized in the following way:

* Dashboard: Python web application to visualize results.
* ROP-Training: Automatization and optimization of the use of the rop executable.
* ROP-Image-Generation: Generation of ROP-Images from trained samples.
* ROP-Image-Clustering: Generation of labels for generated ROP-Images.
* ROP-Image-Treatment: Implementation of CNNs to process labeled ROP-Images.

## Python.

It is recommended to create a virtual environment for executing the Python scripts. You can create a conda virtual environment by following these instructions (assuming Anaconda is properly installed):

* Open Anaconda Prompt.
* Change the working directory to the folder containing this README.md.
* Enter the following commands:

```
conda create -n DeepNICs python=3.8
conda activate DeepNICs
python -m pip install -r requirements.txt
```

This will create a virtual environment inside which all needed Python packages will be installed.

Once the virtual environment has been created, you can activate it or deactivate when you need:

```
conda activate DeepNICs
conda deactivate
```
