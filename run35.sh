#!/bin/bash

sudo kill -9 $(sudo lsof -t -i:8081) &> /dev/null
python3.5 -m pip install -r requirements
python3.5 bootstrap.py
