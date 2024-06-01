from sim_data_loader import SimulationDataLoader
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Load your data
with open('/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData/1/results/0/zone_attack_grid_count.pkl', 'rb') as f:
    importance_dict = pickle.load(f)


loader = SimulationDataLoader("/dt/shabtaia/DT_Satellite/icarus_data/ContinuousData/15/results/10/")
loader.load_data("Grid")
coords_dict = loader.data_cache["Grid"][0]

min_importance = min(importance_dict.values())
max_importance = max(importance_dict.values())

# Function to normalize and scale marker sizes
def scale_marker_size(importance):
    # Normalize importance to a 0-1 scale
    normalized_importance = (importance - min_importance) / (max_importance - min_importance)
    # Scale to range, e.g., from 2 to 20
    return (normalized_importance ** 2.3) * 10

# Set up the plot
plt.figure(figsize=(10, 5))
map = Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80, llcrnrlon=-180, urcrnrlon=180, lat_ts=20, resolution='c')

# Draw map details
map.drawcoastlines()
map.drawcountries()
map.fillcontinents(color='coral', lake_color='aqua')
map.drawmapboundary(fill_color='aqua')

# Plot each point with scaled marker size
for point_id, importance in importance_dict.items():
    if point_id in coords_dict:
        lon, lat = coords_dict[point_id].lon, coords_dict[point_id].lat
        x, y = map(lon, lat)
        map.plot(x, y, 'ko', markersize=scale_marker_size(importance))

plt.title('Map of Points')
plt.show()
plt.savefig('/home/roeeidan/icarus_framework/analytics/zone_map_of_points.png', dpi=300)