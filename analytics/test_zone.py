from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import random
import seaborn as sns

def plot_bar_number_of_attacks(numbers):
    plt.bar(range(len(numbers)), numbers, color='b')

    # Add a title and labels
    plt.title('Bar Plot of Numbers with Index as X-axis')
    plt.xlabel('Index')
    plt.ylabel('Value')

    # Save the plot to a file
    plt.savefig('bar_plot.png')

    # Optionally, close the plot to free memory
    plt.close()
    
def plot_attack_data(attack_data, output_dir='plots'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Calculate the number of attacks each point has appeared in
    attack_counts = {point: len(snapshots) for point, snapshots in attack_data.items()}

    # Sort attack counts in descending order
    sorted_points = sorted(attack_counts, key=attack_counts.get, reverse=True)
    sorted_attack_counts = [attack_counts[point] for point in sorted_points]

    # Plot 1: Descending order of attacks per point
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(sorted_points)), sorted_attack_counts)
    plt.xlabel('Points (in descending order of attacks)')
    plt.ylabel('Number of Attacks')
    plt.title('Number of Attacks per Point in Descending Order')
    plt.savefig(os.path.join(output_dir, 'attacks_per_point.png'))
    plt.close()

    # Prepare data for heatmap plot
    snapshot_range = 18  # 0 to 18
    points = sorted(attack_data.keys())
    presence_matrix = [[1 if snapshot in attack_data[point] else 0 for point in points] for snapshot in range(snapshot_range)]

    # Plot 2: Presence of Points in Each Snapshot
    plt.figure(figsize=(12, 6))
    sns.heatmap(presence_matrix, xticklabels=False, yticklabels=range(snapshot_range), cmap='Blues', cbar=False)
    plt.xlabel('Points')
    plt.ylabel('Snapshot Number')
    plt.title('Presence of Points in Each Snapshot')
    plt.savefig(os.path.join(output_dir, 'presence_in_snapshots.png'))
    plt.close()
def find_and_process_data(base_path):
    base_path = os.path.abspath(base_path)
    counter = 0
    
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                results_dir = os.path.join(root, dir_name)
                key = ((717, 712, 723, 713, 722, 718), (1361, 1379, 1344, 1192, 1362, 1191)) # ITAL INDIA
                key2 = ((3061, 3080, 3043, 3060, 3062, 3042), (3282, 3281, 3299, 3266, 3283, 3265)) # CAlifornia south mexico
                key3 = ((1442, 1441, 3873, 1421, 1420, 3874), (3281, 3298, 3265, 3280, 3282, 3264)) # CALIFORNIA BRITIAN/Franch
                list_keys = [key,key2,key3]
                main_dict = {key: {} for key in list_keys}
                num_of_atks = {key: [] for key in list_keys}
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        counter +=1
                        if counter % 5 == 0:
                            print(f"Current step: {counter}", flush=True)
                        loader = SimulationDataLoader(sub_dir_path)
                        # loader.load_data("Grid")
                        loader.load_data("ZAtkS")
                        # grid_pos = loader.data_cache["Grid"][0]
                        # key_list.append(compute(grid_pos,42))
                        total_attacks = 0
                        total_attack_dict = {}
                        attack_datas = loader.data_cache["ZAtkS"][0]
                        # grid_datas = loader.data_cache["Grid"][0] 
                        for k in list_keys:
                            if k not in attack_datas:
                                continue
                            data = attack_datas[k]
                            atkflowset = data.atkflowset
                            numbers_set = list({num for (num1, num2), _ in atkflowset for num in (num1, num2)})
                            num_of_atks[k].append(len(numbers_set))
                            for num in numbers_set:
                                if num in main_dict[k]:
                                    main_dict[k][num].append(int(sub_dir_name))
                                else:
                                    main_dict[k][num] = [int(sub_dir_name)]
                for keyp, list_num in num_of_atks.items():
                    plot_bar_number_of_attacks(list_num)
                    print()
                # for keyp, dict in main_dict.items():
                #     plot_attack_data(dict)
                #     print()
                return #todo add how much attack
                                
                        

# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)


