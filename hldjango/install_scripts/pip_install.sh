#!/usr/bin/env sh

# update pip packages
pip install --upgrade pip

# install all python modules/requirements (django, etc.)
# ATTN: JR if using poetry, update the requirements.txt with: poetry export -f requirements.txt --output requirements.txt
pip install -r requirements.txt
