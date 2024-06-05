import sys
import os
import matplotlib.pyplot as plt

# Add the parent directory (analytics) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sim_data_loader import SimulationDataLoader
import pickle

def update_single_snapshot_dict(snapshot_single_dict,snapshot_pair_dict, num1,num2):
    if num1 in snapshot_single_dict:
            snapshot_single_dict[num1] += 1
    else:
        snapshot_single_dict[num1] = 1
        
    if num2 in snapshot_single_dict:
        snapshot_single_dict[num2] += 1
    else:
        snapshot_single_dict[num2] = 1
    
        # Update pair count
    pair = (num1, num2)
    if pair in snapshot_pair_dict:
        snapshot_pair_dict[pair] += 1
    else:
        snapshot_pair_dict[pair] = 1

def merge_dicts_with_addition(scenario_dict, snapshot_dict):
    for key, value in snapshot_dict.items():
        if key in scenario_dict:
            scenario_dict[key] += value
        else:
            scenario_dict[key] = value

def prep_datas(sub_dir_path):
    loader = SimulationDataLoader(sub_dir_path)
    loader.load_data("LAtk")
    datas = loader.data_cache["LAtk"][0]
    return datas

def update_snapshot_dict(snapshot_single_dict,snapshot_pair_dict, datas):
    for data in datas.values():
        if data is None:
            continue
        atkflowset = data.atkflowset
        for item in atkflowset:
            num1, num2 = item[0]
            update_single_snapshot_dict(snapshot_single_dict, snapshot_pair_dict, num1, num2)

def plot_and_save_histograms(individual_count, pair_count, path='.', filename='histograms_line_attackers.png', ):
    """
    Plots and saves histograms for individual counts and pair counts to a file.
    
    Parameters:
    individual_count (dict): Dictionary of individual counts
    pair_count (dict): Dictionary of pair counts
    filename (str): The filename to save the histograms (default is 'histograms.png')
    """
    # Create a figure
    file_path = os.path.join(path, filename)
    
    # Create a figure
    plt.figure(figsize=(12, 5))

    # Histogram for individual counts
    plt.subplot(1, 2, 1)
    plt.bar(individual_count.keys(), individual_count.values())
    plt.xlabel('Numbers')
    plt.ylabel('Frequency')
    plt.title('Histogram of Individual Number Occurrences')

    # Histogram for pair counts
    plt.subplot(1, 2, 2)
    pairs = [str(pair) for pair in pair_count.keys()]
    plt.bar(pairs, pair_count.values())
    plt.xlabel('Pairs (num1, num2)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Pair Occurrences')

    plt.tight_layout()
    
    # Save the figure
    plt.savefig(file_path)

    # Close the plot to free memory
    plt.close()

    
def save_dicts(single_dict, pair_dict, dir_path):
    # Construct the file paths
    single_pickle_path = os.path.join(dir_path, "line_attackers_single_count.pkl")
    pair_pickle_path = os.path.join(dir_path, "line_attackers_pair_count.pkl")

    # Save the single_dict to the single_pickle_path
    with open(single_pickle_path, 'wb') as file:
        pickle.dump(single_dict, file)

    # Save the pair_dict to the pair_pickle_path
    with open(pair_pickle_path, 'wb') as file:
        pickle.dump(pair_dict, file)
        
def find_and_process_data(base_path):
    print(f"histogram of line data collection", flush=True)
    counter = 0
    base_path = os.path.abspath(base_path)
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                counter +=1
                if counter % 10 == 0:
                    print(f"Current step {counter}", flush=True)
                results_dir = os.path.join(root, dir_name)
                scenario_single_dict = {}
                scenario_pair_dict = {}
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        print(f"Processing: {sub_dir_path}", flush=True)
                        datas = prep_datas(sub_dir_path)
                        
                        snapshot_single_dict = {}
                        snapshot_pair_dict = {}
                        
                        update_snapshot_dict(snapshot_single_dict,snapshot_pair_dict, datas)
                        save_dicts(snapshot_single_dict, snapshot_pair_dict, sub_dir_path)
                        # plot_and_save_histograms(snapshot_single_dict, snapshot_pair_dict, sub_dir_path)
                        
                        merge_dicts_with_addition(scenario_single_dict, snapshot_single_dict)
                        merge_dicts_with_addition(scenario_pair_dict, snapshot_pair_dict)
                save_dicts(scenario_single_dict, scenario_pair_dict, results_dir)
                        
# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)
