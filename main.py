#  2020 Tommaso Ciussani and Giacomo Giuliari
"""
Example usage of the icarus_simulator and sat_plotter libraries.
This file makes use of the configuration mechanism, described in configuration.py.

For general information on the library usage, refer to readme.md and to the following files:
    - icarus_simulator/icarus_simulator.py,
    - icarus_simulator/phases/base_phase.py,
    - icarus_simulator/strategies/base_strategy.py,
    - icarus_simulator/structure_definitions,
    - icarus_simulator/multiprocessor.py

This file first exemplifies the creation of the computation phases and the simulation execution, then extracts data
from the IcarusSimulator object and creates useful plots.
After adjusting the class constants, execute the file to create the plots and the result dumps.
Due to the computational burden, it is advised to always run this library on a heavy-multicore machine.
"""
import os
import shutil
import pickle
from statistics import mean
import tempfile
import random
import string

from icarus_simulator.icarus_simulator import IcarusSimulator
from icarus_simulator.default_properties import *
from icarus_simulator.phases import *
from sat_plotter import GeoPlotBuilder
from sat_plotter.stat_plot_builder import StatPlotBuilder

from configuration import CONFIG, parse_config, get_strat, get_random_dict

import sys

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout  # Save a reference to the original standard output
        self.log = open(filename, "a")  # Open a log file in append mode

    def write(self, message):
        self.terminal.write(message)  # Write the message to the standard output
        self.log.write(message)  # Write the message to the log file

    def flush(self):  # Needed for Python 3 compatibility
        # This flush method is needed for python 3 compatibility.
        # This handles the implicit flush command by file objects.
        pass
    
# Change these parameters to match your machine
CORE_NUMBER = 16
RESULTS_DIR = "results"
OUTPUT_DIR = "outputs"
LOGS_DIR = "logs"
TEMP_DATA = "icarus_simulator/temp_data"

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
    
def copy_files(output_dir, conf_id, paths_to_copy, conf):
    output_dir = os.path.abspath(output_dir)
    new_dir_path = os.path.join(output_dir, str(conf_id))
    if not os.path.exists(new_dir_path):
        os.makedirs(new_dir_path)
    copy_files_with_subdirectories(paths_to_copy, new_dir_path)
    file_path = os.path.join(new_dir_path, "conf.pkl")
    with open(file_path, 'wb') as file:
        pickle.dump(conf, file)

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
            
def prepare_jobs():
    from job_manager import JobManager
    python_script_path = "/home/roeeidan/icarus_framework/task_monitor.py"
    parent_path = "/home/roeeidan/icarus_framework"
    env_path = "/home/roeeidan/.conda/envs/icarus/bin/python"
    temp_data_path = "/home/roeeidan/icarus_framework/logs"
    monitor_file_template = "/home/roeeidan/icarus_framework/icarus_simulator/temp_data/run_X.txt"
    num_jobs = 40
    cpus_per_job = CORE_NUMBER
    mem = 120

    manager = JobManager(python_script_path, parent_path, env_path, temp_data_path, monitor_file_template, num_jobs, cpus_per_job, mem)
    manager.create_jobs()  

def clean_paths(list_of_directories):
    for directory in list_of_directories:
        delete_files_in_directory(directory)
    
def prepare_system(logs_dir, paths_to_copy):
    from cancel_monitor_jobs import clear_jobs
    clear_jobs()
    delete_files_in_directory(logs_dir)
    clean_paths(paths_to_copy)
    prepare_jobs()

