from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle
from collections import defaultdict

# loader = SimulationDataLoader("/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData/43/results/3/")
# loader.load_data("LAtk")  # Load the data for 'LSN', no need to assign

# # Accessing data directly from the cache
# if "LAtk" in loader.data_cache:
#     try:
#         first_key, first_value = next(iter(loader.data_cache["LAtk"][0].items()))
#         print(f"First item: Key = {first_key}, Value = {type(first_value)}")
#     except StopIteration:
#         print("The dictionary is empty.")
#     except KeyError:
#         print("Key 'ZAtk' not found in data_cache.")

# def compare_dictionaries(dicts):
#     """Compare multiple dictionaries to check if all values for matching keys are the same."""
#     if not dicts:
#         return True
    
#     # Reference dictionary to compare against
#     reference = dicts[0]

#     for key in reference:
#         reference_value = reference[key]
#         for d in dicts[1:]:
#             if key not in d or d[key] != reference_value:
#                 return False
#     return True

# def find_and_compare_data(base_path):
#     base_path = os.path.abspath(base_path)
#     dict_list = []

#     for root, dirs, files in os.walk(base_path):
#         for dir_name in dirs:
#             if dir_name == 'results':
#                 results_dir = os.path.join(root, dir_name)
#                 for sub_dir_name in os.listdir(results_dir):
#                     sub_dir_path = os.path.join(results_dir, sub_dir_name)
#                     if os.path.isdir(sub_dir_path):
#                         loader = SimulationDataLoader(sub_dir_path)
#                         loader.load_data("Grid")
#                         if "Grid" in loader.data_cache:
#                             dict_list.append(loader.data_cache["Grid"][0])

#     all_equal = compare_dictionaries(dict_list)
#     return all_equal

# base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
# are_all_values_equal = find_and_compare_data(base_path)
# print("Are all values in the keys the same across all dictionaries?:", are_all_values_equal)


def find_and_process_data(base_path):
    base_path = os.path.abspath(base_path)
    total_number_counts = defaultdict(int)
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
                                    total_number_counts[num1] += 1
                                    total_number_counts[num2] += 1
                            # Save individual counts to pickle in the same directory
                            pickle_path = os.path.join(sub_dir_path, 'line_attack_grid_count.pkl')
                            with open(pickle_path, 'wb') as file:
                                pickle.dump(individual_counts, file)
    return total_number_counts

def save_data_as_pickle(data, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(data, file)
    print(f"Data saved as pickle at: {file_path}")

# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
counts = find_and_process_data(base_path)
pickle_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData/study_data/total_line_attack_grid_count.pkl'
save_data_as_pickle(counts, pickle_path)