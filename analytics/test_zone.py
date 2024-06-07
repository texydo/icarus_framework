from sim_data_loader import SimulationDataLoader
import os
from pathlib import Path
import pickle

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
                        loader.load_data(";Atk")
                        dict_detectability = []
                        if "ZAtk" in loader.data_cache:
                            datas = loader.data_cache["ZAtk"][0]
                            for data in datas.values():
                                if data is None:
                                    continue
                                detectability = data.detectability
                                dict_detectability.append(detectability)
                        import matplotlib.pyplot as plt
                        plt.hist(dict_detectability, bins=50, edgecolor='black', alpha=0.7)
                        # Add title and labels
                        plt.title('Distribution of Numbers')
                        plt.xlabel('Number')
                        plt.ylabel('Frequency')
                        # Show the plot
                        plt.savefig('/home/roeeidan/icarus_framework/analytics/distribution_plot.png')
                        plt.close()


# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)