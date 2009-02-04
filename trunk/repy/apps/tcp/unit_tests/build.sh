#!/bin/bash

# Uses repypp to build tests.
# Puts tests in $TESTDIR.

REPYPP=repypp.py
TESTDIR=test

cp ../*.repy .
echo "Building tests..."
files=`ls [zne]_test*.py`
for f in ${files}
do
  echo ${f}
  python ../${TESTDIR}/${REPYPP} ${f} ../${TESTDIR}/${f}
done
echo "Done"

exit

