import os
import time
import compress_pickle

import sys
current_script_path = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_script_path, os.pardir)
sys.path.append(os.path.normpath(base_directory))

class SimulationDataLoader:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_cache = {}  # Cache to store loaded data
        self.verbose: bool = False

    def load_data(self, data_type):
        # Check cache first
        if data_type in self.data_cache:
            if self.verbose:
                print(f"Loading {data_type} from cache")
            return
        
        # Maps data type to the respective file name
        file_map = {
            "LSN": "LSN.pkl.bz2",
            "LAtk": "LAtk.pkl.bz2",
            "ZAtk": "ZAtk.pkl.bz2",
            "Routes": "Routes.pkl.bz2",
            "Cover": "Cover.pkl.bz2",
            "Bw": "Bw.pkl.bz2",
            "Grid": "Grid.pkl.bz2",
            "Edges": "Edges.pkl.bz2",
            "ZAtkS":"ZAtkS.pkl.bz2"
        }
        
        # Check if the data_type is valid
        if data_type not in file_map:
            print(f"Data type '{data_type}' is not recognized.")
            return
        
        # Build the file path
        file_path = os.path.join(self.base_dir, file_map[data_type])
        
        # Check if the file exists
        if not os.path.isfile(file_path):
            print(f"No file found for {data_type} at {file_path}")
            return
        
        # Load the data
        start = time.time()
        if self.verbose:
            print(self.verbose)
            print(f"Reading {data_type} from file", flush=True)
        
        result = compress_pickle.load(
            file_path, compression="bz2", set_default_extension=False
        )
        if self.verbose:
            print(f"Read {data_type} in {time.time() - start} seconds", flush=True)
        
        # Store to cache
        self.data_cache[data_type] = result