#!/bin/bash
cd ~/Documents/Educacao/UTFPR\ -\ RANDOM/IC/OpenBCI_Python_Framework
sphinx-apidoc -o docs .
cd ./docs
make html
