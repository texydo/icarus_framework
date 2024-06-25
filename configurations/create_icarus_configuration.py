
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pickle
from icarus_simulator.strategies import *

def save_config(config_sim, save_path):

    with open(save_path, 'wb') as file:
        pickle.dump(config_sim, file)


def edit_config(sim_pkl_file_path):
    with open(sim_pkl_file_path, 'rb') as pkl_file:
            sim_config_data = pickle.load(pkl_file)
    sim_config_data["zone_select"] = {}
    sim_config_data["zone_select"]["strat"] = LoadZoneStrat
    sim_config_data["zone_select"]["dataset_file"] = None
    save_config(sim_config_data, sim_pkl_file_path)

def update_all_configs(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == "config_sim.pkl":
                import time
                start_time = time.time()
                config_path = os.path.join(dirpath, filename)
                edit_config(config_path)
                print(f"It took {time.time() - start_time} ")

root_directory = '/dt/shabtaia/DT_Satellite/icarus_data/sim_intervals_30s/'
update_all_configs(root_directory)