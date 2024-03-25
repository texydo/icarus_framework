#!/bin/bash
#SBATCH --job-name=main_run
#SBATCH --cpus-per-task=128
#SBATCH --mem=64G
#SBATCH --output=/sise/home/roeeidan/icarus_framework/main_logs/job_main_output-%j.txt

/home/roeeidan/.conda/envs/icarus/bin/python /home/roeeidan/icarus_framework/main.py