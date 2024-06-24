import pandas as pd
import geopy.distance
import matplotlib.pyplot as plt
import random
from mpl_toolkits.basemap import Basemap
import numpy as np
import random

def normalize_weights(cities_df):
    # Convert population and GDP columns to numerical values
    cities_df['Population_weight'] = cities_df['Metropolitian Population'].str.replace(',', '').astype(float)
    cities_df['GDP_weight'] = cities_df['Official est. GDP(billion US$)'].str.replace(',', '').astype(float)

    # Calculate total population and GDP
    max_pop = cities_df['Population_weight'].max()
    total_population = cities_df['Population_weight'].sum()
    total_gdp = cities_df['GDP_weight'].sum()

    # Normalize weights based on different criteria
    cities_df['Normalized_combined_weight'] = (cities_df['Population_weight'] / total_population) + (
                cities_df['GDP_weight'] / total_gdp)
    cities_df['Normalized_population_weight'] = cities_df['Population_weight'] / total_population
    cities_df['Normalized_gdp_weight'] = cities_df['GDP_weight'] / total_gdp

    return cities_df


# Function to select a random city based on different normalized weights
def select_random_city(weighted_df):
    # Randomly choose one of the three cases
    
    # choice = np.random.choice(['gdp'])
    choice = np.random.choice(['combined','population','gdp'])
    if choice == 'combined':
        return weighted_df.sample(weights=weighted_df['Normalized_combined_weight'], replace=True).iloc[0]
    elif choice == 'population':
        return weighted_df.sample(weights=weighted_df['Normalized_population_weight'], replace=True).iloc[0]
    else:  # choice == 'gdp'
        return weighted_df.sample(weights=weighted_df['Normalized_gdp_weight'], replace=True).iloc[0]


# Function to calculate the distance between two coordinates
def calculate_distance(coord1, coord2):
    return geopy.distance.geodesic(coord1, coord2).km


# Function to generate weighted pairs of cities
def weighted_city_pairs(cities_df, num_pairs_amount, min_distance_km):
    cities_df = normalize_weights(cities_df)

    city_pairs = []

    while len(city_pairs) < num_pairs_amount:
        city1 = select_random_city(cities_df)
        city2 = select_random_city(cities_df)

        coord1 = (city1['latitude'], city1['longitude'])
        coord2 = (city2['latitude'], city2['longitude'])

        distance = calculate_distance(coord1, coord2)

        if distance >= min_distance_km:
            city_pairs.append((city1['Metropolitian Area/City'], city2['Metropolitian Area/City'], distance))

    return city_pairs


# Function to create a CSV file with city pairs
def create_city_pairs_csv(city_pairs, cities_df, output_file):
    city_pairs_data = []

    for pair in city_pairs:
        city1, city2, distance = pair
        city1_data = cities_df[cities_df['Metropolitian Area/City'] == city1].iloc[0]
        city2_data = cities_df[cities_df['Metropolitian Area/City'] == city2].iloc[0]

        city_pairs_data.append([
            city1, city1_data['latitude'], city1_data['longitude'],
            city2, city2_data['latitude'], city2_data['longitude'],
            distance
        ])

    city_pairs_df = pd.DataFrame(city_pairs_data, columns=[
        'City1', 'Latitude1', 'Longitude1', 'City2', 'Latitude2', 'Longitude2', 'Distance_km'
    ])

    city_pairs_df.to_csv(output_file, index=False)


# Function to plot city pairs from CSV on a world map
def plot_city_pairs_from_csv(input_file):
    city_pairs_df = pd.read_csv(input_file)

    plt.figure(figsize=(14, 10))
    m = Basemap(projection='mill', llcrnrlat=-60, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180, resolution='c')
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='lightgray', lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    for index, row in city_pairs_df.iterrows():
        lat1, lon1 = row['Latitude1'], row['Longitude1']
        lat2, lon2 = row['Latitude2'], row['Longitude2']

        # Plot great circle line with a random color
        m.drawgreatcircle(lon1, lat1, lon2, lat2, linewidth=2,
                          color=(random.random(), random.random(), random.random()))

        x1, y1 = m(lon1, lat1)
        x2, y2 = m(lon2, lat2)

        # Plot city points
        m.scatter([x1, x2], [y1, y2], color='black', s=10)

        # Annotate cities

    plt.title('City Pairs on World Map')
    plt.show()

# Load the dataset
file_path = 'icarus_simulator/data/cities_by_gdp.csv'
cities_df = pd.read_csv(file_path)

# Normalize weights
cities_df = normalize_weights(cities_df)

# Generate 10 pairs of cities with a minimum distance of 1000 km
num_pairs = 3500
min_distance_km = 1000
city_pairs = weighted_city_pairs(cities_df, num_pairs, min_distance_km)

# Define the output CSV file path
output_file = 'configurations/setup_attack_pairs/city_pairs.csv'

# Create the CSV file with the city pairs
create_city_pairs_csv(city_pairs, cities_df, output_file)

# Plot the city pairs from the CSV
plot_city_pairs_from_csv(output_file)
