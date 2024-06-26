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
            [lsn_ph, grid_ph, cov_ph, rout_ph, edge_ph, bw_ph, latk_ph, zatk_ph], #simulate_scenario_ph], #, sim_traffic_ph, sim_attack_traffic_ph],
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
    
    inital_start = get_largest_numbered_folder(output_dir) + 1
    number_runs = 999
    for conf_id in range(inital_start, inital_start + number_runs):
        print(f"current run out of {conf_id} {inital_start + number_runs}", flush=True)
        try:
            clean_paths(paths_to_clean)
            # Repeat the simulation process for all configurations in the config file
            config_sim = parse_config(get_random_dict())[0]
            logger_name = os.path.join(logs_dir, f"simulation_{conf_id}.log")
            sys.stdout = Logger(logger_name)
            sys.stderr = sys.stdout
            print_lines(4)
            print(f"Configuration number {conf_id} out of {number_runs}",flush=True)  # 0-based
            
            total_start_time = time.time()
            for run_num in range(number_of_runs):
                print(f"Run number {run_num} out of {number_of_runs}", flush=True)
                single_start_time = time.time()
                current_result_folder  = create_run_folder(result_dir, run_num)
                if run_num == 0:
                    zone_random_seed_generator(config_sim)
                else:
                    update_time_intervals(config_sim, interval_size_sec, interval_size_min)
                sim = initialize_icarus(config_sim, core_number, run_jobs,num_jobs, run_with_socket, current_result_folder)
                sim.compute_simulation()
                print(f"Single run time took: {print_total_run_time_minutes(single_start_time):.2f} minutes", flush=True)
                print_lines(1)
            print(f"Simulation run time took: {print_total_run_time_minutes(total_start_time):.2f} minutes", flush=True)
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            conf_id = get_largest_numbered_folder(output_dir) + 1
            copy_files(output_dir, conf_id, paths_to_copy, config_sim,config_init)
        except Exception as e:
            print(f"There was an error:", flush=True)
            print(f"{e}", flush=True)
            print("Traceback (most recent call last):", flush=True)
            traceback.print_exc(file=sys.stdout)
            print(f"error end", flush=True)
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            conf_id = conf_id - 1
        os.remove(logger_name) 
                  
def get_results_folders(main_folder, num):
    folders = [os.path.join(main_folder, folder) for folder in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, folder))]
    folders.sort(key=lambda x: int(os.path.basename(x)))
    filtered_folders = []
    for folder in folders:
        folder_name = os.path.basename(folder)
        # if int(folder_name) % 5 == num:
        results_folder = os.path.join(folder, 'results')
        if os.path.exists(results_folder):
            filtered_folders.append(results_folder)
    return filtered_folders

def create_training_data(run_jobs, core_number, output_dir, num_jobs, run_with_socket):
    output_dir = output_dir
    data_folders = get_results_folders(output_dir, 4)
    core_number = core_number
    for folder in data_folders:
        try:
            conf = parse_config(get_random_dict())[0]
            result_dir = folder
            print(
                "---------------------------------------------------------------------------------"
            ,flush=True)
            print(f"Configuration number {folder} out of {len(data_folders)}",flush=True)  # 0-based
            
            sim = initialize_icarus(conf, core_number, run_jobs,num_jobs, run_with_socket, result_dir)
            sim.compute_simulation()
        except Exception as e:
            # TODO add something to do when it failes
            print(f"There was an error:", flush=True)
            print(f"{e}", flush=True)
            print(f"error end", flush=True)
            
# Execute on main
if __name__ == "__main__":
    if len(sys.argv) == 1:
        setup_config_path = os.path.join(os.getcwd(),"configurations/config.json")
    else:
        setup_config_path = sys.argv[1]
    config_init = load_config(setup_config_path)
    main(config_init)


