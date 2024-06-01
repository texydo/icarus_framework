from sim_data_loader import SimulationDataLoader
import os
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from collections import defaultdict

def load_and_aggregate_data(base_path):
    combined_importance_dict = defaultdict(int)

    # Walk through the directory to find all results subdirectories
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                results_dir = os.path.join(root, dir_name)
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        pkl_file_path = os.path.join(sub_dir_path, 'zone_attack_grid_count.pkl')
                        if os.path.exists(pkl_file_path):
                            with open(pkl_file_path, 'rb') as f:
                                importance_dict = pickle.load(f)
                                for key, value in importance_dict.items():
                                    combined_importance_dict[key] += value
    return combined_importance_dict

def scale_marker_size(importance, min_importance, max_importance):
    normalized_importance = (importance - min_importance) / (max_importance - min_importance)
    return (normalized_importance ** 2.3) * 10  # Example scaling

def plot_points_on_map(importance_dict, coords_dict):
    min_importance = min(importance_dict.values())
    max_importance = max(importance_dict.values())

    plt.figure(figsize=(10, 5))
    map = Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180, lat_ts=20, resolution='c')
    map.drawcoastlines()
    map.drawcountries()
    map.fillcontinents(color='coral', lake_color='aqua')
    map.drawmapboundary(fill_color='aqua')

    for point_id, importance in importance_dict.items():
        if point_id in coords_dict:
            lon, lat = coords_dict[point_id].lon, coords_dict[point_id].lat
            x, y = map(lon, lat)
            map.plot(x, y, 'ko', markersize=scale_marker_size(importance, min_importance, max_importance))

    plt.title('Map of Points')
    plt.show()
    plt.savefig('/home/roeeidan/icarus_framework/analytics/total_zone_map_of_points.png', dpi=300)

# Main Execution
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
combined_importance_dict = load_and_aggregate_data(base_path)

loader = SimulationDataLoader("/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData/1/results/0/")
loader.load_data("Grid")
coords_dict = loader.data_cache["Grid"][0]

plot_points_on_map(combined_importance_dict, coords_dict)
