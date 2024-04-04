import sys
import os
import subprocess
import json
import shutil
import time
import re

def create_job_script(job_index, cpus_per_job, config_file_path):
    current_directory = os.getcwd()
    parent_path = os.path.abspath(os.path.join(current_directory, os.pardir))
    python_script_path = os.path.join(parent_path, "main.py")
    enviorment_path = find_conda_env_path("icarus")
    log_data_path = os.path.join(parent_path, "main_logs")
    # Replace "X" in the template with the current job_index
    job_script_name = os.path.join(current_directory, f"job_script_{job_index}.sh")
    with open(job_script_name, 'w') as script_file:
        script_file.write("#!/bin/bash\n")
        script_file.write(f"#SBATCH --job-name=threads_main_{job_index}\n")
        script_file.write(f"#SBATCH --cpus-per-task={cpus_per_job}\n")
        script_file.write(f"#SBATCH --output={os.path.join(log_data_path, f'%j_job_main_output_{job_index}.txt')}\n")
        script_file.write(f"#SBATCH --mem=150G\n")
        script_file.write(f"python_script_directory=\"{parent_path}\"\n")
        script_file.write(f"cd \"$python_script_directory\" || exit\n")
        script_file.write(f"{enviorment_path} {python_script_path} {config_file_path}\n")
    return job_script_name


def submit_jobs(job_scripts):
    job_ids = []
    for script in job_scripts:
        result = subprocess.run(['sbatch', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        job_id = result.stdout.strip().split()[-1]
        job_ids.append(job_id)
    print("Submitted jobs with IDs:", job_ids, flush=True)

def cleanup(job_scripts):
    for script in job_scripts:
        os.remove(script)
    # print("Cleaned up job script files.")

def config_file_update(job_index, cpus_per_job):
    output_directory = "temp_configs"
    new_file_name = f"config_{job_index}.json"
    current_directory = os.getcwd()
    
    parent_path = os.path.abspath(os.path.join(current_directory, os.pardir))
    original_file_path = os.path.join(parent_path, "configurations/config.json")
    output_directory = os.path.join(current_directory, "temp_configs")
    
    output_file_path = os.path.join(output_directory, new_file_name)
    shutil.copy(original_file_path, output_file_path)
    with open(output_file_path, 'r') as file:
        config_data = json.load(file)

    # Update the core_number field
    config_data["core_number"] = cpus_per_job

    # Write the modified data back to the file
    with open(output_file_path, 'w') as file:
        json.dump(config_data, file, indent=4)
    return output_file_path

def delete_files_in_temp_configs():
    # Get the current working directory
    current_directory = os.getcwd()

    # Directory where the files are located
    temp_configs_directory = os.path.join(current_directory, "temp_configs")

    # Check if the directory exists
    if os.path.exists(temp_configs_directory):
        # Get the list of files in the directory
        files_in_directory = os.listdir(temp_configs_directory)
        
        # Iterate over the files and delete them
        for file_name in files_in_directory:
            file_path = os.path.join(temp_configs_directory, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
def create_jobs(available_cpus):
    delete_files_in_temp_configs()
    job_scripts = []
    for job_index, cpus_per_job in enumerate(available_cpus):
        if cpus_per_job > 64:
            config_file_path = config_file_update(job_index, cpus_per_job)
            job_script_name = create_job_script(job_index, cpus_per_job, config_file_path)
            job_scripts.append(job_script_name)
    submit_jobs(job_scripts)
    cleanup(job_scripts)
    delete_files_in_temp_configs()

def find_conda_env_path(env_name):
    # Execute the "conda env list" command
    result = subprocess.run(['conda', 'env', 'list'], stdout=subprocess.PIPE, text=True)
    # Process the output line by line
    for line in result.stdout.splitlines():
        if env_name in line:
            # Extract the path which is typically the second column
            env_path = line.split()[1]
            return os.path.join(env_path, "bin", "python") 
    return None

if __name__ == "__main__":
    available_cpus = [int(cpu) for cpu in sys.argv[1:]]
    available_cpus = sorted(available_cpus, reverse=True)
    create_jobs(available_cpus)
    time.sleep(2)
    # output = subprocess.check_output(['squeue -u roeeidan'], text=True)
    # print(output)
