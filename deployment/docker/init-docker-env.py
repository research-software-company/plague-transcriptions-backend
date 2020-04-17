#!/usr/bin/python3

# This file performs migrations and initial data ingestion on the docker backend environment.
# It expects the configuration to be as specified in docker-compose.yml in this folder

# Run it from the current directory. Don't forget to activate the proper virtual environment

import os

os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:postgres@localhost:25432/plague-transcription'

curdir = os.curdir

try:
    os.chdir('../..')
    os.system('flask db upgrade')
    os.system('flask ingest data-files/manuscripts.xlsx')
    os.system('flask ingest data-files/manuscripts.xlsx --sheet 3')
finally:
    os.chdir(curdir)