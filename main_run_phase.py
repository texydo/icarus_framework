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
import time

from icarus_simulator.icarus_simulator import IcarusSimulator
from icarus_simulator.default_properties import *
from icarus_simulator.phases import *
from sat_plotter import GeoPlotBuilder
from sat_plotter.stat_plot_builder import StatPlotBuilder

from configurations.icarus_configuration import CONFIG, parse_config, get_strat, get_random_dict

import sys
import traceback

from multi_job_managment.job_manager import JobManager, JobManagerSocket
from multi_job_managment.cancel_monitor_jobs import clear_jobs
from multi_job_managment.logger import Logger
from main_utils import *
    
# Change these parameters to match your machine
CORE_NUMBER = 128
RESULTS_DIR = "results"
OUTPUT_DIR = "outputs"
LOGS_DIR = "logs"
TEMP_DATA = "icarus_simulator/temp_data"
    
def prepare_system(logs_dir, paths_to_copy, core_number,num_jobs, with_socket):
    clear_jobs()
    delete_files_in_directory(logs_dir)
    clean_paths(paths_to_copy)
    prepare_jobs(core_number, num_jobs, with_socket)

def get_ascending_order_folders(directory, n=1, m=1):
    # List all entries in the directory
    entries = os.listdir(directory)
    
    # Filter out non-directory entries and keep only numerical directories
    numerical_folders = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry)) and entry.isdigit()]
    
    # Sort the directories in ascending numerical order
    sorted_folders = sorted(numerical_folders, key=int)
    
    # Filter folders based on the condition folder_number % n == m
    filtered_folders = [folder for folder in sorted_folders if int(folder) % n == m]
    
    return filtered_folders

def load_config_files(folder_path):
    init_pkl_file_path = os.path.join(folder_path, 'config_init.pkl')
        
    # Check if the file exists
    if os.path.exists(init_pkl_file_path):
        with open(init_pkl_file_path, 'rb') as pkl_file:
            init_config_data = pickle.load(pkl_file)
    
    sim_pkl_file_path = os.path.join(folder_path, 'config_sim.pkl')
        
    # Check if the file exists
    if os.path.exists(sim_pkl_file_path):
        with open(sim_pkl_file_path, 'rb') as pkl_file:
            sim_config_data = pickle.load(pkl_file)
    sim_config_data["lsn"]["hrs"] = 0
    sim_config_data["lsn"]["mins"] = 0
    sim_config_data["lsn"]["secs"] = 0
    
    number_of_runs = init_config_data["number_of_runs"]
    interval_size_sec = init_config_data["interval_size_sec"]
    interval_size_min = init_config_data["interval_size_min"]
    return sim_config_data, number_of_runs, interval_size_sec, interval_size_min
    
