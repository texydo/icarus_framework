#!/bin/bash
#SBATCH --job-name=threads_main
#SBATCH --cpus-per-task=164
#SBATCH --mem=150G
#SBATCH --output=/sise/home/roeeidan/icarus_framework/main_logs/job_main_output-%j.txt

/home/roeeidan/.conda/envs/icarus/bin/python /home/roeeidan/icarus_framework/main.py 0 164  /home/roeeidan/icarus_framework/outputs