#!/bin/bash
#SBATCH --job-name=analysis_prep_zone_grid_data
#SBATCH --cpus-per-task=5
#SBATCH --mem=30G
#SBATCH --output=/sise/home/roeeidan/icarus_framework/main_logs/job_analysis_prep_zone_grid_data-%j.txt

python_script_directory="/home/roeeidan/icarus_framework/analytics"

# Change directory to the specified directory
cd "$python_script_directory" || exit
/home/roeeidan/.conda/envs/icarus/bin/python /home/roeeidan/icarus_framework/analytics/prep_grid_zone_data.py