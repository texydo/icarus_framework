#!/bin/bash
#SBATCH --job-name=analysis_line_user_ditribution
#SBATCH --cpus-per-task=5
#SBATCH --mem=60G
#SBATCH --output=/sise/home/roeeidan/icarus_framework/main_logs/job_analysis_line_user_ditribution-%j.txt

python_script_directory="/home/roeeidan/icarus_framework/analytics"

# Change directory to the specified directory
cd "$python_script_directory" || exit
/home/roeeidan/.conda/envs/icarus/bin/python /home/roeeidan/icarus_framework/analytics/plots/line_user_precentage_distribution.py