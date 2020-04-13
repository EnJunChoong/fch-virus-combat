#!/bin/bash

conda activate covid

python run_crawler_sebenarnya.py & python run_processing_sebenarnya.py

python run_crawler_harianmetro.py & python run_processing_harianmetro.py

python run_crawler_thestar.py & python run_processing_thestar.py

python run_crawler_beritaharian.py & python run_processing_beritaharian.py