# from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_line(data_dict):
    sorted_values = sorted(data_dict.values(), reverse=True)
    # Step 2: Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_values)
    plt.ylabel('Values')
    plt.title('Distribution of Dictionary Values in Descending Order')
    plt.savefig('/home/roeeidan/icarus_framework/analytics/grid_user_distrib.png')
    plt.close()
    
def plot_grorups(data_dict):
    sorted_values = sorted(data_dict.values(), reverse=True)

    # Step 2: Divide the sorted values into batches of 100
    batch_size = 100
    batches = [sorted_values[i:i + batch_size] for i in range(0, len(sorted_values), batch_size)]

    # Step 3: Calculate the average for each batch
    batch_averages = [np.mean(batch) for batch in batches]

    # Step 4: Plot the averages as a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(batch_averages)), batch_averages)
    plt.xlabel('Batch Number')
    plt.ylabel('Average Value')
    plt.title('Average Values in Each Batch of 100')
    plt.xticks(range(len(batch_averages)), [f'Batch {i+1}' for i in range(len(batch_averages))], rotation=90)
    plt.grid(axis='y')
    plt.savefig('/home/roeeidan/icarus_framework/analytics/grid_user_distrib2.png')
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
                        file_name = "zone_attackers_single_count.pkl"
                        file_path = os.path.join(sub_dir_path, file_name)
                        if not os.path.isfile(file_path):
                            continue
                        counter +=1
                        if counter % 5 == 0:
                            print(f"Current step: {counter}", flush=True)
                        with open(file_path, 'rb') as file:
                            data_dict = pickle.load(file)
                        plot_grorups(data_dict)
                        return



# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)