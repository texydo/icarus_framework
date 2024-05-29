from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle
from collections import defaultdict

loader = SimulationDataLoader("/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData/43/results/3/")
loader.load_data("ZAtk")  # Load the data for 'LSN', no need to assign

# Accessing data directly from the cache
if "ZAtk" in loader.data_cache:
    try:
        first_key, first_value = next(iter(loader.data_cache["ZAtk"][0].items()))
        print(f"First item: Key = {first_key}, Value = {type(first_value)}")
    except StopIteration:
        print("The dictionary is empty.")
    except KeyError:
        print("Key 'ZAtk' not found in data_cache.")

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