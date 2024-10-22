#!/bin/zsh
# This script cleans everything 

# remove all previous build directories

echo "Deleting previous build directories, if present"
rm -rf build dist *.egg-info > /dev/null 2>&1

# remove cython files
echo "Deleting cython files, if present"
rm metapredict/backend/cython/*so > /dev/null 2>&1
rm metapredict/backend/cython/*c > /dev/null 2>&1

echo "Building the package"
python -m build
python setup.py build_ext --inplace
