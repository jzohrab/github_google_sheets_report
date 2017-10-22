#!/bin/bash

# Creates venv.  After running, do "source venv/bin/activate" to start the venv.

PYTHON='/usr/local/bin/python3'  # default Python

if [ "$#" == 1 ]; then
    PYTHON="$1"
fi

rm -rf venv

# Create virtual env with specific python
virtualenv -p "$PYTHON" venv
