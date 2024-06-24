import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# Haversine distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

# Define the function
def find_nearest_points(datas, csv_path):
    # Load the CSV file
    city_pairs_df = pd.read_csv(csv_path)
    
    # Find the nearest point in `datas` for both cities in each row of the CSV
    nearest_points = []

    for index, row in city_pairs_df.iterrows():
        city1_lat = row['Latitude1']
        city1_lon = row['Longitude1']
        city2_lat = row['Latitude2']
        city2_lon = row['Longitude2']
        
        min_distance_city1 = float('inf')
        nearest_key_city1 = None
        min_distance_city2 = float('inf')
        nearest_key_city2 = None
        
        for key in datas:
            distance_city1 = haversine(city1_lat, city1_lon, datas[key].lat, datas[key].lon)
            if distance_city1 < min_distance_city1:
                min_distance_city1 = distance_city1
                nearest_key_city1 = key
            
            distance_city2 = haversine(city2_lat, city2_lon, datas[key].lat, datas[key].lon)
            if distance_city2 < min_distance_city2:
                min_distance_city2 = distance_city2
                nearest_key_city2 = key
        
        nearest_points.append((nearest_key_city1, nearest_key_city2))

    return nearest_points

def plot_number_appearances(tuple_list, save_dir, filename):
    from collections import Counter
    import matplotlib.pyplot as plt
    import os

    # Flatten the list of tuples and count appearances
    numbers = [num for tup in tuple_list for num in tup]
    count = Counter(numbers)

    # Create the plot
    plt.figure(figsize=(12, 8))
    plt.bar(count.keys(), count.values(), color='blue')
    plt.xlabel('Numbers')
    plt.ylabel('Appearances')
    plt.title('Number of Appearances')

    # Set limits for better visibility
    plt.xlim(0, max(count.keys()) + 10)
    plt.ylim(0, max(count.values()) + 10)

    plt.xticks(rotation=45)  # Rotate x labels if too many
    plt.tight_layout()  # Adjust layout to fit everything

    # Save the plot to the specified directory
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    plt.savefig(os.path.join(save_dir, filename))
    plt.close()

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from math import radians, sin, cos, sqrt, atan2


# Define the function
def plot_gdp_on_map(datas, gdp_csv_path):
    # Load the GDP data from the CSV file
    gdp_df = pd.read_csv(gdp_csv_path)
    
    # Ensure the necessary columns are present
    if 'latitude' not in gdp_df.columns or 'longitude' not in gdp_df.columns or 'Official est. GDP(billion US$)' not in gdp_df.columns:
        raise ValueError("The GDP CSV file must contain 'latitude', 'longitude', and 'Official est. GDP(billion US$)' columns.")
    
    # Convert GDP to numeric, removing any commas
    gdp_df['Official est. GDP(billion US$)'] = gdp_df['Official est. GDP(billion US$)'].str.replace(',', '').astype(float)
    
    # Aggregate GDP values for each unique point
    gdp_aggregated = gdp_df.groupby(['latitude', 'longitude'])['Official est. GDP(billion US$)'].sum().reset_index()

    # Find the nearest point in `datas` for each point in the aggregated GDP data
    nearest_points = []
    for index, row in gdp_aggregated.iterrows():
        point_lat = row['latitude']
        point_lon = row['longitude']
        
        min_distance = float('inf')
        nearest_key = None
        
        for key in datas:
            distance = haversine(point_lat, point_lon, datas[key].lat, datas[key].lon)
            if distance < min_distance:
                min_distance = distance
                nearest_key = key
        
        nearest_points.append((datas[nearest_key].lat, datas[nearest_key].lon, row['Official est. GDP(billion US$)']))
    
    # Create a DataFrame for plotting
    plot_data = pd.DataFrame(nearest_points, columns=['latitude', 'longitude', 'gdp'])
    geometry = [Point(xy) for xy in zip(plot_data['longitude'], plot_data['latitude'])]
    gdf = gpd.GeoDataFrame(plot_data, geometry=geometry)

    # World basemap
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Plot
    fig, ax = plt.subplots(figsize=(15, 10))
    world.plot(ax=ax, color='lightgray')
    gdf.plot(ax=ax, color='blue', markersize=gdf['gdp'] / 100)  # Scale the marker size based on GDP

    # Customize the plot
    plt.title('GDP Distribution on World Map')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.savefig("/home/roeeidan/icarus_framework/analytics/outputs/gdp_map.png")
    plt.close()
    
    
def plot_point_pairs(datas, result, output_path):
    import numpy as np
    fig, ax = plt.subplots(figsize=(15, 10))
    m = Basemap(projection='merc', llcrnrlat=-60, urcrnrlat=85, llcrnrlon=-180, urcrnrlon=180, resolution='c')

    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary(fill_color='aqua')
    m.fillcontinents(color='lightgreen', lake_color='aqua')

    # Generate distinct colors for each line
    colors = plt.cm.rainbow(np.linspace(0, 1, len(result)))

    for idx, (key1, key2) in enumerate(result):
        lat1, lon1 = datas[key1].lat, datas[key1].lon
        lat2, lon2 = datas[key2].lat, datas[key2].lon

        # Convert latitude and longitude to map projection coordinates
        x1, y1 = m(lon1, lat1)
        x2, y2 = m(lon2, lat2)

        # Draw a line between points
        m.drawgreatcircle(lon1, lat1, lon2, lat2, color=colors[idx], linewidth=2)

    plt.title("Point Pairs on World Map")
    plt.savefig(output_path)
    plt.close()