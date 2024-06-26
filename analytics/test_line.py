from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle
from collections import defaultdict


def find_and_process_data(base_path):
    base_path = os.path.abspath(base_path)
    counter = 0
    all_atks_counter = 0
    number_atks = 0
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                results_dir = os.path.join(root, dir_name)
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        counter +=1
                        if counter % 5 == 0:
                            print(f"Current step: {counter}", flush=True)
                            print(f"Average number of attackers per line: {all_atks_counter/number_atks}")
                        loader = SimulationDataLoader(sub_dir_path)
                        loader.load_data("ZoneBottle")
                        datas = loader.data_cache["ZoneBottle"][0]
                        loader.load_data("Routes")
                        datas = loader.data_cache["Routes"][0]
                        loader.load_data("LAtk")
                        if "LAtk" in loader.data_cache:
                            datas = loader.data_cache["LAtk"][0]
                            individual_counts = defaultdict(int)
                            for data in datas.values():
                                if data is None:
                                    continue
                                atkflowset = data.atkflowset
                                all_atks_counter += len(atkflowset)
                                number_atks +=1
    print(f"Final Average number of attackers per line: {all_atks_counter/number_atks}")


# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/sim_intervals_30s/55770/'
find_and_process_data(base_path)