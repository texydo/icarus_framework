#  2020 Tommaso Ciussani and Giacomo Giuliari
from typing import Tuple, List
import os
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

from icarus_simulator.strategies.zone_select.base_zone_select_strat import (
    BaseZoneSelectStrat,
)
from icarus_simulator.structure_definitions import GridPos

dirname = os.path.dirname(__file__)
strategies_dirname = os.path.split(dirname)[0]
library_dirname = os.path.split(strategies_dirname)[0]
data_dirname = os.path.join(library_dirname, "data")
PAIRS_FILE: str = os.path.join(data_dirname, "city_pairs.csv")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance

class LoadZoneStrat(BaseZoneSelectStrat):
    def __init__(self, dataset_file: str = None, **kwargs):
        super().__init__()
        if dataset_file is None:
            self.dataset = PAIRS_FILE
        else:
            self.dataset = dataset_file
        if len(kwargs) > 0:
            pass  # Appease the unused param inspection

    @property
    def name(self) -> str:
        return "slct_zone"

    @property
    def param_description(self) -> str:
        return None

    def compute(self, grid_pos: GridPos) -> List[Tuple[int, int]]:
        # Load the CSV file
        city_pairs_df = pd.read_csv(self.dataset)
        
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
            
            for key in grid_pos:
                distance_city1 = haversine(city1_lat, city1_lon, grid_pos[key].lat, grid_pos[key].lon)
                if distance_city1 < min_distance_city1:
                    min_distance_city1 = distance_city1
                    nearest_key_city1 = key
                
                distance_city2 = haversine(city2_lat, city2_lon, grid_pos[key].lat, grid_pos[key].lon)
                if distance_city2 < min_distance_city2:
                    min_distance_city2 = distance_city2
                    nearest_key_city2 = key
            
            nearest_points.append((nearest_key_city1, nearest_key_city2))

        return nearest_points
