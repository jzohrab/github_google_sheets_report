#!/bin/bash

virtualenv venv --always-copy
source venv/bin/activate
pip install -r requirements.txt
python generate_report.py --config config.yml.klick-genome
