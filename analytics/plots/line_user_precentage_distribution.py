import sys
import os

# Add the parent directory (analytics) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from sim_data_loader import SimulationDataLoader
import os


import matplotlib.pyplot as plt

def dict_normalizer(input_dict, divisor):
    """
    Divide all values in the dictionary by the given divisor, modifying the original dictionary in place.
    
    Args:
    input_dict (dict): The original dictionary with numeric values.
    divisor (int or float): The number to divide each value by.

    Returns:
    None
    """
    if divisor == 0:
        raise ValueError("The divisor cannot be zero.")
    
    for key in input_dict:
        input_dict[key] /= divisor

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


def plot_percentage_distribution(data_dict, filepath):
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
    plt.title('Zone Scenario User Percentage Distribution appearance')
    plt.ylim(0, 1)
    
    # Save the plot to a file
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    
    
def find_and_process_data(base_path):
    base_path = os.path.abspath(base_path)
    counter = 0
    total_attacks = 0
    total_attack_dict = {}
    file_path = "/home/roeeidan/icarus_framework/analytics/outputs/line_distribution/distribution_user_precentage_appearance_line.png"
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                results_dir = os.path.join(root, dir_name)
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        counter +=1
                        if counter % 1 == 0:
                            print(f"Current step: {counter}", flush=True)
                        loader = SimulationDataLoader(sub_dir_path)
                        loader.load_data("LAtk")
                        if "LAtk" in loader.data_cache:
                            datas = loader.data_cache["LAtk"][0]
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
                dict_normalizer(total_attack_dict,total_attacks)
                
                
                plot_percentage_distribution(total_attack_dict,file_path)
                return
                                
                        

# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)