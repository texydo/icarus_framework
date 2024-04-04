#!/bin/bash
#SBATCH --job-name=threads_main
#SBATCH --cpus-per-task=256
#SBATCH --mem=150G
#SBATCH --output=/sise/home/roeeidan/icarus_framework/main_logs/job_main_output-%j.txt

python_script_directory="/home/roeeidan/icarus_framework"

# Change directory to the specified directory
cd "$python_script_directory" || exit
/home/roeeidan/.conda/envs/icarus/bin/python /home/roeeidan/icarus_framework/main.py