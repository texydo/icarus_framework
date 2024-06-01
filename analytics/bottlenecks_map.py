import os
from sim_data_loader import SimulationDataLoader
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

def initialize_map():
    """Initialize a Basemap instance for plotting."""
    plt.figure(figsize=(10, 8))
    m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=70, llcrnrlon=-180, urcrnrlon=180, resolution='i')
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    return m

def draw_line_on_map(m, lon1, lat1, lon2, lat2):
    """Draw a line between two points on a given map."""
    x1, y1 = m(lon1, lat1)
    x2, y2 = m(lon2, lat2)
    m.plot([x1, x2], [y1, y2], marker='o', markersize=1.5, linestyle='-', color='r')
    plt.draw()

def find_and_process_data(base_path):
    base_path = os.path.abspath(base_path)
    map_obj = initialize_map()

    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == 'results':
                results_dir = os.path.join(root, dir_name)
                for sub_dir_name in os.listdir(results_dir):
                    sub_dir_path = os.path.join(results_dir, sub_dir_name)
                    if os.path.isdir(sub_dir_path):
                        image_save_path = os.path.join(sub_dir_path, 'bottleneck_map.png')
                        if os.path.exists(image_save_path):
                            print(f"Skipping {sub_dir_path} as bottleneck_map.png already exists.", flush=True)
                            continue
                        print(f"Processing: {sub_dir_path}", flush=True)
                        loader = SimulationDataLoader(sub_dir_path)
                        loader.load_data("ZAtk")
                        loader.load_data("LSN")
                        datas = loader.data_cache["ZAtk"][0]
                        geo_location_data = loader.data_cache["LSN"][0]
                        
                        map_obj = initialize_map()
                        
                        for data in datas.values():
                            if data is None:
                                continue
                            for (num1, num2) in data.bottlenecks:
                                geo1 = geo_location_data.get(num1)
                                geo2 = geo_location_data.get(num2)
                                if geo1 and geo2:
                                    draw_line_on_map(map_obj, geo1.lon, geo1.lat, geo2.lon, geo2.lat)
                                # Save the updated map after processing each subdirectory
                        plt.savefig(image_save_path)
                        plt.close()
                        print(f"Map saved at: {image_save_path}", flush=True)

# Usage
base_path = '/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData'
find_and_process_data(base_path)
