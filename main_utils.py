import os
import sys
import shutil
import random
import pickle
import tempfile
import string
import json
from multi_job_managment.job_manager import JobManager, JobManagerSocket

def clear_logs_in_directory(directory):
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        return  # If the directory is not valid, exit the function

    log_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.log')]
    import fcntl
    for log_file in log_files:
        with open(log_file, 'a+') as file:
            try:
                fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                file.truncate(0)  # Clear the file
                fcntl.flock(file.fileno(), fcntl.LOCK_UN)
            except BlockingIOError:
                print(f"File '{log_file}' is locked by another process.")

def prepare_jobs(core_number, num_jobs, with_socket):
    icarus_directory = os.getcwd()
    parent_path = icarus_directory
    env_path = sys.executable
    log_data_path = os.path.join(icarus_directory, "logs")
    monitor_file_template = os.path.join(icarus_directory, "icarus_simulator/temp_data/run_X.txt")
    num_jobs = num_jobs
    cpus_per_job = core_number
    mem = 120
    if with_socket:
        python_script_path = os.path.join(icarus_directory, "multi_job_managment/task_monitor_socket.py")
        manager = JobManagerSocket(python_script_path, parent_path, env_path, log_data_path, num_jobs, cpus_per_job, mem)
    else:
        python_script_path = os.path.join(icarus_directory, "multi_job_managment/task_monitor.py")
        manager = JobManager(python_script_path, parent_path, env_path, log_data_path, monitor_file_template, num_jobs, cpus_per_job, mem)
    manager.create_jobs()
    
def delete_files_in_directory(directory_path):
    directory_path = os.path.abspath(directory_path)
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"The directory {directory_path} does not exist.", flush=True)
        return

    # Iterate over all files in the directory and remove them
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                # print(f"Deleted {file_path}")
            else:
                print(f"Skipped {file_path} (Not a file)", flush=True)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}", flush=True)

def copy_files_with_subdirectories(paths_to_copy, destination_folder):
    for source_path in paths_to_copy:
        # Get the last component of the source path
        _, last_component = os.path.split(source_path)
        # Construct the destination path
        destination_path = os.path.join(destination_folder, last_component)
        source_path = os.path.abspath(source_path)
        # If the source path is a file, copy it directly
        if os.path.isfile(source_path):
            # Create the directory structure if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)
            # Copy the file to the destination
            shutil.copyfile(source_path, destination_path)
        # If the source path is a directory, copy its contents recursively
        elif os.path.isdir(source_path):
            # Copy the directory contents to the destination
            for root, _, files in os.walk(source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    # Construct the destination file path
                    destination_file = os.path.join(destination_path, os.path.relpath(source_file, source_path))
                    # Create the directory structure if it doesn't exist
                    os.makedirs(os.path.dirname(destination_file), exist_ok=True)
                    # Copy the file to the destination
                    shutil.copyfile(source_file, destination_file)
                    
def get_largest_numbered_folder(directory):
    # Get list of all directories in the specified directory
    directories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

    # Filter out non-numeric directories and convert the remaining ones to integers
    numeric_directories = [int(d) for d in directories if d.isdigit()]

    if numeric_directories:
        # Return the maximum number
        return max(numeric_directories)
    else:
        # If no numeric directories found, return None
        return 0
    
def copy_files(output_dir, conf_id, paths_to_copy, config_sim, config_init):
    output_dir = os.path.abspath(output_dir)
    new_dir_path = os.path.join(output_dir, str(conf_id))
    if not os.path.exists(new_dir_path):
        os.makedirs(new_dir_path)
    copy_files_with_subdirectories(paths_to_copy, new_dir_path)
    file_path = os.path.join(new_dir_path, "config_sim.pkl")
    with open(file_path, 'wb') as file:
        pickle.dump(config_sim, file)
    file_path = os.path.join(new_dir_path, "config_init.pkl")
    with open(file_path, 'wb') as file:
        pickle.dump(config_init, file)

def create_temp_subdirectory():
    # Get the path to the temporary directory
    temp_dir = tempfile.gettempdir()
    
    # Generate a random folder name
    random_folder_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Create the random folder in the temporary directory
    random_folder_path = os.path.join(temp_dir, random_folder_name)
    os.makedirs(random_folder_path)
    
    # Create a subdirectory named "results" inside the random folder
    results_subdirectory_path = os.path.join(random_folder_path, "results")
    os.makedirs(results_subdirectory_path)
    
    return results_subdirectory_path
            
def clean_paths(list_of_directories):
    for directory in list_of_directories:
        delete_files_in_directory(directory)
        
def load_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

def extract_config_init(config):
    run_jobs = config['run_jobs']
    core_number = config['core_number']
    output_dir = config['output_dir']
    num_jobs = config['num_jobs']
    run_with_socket = config['run_with_socket']
    number_of_runs = config['number_of_runs']
    interval_size_sec = config['interval_size_sec']
    interval_size_min = config['interval_size_min']
    return run_jobs, core_number, output_dir, num_jobs, run_with_socket, number_of_runs, interval_size_sec, interval_size_min
    
def update_time_intervals(config, interval_size_sec, interval_size_min):
    lsn_value = config["lsn"]

    # Extract current time components
    hrs = lsn_value["hrs"][0]
    mins = lsn_value["mins"][0]
    secs = lsn_value["secs"][0]

    # Calculate total seconds after adding intervals
    total_secs = hrs * 3600 + mins * 60 + secs + interval_size_sec + interval_size_min * 60

    # Calculate new time components
    new_hrs = total_secs // 3600
    new_mins = (total_secs % 3600) // 60
    new_secs = total_secs % 60

    # Update time components
    lsn_value["hrs"][0] = new_hrs
    lsn_value["mins"][0] = new_mins
    lsn_value["secs"][0] = new_secs
    
def create_run_folder(result_dir, run_num):
    # Create the directory path
    run_folder = os.path.join(result_dir, f"{run_num}")

    # Create the directory if it doesn't exist
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)

    # Return the path to the created directory
    return run_folder