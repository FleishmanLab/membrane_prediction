TopGraph README
===============

Introduction
------------
TopGraph is a membrane topology predictor based on biophysical measurements of membrane insertion energies.

Installing
----------
download the code and run... (you're more than welcome to fork this repo)
all code is in python2.7, required libraries are:
* matplotlib
* networkx
* biopython
* threading
* argparse
* numpy
* scipy
* a few more, if you run specific analysis scripts

Running
-------
easiest way to run this code, is on our [web-server](http://topgraph.weizmann.ac.il)
if you wish to run locally, download the code form this repo. a sample command is:
    python2.7 TMpredict_WinGrade.py -mode user -run_type plain -name NAME -seq SEQ -create_html True -ss2 PATH_TO_SS2 


Citing
------
Elazar, Assaf, Jonathan Weinstein, Ido Biran, Yearit Fridman, Eitan Bibi, and Sarel Jacob Fleishman. 2016. “Mutational Scanning Reveals the Determinants of Protein Insertion and Association Energetics in the Plasma Membrane.” Edited by Yibing Shan. eLife. doi:10.7554/eLife.12125.