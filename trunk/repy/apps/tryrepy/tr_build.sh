#! /bin/bash

echo "Building Try Repy..."
echo "Removing build directory..."
rm -r build
echo "Creating new build directory..."
mkdir build
echo "Calling python script to flat out web directory..."
python tr_convertfiles.py
echo "Copying needed py and repy file to build directory..."
cp tr_webcontroller.repy build
cp restrictions.tryrepy build
cp tr_sandbox.repy build
cp tr_fileabstraction.repy build
echo "Finished building! You can now run tr_run.sh </abspath/to/seattle_repy> <serverport>"