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
from statistics import mean

from icarus_simulator.icarus_simulator import IcarusSimulator
from icarus_simulator.default_properties import *
from icarus_simulator.phases import *
from sat_plotter import GeoPlotBuilder
from sat_plotter.stat_plot_builder import StatPlotBuilder

from configuration import CONFIG, parse_config, get_strat

# Change these parameters to match your machine
CORE_NUMBER = 16
RESULTS_DIR = "result_dumps"

def delete_files_in_directory(directory_path):
    import os
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return

    # Iterate over all files in the directory and remove them
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                # print(f"Deleted {file_path}")
            else:
                print(f"Skipped {file_path} (Not a file)")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
            
def run_jobs():
    from job_manager import JobManager
    python_script_path = "/home/roeeidan/icarus_framework/task_monitor.py"
    parent_path = "/home/roeeidan/icarus_framework"
    env_path = "/home/roeeidan/.conda/envs/icarus/bin/python"
    temp_data_path = "/home/roeeidan/icarus_framework/logs"
    monitor_file_template = "/home/roeeidan/icarus_framework/icarus_simulator/temp_data/run_X.txt"
    num_jobs = 40
    cpus_per_job = 16
    mem = 120

    manager = JobManager(python_script_path, parent_path, env_path, temp_data_path, monitor_file_template, num_jobs, cpus_per_job, mem)
    manager.create_jobs()  


def prepare_system():
    from cancel_monitor_jobs import clear_jobs
    clear_jobs()
    # delete_files_in_directory("/home/roeeidan/icarus_framework/result_dumps")
    delete_files_in_directory("/home/roeeidan/icarus_framework/icarus_simulator/temp_data")
    delete_files_in_directory("/home/roeeidan/icarus_framework/logs")
    run_jobs()

def initialize_icarus(conf):
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
            CORE_NUMBER,
            2,
            rout_strat=get_strat("rout", conf),
            grid_in=GRID_POS,
            cov_in=COVERAGE,
            nw_in=SAT_NW,
            paths_out=PATH_DATA,
        )

        edge_ph = EdgePhase(
            True,
            True,
            CORE_NUMBER,
            1,
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
            CORE_NUMBER,
            3,
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
            CORE_NUMBER,
            4,
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
            RESULTS_DIR,
        )
        return sim 
    
def main():
    prepare_system()
    # Optional feature: parse the configuration file
    full_conf = parse_config(CONFIG)

    for conf_id, conf in enumerate(full_conf):
        # Repeat the simulation process for all configurations in the config file
        print(
            "---------------------------------------------------------------------------------"
        )
        print(f"Configuration number {conf_id}")  # 0-based

        sim = initialize_icarus(conf)
        sim.compute_simulation()
        print("Computation finished")

        # EXAMPLE PLOTS
        # GEOGRAPHICAL PLOTS
        sat_pos, isls, grid_pos = (
            sim.get_property(SAT_POS),
            sim.get_property(SAT_ISLS),
            sim.get_property(GRID_POS),
        )
        edge_data, bw_data = sim.get_property(EDGE_DATA), sim.get_property(BW_DATA)
        path_data, atk_data = sim.get_property(PATH_DATA), sim.get_property(ATK_DATA)
        zatk_data = sim.get_property(ZONE_ATK_DATA)
        traffic_data =sim.get_property(TRAFFIC_DATA)
        attack_traffic_data = sim.get_property(ATTACK_TRAFFIC_DATA)
        print("")
        

# Execute on main
if __name__ == "__main__":
    main()
