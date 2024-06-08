from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle
import matplotlib.pyplot as plt

def merge_integer_dictionaries(base_dict, new_dict):
    """
    Merge new_dict into base_dict. If a key exists in both, add the values.
    
    Args:
    base_dict (dict): The original dictionary with integer keys and values.
    new_dict (dict): The dictionary to merge into the original with integer keys and values.

    Returns:
    dict: The updated dictionary.
    """
    for key, value in new_dict.items():
        if key in base_dict:
            base_dict[key] += value
        else:
            base_dict[key] = value


def plot_percentage_distribution(data_dict, filename):
    """
    Plots the percentage distribution of dictionary values in descending order and saves the figure.
    
    Args:
    data_dict (dict): Dictionary with keys and percentage values (between 0 and 1).
    filename (str): The filename to save the plot.
    """
    # Sort the values in descending order
    sorted_values = sorted(data_dict.values(), reverse=True)
    
    # Create the bar plot
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(sorted_values)), sorted_values, color='skyblue')
    plt.ylabel('Percentage')
    plt.title('Zone scenario Percentage Distribution appearance')
    plt.ylim(0, 1)
    
    # Save the plot to a file
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    
    
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
                        if counter % 5 == 0:
                            print(f"Current step: {counter}", flush=True)
                        loader = SimulationDataLoader(sub_dir_path)
                        loader.load_data("ZAtk")
                        total_attacks = 0
                        total_attack_dict = {}
                        if "ZAtk" in loader.data_cache:
                            datas = loader.data_cache["ZAtk"][0]
                            for data in datas.values():
                                if data is None:
                                    continue
                                atkflowset = data.atkflowset
                                dict_show_up = {}
                                total_attacks += 1
                                for item in atkflowset:
                                    if item[0][0] not in dict_show_up.keys():
                                        dict_show_up[item[0][0]] = 1
                                    if item[0][1] not in dict_show_up.keys():
                                        dict_show_up[item[0][0]] = 1
                                merge_integer_dictionaries(total_attack_dict, dict_show_up)
                        return
                                
                        

# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)