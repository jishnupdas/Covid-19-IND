#!/bin/bash

# activating venv
conda activate base

source data_update.sh

# Running python script
python3 cov_vis.py

# staging changes, adding commiting and pushing to remote
git add data/* report.pdf && git commit -m "update" && git push