def initialize_icarus(conf, core_number, run_jobs, result_dir):
    # SIMULATION: phase definition and final computation
        lsn_ph = LSNPhase(
            True,
            True,
            lsn_strat=get_strat("lsn", conf),
            lsn_out=SAT_POS,
            nw_out=SAT_NW,
            isls_out=SAT_ISLS,
        )

        grid_ph = GridPhase(
            True,
            True,
            grid_strat=get_strat("grid", conf),
            weight_strat=get_strat("gweight", conf),
            grid_out=FULL_GRID_POS,
            size_out=GRID_FULL_SZ,
        )

        cov_ph = CoveragePhase(
            True,
            True,
            cov_strat=get_strat("cover", conf),
            sat_in=SAT_POS,
            grid_in=FULL_GRID_POS,
            cov_out=COVERAGE,
            grid_out=GRID_POS,
        )

        rout_ph = RoutingPhase(
            True,
            True,
            num_procs=core_number,
            num_batches=3,
            run_jobs=run_jobs,
            rout_strat=get_strat("rout", conf),
            grid_in=GRID_POS,
            cov_in=COVERAGE,
            nw_in=SAT_NW,
            paths_out=PATH_DATA,
        )

        edge_ph = EdgePhase(
            True,
            True,
            num_procs=core_number,
            num_batches=1,
            run_jobs=run_jobs,
            ed_strat=get_strat("edges", conf),
            paths_in=PATH_DATA,
            nw_in=SAT_NW,
            sats_in=SAT_POS,
            grid_in=GRID_POS,
            edges_out=EDGE_DATA,
        )

        # FULL_GRID_POS is passed for consistency with other experiments, where the coverage grid filtering is different
        bw_ph = TrafficPhase(
            True,
            True,
            select_strat=get_strat("bw_sel", conf),
            assign_strat=get_strat("bw_asg", conf),
            grid_in=FULL_GRID_POS,
            paths_in=PATH_DATA,
            edges_in=EDGE_DATA,
            bw_out=BW_DATA,
        )

        latk_ph = LinkAttackPhase(
            True,
            True,
            num_procs=core_number,
            num_batches=3,
            run_jobs=run_jobs,
            geo_constr_strat=get_strat("atk_constr", conf),
            filter_strat=get_strat("atk_filt", conf),
            feas_strat=get_strat("atk_feas", conf),
            optim_strat=get_strat("atk_optim", conf),
            grid_in=GRID_POS,
            paths_in=PATH_DATA,
            edges_in=EDGE_DATA,
            bw_in=BW_DATA,
            latk_out=ATK_DATA,
        )

        zatk_ph = ZoneAttackPhase(
            True,
            True,
            num_procs=core_number,
            num_batches=4,
            run_jobs=run_jobs,
            geo_constr_strat=get_strat("atk_constr", conf),
            zone_select_strat=get_strat("zone_select", conf),
            zone_build_strat=get_strat("zone_build", conf),
            zone_edges_strat=get_strat("zone_edges", conf),
            zone_bneck_strat=get_strat("zone_bneck", conf),
            atk_filter_strat=get_strat("atk_filt", conf),
            atk_feas_strat=get_strat("atk_feas", conf),
            atk_optim_strat=get_strat("atk_optim", conf),
            grid_in=GRID_POS,
            paths_in=PATH_DATA,
            edges_in=EDGE_DATA,
            bw_in=BW_DATA,
            atk_in=ATK_DATA,
            zatk_out=ZONE_ATK_DATA,
        )
        
        sim_traffic_ph = SimulatedTrafficPhase(
            read_persist=True,
            persist=True,
            select_strat=get_strat("traffic_routing_select_simulation",conf),
            assign_strat=get_strat("traffic_routing_asg_simulation",conf),
            grid_in=FULL_GRID_POS,
            paths_in=PATH_DATA,
            edges_in=EDGE_DATA,
            traffic_out=TRAFFIC_DATA,
        )
        
        sim_attack_traffic_ph = SimulatedAttackTrafficPhase(
            read_persist=True,
            persist=True,
            num_procs=core_number,
            num_batches=2,
            run_jobs=run_jobs,
            select_strat=get_strat("traffic_attack_select_simulation",conf),
            assign_strat=get_strat("traffic_routing_asg_simulation",conf),
            paths_in=PATH_DATA,
            edges_in=EDGE_DATA,
            zattack_in=ZONE_ATK_DATA,
            traffic_in=TRAFFIC_DATA,
            attack_traffic_out= ATTACK_TRAFFIC_DATA,
        )

        sim = IcarusSimulator(
            [lsn_ph, grid_ph, cov_ph, rout_ph, edge_ph, bw_ph, latk_ph, zatk_ph, sim_traffic_ph, sim_attack_traffic_ph],
            result_dir,
        )
        return sim 
    
def main(output_dir=OUTPUT_DIR, core_number=CORE_NUMBER, run_jobs=True):
    output_dir = output_dir
    core_number = core_number
    if run_jobs:
        logs_dir = LOGS_DIR
        result_dir = RESULTS_DIR
        paths_to_copy = [logs_dir, result_dir]
        paths_to_clean = [result_dir,TEMP_DATA]
        prepare_system(logs_dir, paths_to_copy)
    else:
        result_dir = create_temp_subdirectory()
        print(f"Result dir path: {result_dir}", flush=True)
        logs_dir = result_dir
        paths_to_copy = [result_dir]
        paths_to_clean = [result_dir]
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    inital_start = get_largest_numbered_folder(output_dir) + 1
    number_runs = 999
    for conf_id in range(inital_start, inital_start + number_runs):
        print(f"current run out of {conf_id} {inital_start + number_runs}", flush=True)
        try:
            clean_paths(paths_to_clean)
            # Repeat the simulation process for all configurations in the config file
            conf = parse_config(get_random_dict())[0]
            logger_name = os.path.join(logs_dir, f"simulation_{conf_id}.log")
            sys.stdout = Logger(logger_name)
            sys.stderr = sys.stdout
            print(
                "---------------------------------------------------------------------------------"
            ,flush=True)
            print(f"Configuration number {conf_id} out of {number_runs}",flush=True)  # 0-based

            sim = initialize_icarus(conf, core_number, run_jobs, result_dir)
            sim.compute_simulation()
            
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            conf_id = get_largest_numbered_folder(output_dir) + 1
            copy_files(output_dir, conf_id, paths_to_copy, conf)
        except Exception as e:
            # TODO add something to do when it failes
            print(f"There was an error:", flush=True)
            print(f"{e}", flush=True)
            print(f"error end", flush=True)
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            conf_id = conf_id - 1
        os.remove(logger_name)
            

# Execute on main
if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        main()
    else:
        run_jobs = bool(int(sys.argv[1]))
        core_number = int(sys.argv[2])
        output_dir= sys.argv[3]
        main(output_dir=output_dir, run_jobs=run_jobs, core_number=core_number)
