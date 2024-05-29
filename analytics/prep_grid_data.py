from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle
from collections import defaultdict

def find_and_process_data(base_path):
    base_path = os.path.abspath(base_path)
    counter = 0
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                results_dir = os.path.join(root, dir_name)
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        counter +=1
                        if counter % 100 == 0:
                            print(f"Current step: {counter}")
                        pickle_path = os.path.join(sub_dir_path, 'line_attack_grid_count.pkl')
                        if os.path.exists(pickle_path):
                            continue
                        loader = SimulationDataLoader(sub_dir_path)
                        loader.load_data("LAtk")
                        if "LAtk" in loader.data_cache:
                            datas = loader.data_cache["LAtk"][0]
                            individual_counts = defaultdict(int)
                            for data in datas.values():
                                if data is None:
                                    continue
                                atkflowset = data.atkflowset
                                # Increment count for num1 and num2
                                for ((num1, num2), _) in atkflowset:
                                    individual_counts[num1] += 1
                                    individual_counts[num2] += 1
                            # Save individual counts to pickle in the same directory
                            
                            with open(pickle_path, 'wb') as file:
                                pickle.dump(individual_counts, file)

def save_data_as_pickle(data, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)
    print(f"Data saved as pickle at: {file_path}")

# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)