def initialize_icarus(conf, core_number, run_jobs,num_jobs, run_server, result_dir):
    # SIMULATION: phase definition and final computation
        lsn_ph = LSNPhase(
            read_persist=True,
            persist=True,
            lsn_strat=get_strat("lsn", conf),
            lsn_out=SAT_POS,
            nw_out=SAT_NW,
            isls_out=SAT_ISLS,
        )

        grid_ph = GridPhase(
            read_persist=True,
            persist=True,
            grid_strat=get_strat("grid", conf),
            weight_strat=get_strat("gweight", conf),
            grid_out=FULL_GRID_POS,
            size_out=GRID_FULL_SZ,
        )

        cov_ph = CoveragePhase(
            read_persist=True,
            persist=True,
            cov_strat=get_strat("cover", conf),
            sat_in=SAT_POS,
            grid_in=FULL_GRID_POS,
            cov_out=COVERAGE,
            grid_out=GRID_POS,
        )

        rout_ph = RoutingPhase(
            read_persist=True,
            persist=True,
            num_jobs=num_jobs,
            num_procs=core_number,
            run_server = run_server,
            num_batches=3,
            run_jobs=run_jobs,
            rout_strat=get_strat("rout", conf),
            grid_in=GRID_POS,
            cov_in=COVERAGE,
            nw_in=SAT_NW,
            paths_out=PATH_DATA,
        )

        edge_ph = EdgePhase(
            read_persist=True,
            persist=True,
            num_jobs=num_jobs,
            num_procs=core_number,
            run_server = run_server,
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
            read_persist=True,
            persist=True,
            select_strat=get_strat("bw_sel", conf),
            assign_strat=get_strat("bw_asg", conf),
            grid_in=FULL_GRID_POS,
            paths_in=PATH_DATA,
            edges_in=EDGE_DATA,
            bw_out=BW_DATA,
        )

        latk_ph = LinkAttackPhase(
            read_persist=True,
            persist=True,
            num_jobs=num_jobs,
            num_procs=core_number,
            run_server = run_server,
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
            read_persist=True,
            persist=True,
            num_jobs=num_jobs,
            num_procs=core_number,
            run_server = run_server,
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
            num_jobs=num_jobs,
            num_procs=core_number,
            run_server = run_server,
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

        simulate_scenario_ph = SimulatedScenarioPhase(
            read_persist=True,
            persist=True,
            num_jobs=num_jobs,
            num_procs=core_number,
            run_server = run_server,
            num_batches=2,
            run_jobs=run_jobs,
            select_strat=get_strat("traffic_routing_select_simulation",conf),
            assign_strat=get_strat("traffic_routing_asg_simulation",conf),
            attack_select_strat=get_strat("traffic_attack_select_simulation",conf),
            training_data_strat=get_strat("training_data_creation",conf),
            sat_in=SAT_POS,
            grid_in=FULL_GRID_POS,
            paths_in=PATH_DATA,
            edges_in=EDGE_DATA,
            zattack_in=ZONE_ATK_DATA,
            scenario_out= SCENARIO_SIMULATED_DATA,
        )

        sim = IcarusSimulator(
            [lsn_ph, grid_ph, cov_ph, rout_ph, edge_ph, bw_ph, latk_ph, zatk_ph,simulate_scenario_ph], #, sim_traffic_ph, sim_attack_traffic_ph],
            result_dir,
        )
        return sim 


def main(config_init):
    config_init_values = extract_config_init(config_init)
    run_jobs, core_number, output_dir, num_jobs, run_with_socket = config_init_values[:5]
    number_of_runs, interval_size_sec, interval_size_min = config_init_values[5:]
    
    output_dir = output_dir
    core_number = core_number
    if run_jobs:
        logs_dir = LOGS_DIR
        result_dir = RESULTS_DIR
        paths_to_copy = [logs_dir, result_dir]
        paths_to_clean = [result_dir,TEMP_DATA]
        prepare_system(logs_dir, paths_to_copy, core_number, num_jobs, run_with_socket)
    else:
        result_dir = create_temp_subdirectory()
        print(f"Result dir path: {result_dir}", flush=True)
        logs_dir = result_dir
        paths_to_copy = [result_dir]
        paths_to_clean = [result_dir]
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    run_on_scenarios = get_ascending_order_folders(output_dir,3,0)
    
    for current_scenario in run_on_scenarios:
        scenario_path = os.path.join(output_dir, current_scenario)
        print(f"current run out of {current_scenario} / {run_on_scenarios[-1]}", flush=True)
        try:
            config_sim, number_of_runs, interval_size_sec, interval_size_min= load_config_files(scenario_path)
            clean_paths(paths_to_clean)
            logger_name = os.path.join(scenario_path, "results", f"simulation_all_traffic.log") #TODO change that it will have function
            
            sys.stdout = Logger(logger_name)
            sys.stderr = sys.stdout
            print_lines(4)
            
            total_start_time = time.time()
            for run_num in range(number_of_runs):
                currect_step_dict = os.path.join(scenario_path,"results",str(run_num))
                print(f"Run number {run_num} out of {number_of_runs}", flush=True)
                single_start_time = time.time()
                if run_num != 0:
                    update_time_intervals(config_sim, interval_size_sec, interval_size_min)
                sim = initialize_icarus(config_sim, core_number, run_jobs,num_jobs, run_with_socket, currect_step_dict)
                sim.compute_simulation()
                print(f"Single run time took: {print_total_run_time_minutes(single_start_time):.2f} minutes", flush=True)
                print_lines(1)
            
            print(f"Simulation run time took: {print_total_run_time_minutes(total_start_time):.2f} minutes", flush=True)
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
        except Exception as e:
            print(f"There was an error:", flush=True)
            print(f"{e}", flush=True)
            print("Traceback (most recent call last):", flush=True)
            traceback.print_exc(file=sys.stdout)
            print(f"error end", flush=True)
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        os.remove(logger_name) 

# Execute on main
if __name__ == "__main__":
    if len(sys.argv) == 1:
        setup_config_path = os.path.join(os.getcwd(),"configurations/config.json")
    else:
        setup_config_path = sys.argv[1]
    config_init = load_config(setup_config_path)
    main(config_init)


