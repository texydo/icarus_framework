import os
import sys
import shutil
import random
import pickle
import tempfile
import string
import json
import time
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
    
# def delete_files_in_directory(directory_path):
#     directory_path = os.path.abspath(directory_path)
#     # Check if the directory exists
#     if not os.path.isdir(directory_path):
#         print(f"The directory {directory_path} does not exist.", flush=True)
#         return

#     # Iterate over all files in the directory and remove them
#     for filename in os.listdir(directory_path):
#         file_path = os.path.join(directory_path, filename)
#         try:
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#                 os.unlink(file_path)
#                 # print(f"Deleted {file_path}")
#             else:
#                 print(f"Skipped {file_path} (Not a file)", flush=True)
#         except Exception as e:
#             print(f"Failed to delete {file_path}. Reason: {e}", flush=True)

def delete_files_in_directory(directory_path):
    directory_path = os.path.abspath(directory_path)
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"The directory {directory_path} does not exist.", flush=True)
        return

    # Iterate over all items in the directory
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove the file or link
                # print(f"Deleted {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove the directory and all its contents
                # print(f"Deleted directory {item_path}")
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}", flush=True)
            
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
    hrs = lsn_value["hrs"]
    mins = lsn_value["mins"]
    secs = lsn_value["secs"]

    # Calculate total seconds after adding intervals
    total_secs = hrs * 3600 + mins * 60 + secs + interval_size_sec + interval_size_min * 60

    # Calculate new time components
    new_hrs = total_secs // 3600
    new_mins = (total_secs % 3600) // 60
    new_secs = total_secs % 60

    # Update time components
    lsn_value["hrs"] = new_hrs
    lsn_value["mins"] = new_mins
    lsn_value["secs"] = new_secs

def set_time_intervals(config, interval_size_sec, interval_size_min):
    lsn_value = config["lsn"]
    total_secs = interval_size_sec + interval_size_min * 60
    new_hrs = total_secs // 3600
    new_mins = (total_secs % 3600) // 60
    new_secs = total_secs % 60

    # Update time components
    lsn_value["hrs"] = new_hrs
    lsn_value["mins"] = new_mins
    lsn_value["secs"] = new_secs
    
def zone_random_seed_generator(config):
    new_seed = random.randint(0, 2**32 - 1)
    config["zone_select"]["random_seed"] = [new_seed]

    
    
def create_run_folder(result_dir, run_num):
    # Create the directory path
    run_folder = os.path.join(result_dir, f"{run_num}")

    # Create the directory if it doesn't exist
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)

    # Return the path to the created directory
    return run_folder

def print_total_run_time_minutes(start_time):
    run_time_seconds = time.time() - start_time
    run_time_minutes = run_time_seconds / 60
    return run_time_minutes

def print_lines(num_lines):
    for _ in range(num_lines):
        print(
                "---------------------------------------------------------------------------------"
            ,flush=True)

def count_direct_subfolders(dir_path):
    """
    Count the number of direct subfolders in the given directory.

    Args:
    dir_path (str): The path to the directory.

    Returns:
    int: The number of direct subfolders.
    """
    if not os.path.isdir(dir_path):
        raise ValueError(f"The path {dir_path} is not a valid directory.")
    
    subfolders = [name for name in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, name))]
    return len(subfolders)

def create_next_interval_folder(base_path, min_interval, sec_interval):
    def parse_folder_name(folder_name):
        """Parse folder name to get the interval in seconds as an integer."""
        try:
            return int(folder_name)
        except ValueError:
            return None

    def calculate_step(min_interval, sec_interval):
        """Calculate the step size in seconds."""
        return min_interval * 60 + sec_interval

    def convert_seconds_to_min_sec(seconds):
        """Convert seconds to minutes and seconds."""
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return minutes, remaining_seconds

    # Calculate the step size in seconds
    step_size = calculate_step(min_interval, sec_interval)

    # Get list of all folders in the base path
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    
    # Parse folders and find the latest interval in seconds
    latest_interval = -1
    for folder in folders:
        interval = parse_folder_name(folder)
        if interval is not None and interval > latest_interval:
            latest_interval = interval

    # Calculate the next interval
    next_interval = latest_interval + step_size if latest_interval != -1 else 0
    next_folder_name = str(next_interval)
    next_folder_path = os.path.join(base_path, next_folder_name)

    # Create the next folder
    os.makedirs(next_folder_path, exist_ok=True)
    
    # Convert the next interval to minutes and seconds
    minutes, seconds = convert_seconds_to_min_sec(next_interval)

    return next_folder_path, minutes, seconds


def copy_configs(copy_dir, config_sim, config_init):
    output_dir = os.path.abspath(copy_dir)
    file_path = os.path.join(output_dir, "config_sim.pkl")
    with open(file_path, 'wb') as file:
        pickle.dump(config_sim, file)
    file_path = os.path.join(output_dir, "config_init.pkl")
    with open(file_path, 'wb') as file:
        pickle.dump(config_init, file)
