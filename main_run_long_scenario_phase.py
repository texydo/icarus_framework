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
import time

from icarus_simulator.icarus_simulator import IcarusSimulator
from icarus_simulator.default_properties import *
from icarus_simulator.phases import *

from configurations.icarus_configuration import CONFIG, parse_config, get_strat, get_random_dict

import sys
import traceback
from multi_job_managment.cancel_monitor_jobs import clear_jobs
from multi_job_managment.logger import Logger
from main_utils import *
    
# Change these parameters to match your machine
CORE_NUMBER = 128
RESULTS_DIR = "results"
OUTPUT_DIR = "outputs"
LOGS_DIR = "logs"
TEMP_DATA = "icarus_simulator/temp_data"
    

def get_random_order_subfolders(folder_path):
    """
    Get all subfolders within a specified folder and return their full paths in a random order.

    Parameters:
    folder_path (str): The path of the folder to search for subfolders.

    Returns:
    list: A list of full paths to each subfolder in random order.
    """
    subfolders = []
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            subfolders.append(os.path.join(root, dir_name))
    
    random.shuffle(subfolders)
    return subfolders

def load_config_sim(folder_path):
    sim_pkl_file_path = os.path.join(folder_path, 'config_sim.pkl') 
    # Check if the file exists
    if os.path.exists(sim_pkl_file_path):
        with open(sim_pkl_file_path, 'rb') as pkl_file:
            sim_config_data = pickle.load(pkl_file)
    sim_config_data["lsn"]["hrs"] = 0
    sim_config_data["lsn"]["mins"] = 0
    sim_config_data["lsn"]["secs"] = 0
    return sim_config_data
    
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
        
        zbatk_ph = ZoneBottleneckPhase(
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
            [lsn_ph, grid_ph, cov_ph, rout_ph, edge_ph, bw_ph, latk_ph, zbatk_ph], result_dir,
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
    
    folder_num = 0
    
    all_folders = get_random_order_subfolders(output_dir)
    total_runs = len(all_folders)
    for current_out_dir in all_folders:
        folder_num += 1
        print(f"Current folder {current_out_dir} current run out of {folder_num} {total_runs}", flush=True)
        try:
            config_sim = load_config_sim(output_dir)
            
            
            logger_name = os.path.join(current_out_dir, f"simulation_bottle.log")
            if os.path.exists(os.path.join(current_out_dir, f"ZoneBottlePhase.pkl.bz2")) or os.path.exists(logger_name):
                continue
            sys.stdout = Logger(logger_name)
            sys.stderr = sys.stdout
            print_lines(4)
            print(f"Configuration number {folder_num} out of {total_runs}",flush=True)  # 0-based
            
            total_start_time = time.time()
            sim = initialize_icarus(config_sim, core_number, run_jobs,num_jobs, run_with_socket, current_out_dir)
            sim.compute_simulation()
            print_lines(1)
                
            print(f"Simulation run time took: {print_total_run_time_minutes(total_start_time):.2f} minutes", flush=True)
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            copy_configs(current_out_dir, config_sim, config_init)
            os.remove(logger_name)
        except Exception as e:
            print(f"There was an error:", flush=True)
            print(f"{e}", flush=True)
            print("Traceback (most recent call last):", flush=True)
            traceback.print_exc(file=sys.stdout)
            print(f"error end", flush=True)
            sys.stdout.log.close()  # Close the log file associated with the logger
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
                  
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


