#!/bin/bash
#SBATCH --job-name=job_main_run
#SBATCH --cpus-per-task=128
#SBATCH --mem=64G
#SBATCH --output=/sise/home/roeeidan/icarus_framework/main_logs/job_main_output-%j.txt

cleanup() {
    echo "Performing cleanup tasks..."
    # Call the cancel_monitor_jobs.py script with the same environment
    /sise/home/roeeidan/.conda/envs/icarus/bin/python /sise/home/roeeidan/icarus_framework/multi_job_managment/cancel_monitor_jobs.py
    echo "Cleanup complete."
}

# Trap signals to call the cleanup function before exiting
trap 'cleanup' EXIT


/home/roeeidan/.conda/envs/icarus/bin/python /home/roeeidan/icarus_framework/main.py /home/roeeidan/icarus_framework/configurations/config_jobs_with_socket.json