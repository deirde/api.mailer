#!/bin/bash

sudo kill -9 $(sudo lsof -t -i:8081) &> /dev/null
pip3 install -r requirements
python3.3 bootstrap.py