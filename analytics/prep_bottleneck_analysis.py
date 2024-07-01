
import os
import pickle
import bz2
from collections import defaultdict

import sys
current_script_path = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_script_path, os.pardir)
sys.path.append(os.path.normpath(base_directory))

# Assuming create_grid_histogram is defined elsewhere
def create_grid_histogram(scenarios_paths, output_folder):
    general_histogram = defaultdict(lambda: defaultdict(int))
    counter = 0
    for scenario_path in scenarios_paths:
        # Construct the path to the ZoneBottlePhase.pkl.bz2 file
        file_path = os.path.join(scenario_path, 'ZoneBottlePhase.pkl.bz2')

        if os.path.exists(file_path):
            with bz2.BZ2File(file_path, 'rb') as f:
                data = pickle.load(f)[0]
            counter +=1
            # Assuming data is a dict where values are ZoneBottleNeckInfo objects
            for key, value in data.items():
                if value is None:
                    continue
                for grid_key, count in value.GridStartAppearanceCounter.items():
                    general_histogram[key][grid_key] += count

    # Save the general histogram as a pickle file
    histogram_pickle_file = os.path.join(output_folder, 'general_histogram.pkl')
    with open(histogram_pickle_file, 'wb') as f:
        pickle.dump(dict(general_histogram), f)
    
    print(f"General histogram saved to {histogram_pickle_file}")

def process_intervals(intervals, base_output_directory):
    for interval in intervals:
        start_index, end_index, paths = interval
        folder_name = f"{start_index}_{end_index}"
        output_folder = os.path.join(base_output_directory, folder_name)
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created directory: {output_folder}")
            create_grid_histogram(paths, output_folder)
            paths_pickle_file = os.path.join(output_folder, 'scenarios_paths.pkl')
            with open(paths_pickle_file, 'wb') as f:
                pickle.dump(paths, f)

def create_intervals(base_path, interval):
    # List all subdirectories and sort them numerically
    subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    subdirs.sort(key=lambda x: int(x))  # Sort directories numerically

    intervals = []
    start_index = 0
    end_index = interval - 1
    paths = []

    for subdir in subdirs:
        subdir_int = int(subdir)
        if subdir_int > end_index:
            intervals.append([start_index, end_index, paths])
            start_index = end_index + 1
            end_index = start_index + interval - 1
            paths = []
        paths.append(os.path.join(base_path, subdir))

    # Append the last interval
    if paths:
        intervals.append([start_index, end_index, paths])

    return intervals

base_directory = "/dt/shabtaia/DT_Satellite/icarus_data/sim_intervals_30s/"
output_base_directory = "/dt/shabtaia/DT_Satellite/icarus_data/sim_intervals_30s_range/"
interval_seconds = 3600  # Set your interval here

# Assuming create_intervals function is already defined as previously provided
intervals = create_intervals(base_directory, interval_seconds)

# Process the intervals and create necessary directories
process_intervals(intervals, output_base_directory)
