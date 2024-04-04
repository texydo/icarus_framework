#!/bin/bash

# Initialize an empty string to collect available CPUs
available_cpus=""

# Run the 'sres' command and capture its output
sres_output=$(sres)

# Use process substitution to avoid creating a subshell
while IFS= read -r line; do
    # Process each line that contains node information
    cpu_count=$(echo "$line" | awk '/dt-cpu|ise-cpu/ {
        free_cpus = $(NF-2) # Extract the free CPUs
        printf "%s", free_cpus
    }')
    # Append each count of free CPUs to the variable, separated by space
    available_cpus="${available_cpus} ${cpu_count}"
done < <(echo "$sres_output" | awk '/NODE               GPUs          MEM            CPUs/,0')

echo "Available CPUs: $available_cpus"
# Now run the Python script, passing the available CPUs as arguments
python3 run_max_threads.py $available_cpus

# Run the squeue command and capture its output
squeue_output=$(squeue -u $(whoami))


job_ids_to_cancel=($(echo "$squeue_output" | awk '/MaxCpuPerAccount/{print $1}'))

for job_id in "${job_ids_to_cancel[@]}"
do
    scancel "$job_id"
    # echo "Cancelled job $job_id"
done

env_path=$(conda env list | grep 'icarus' | awk '{print $2}')
