#  2020 Tommaso Ciussani and Giacomo Giuliari
import random
import numpy as np
from typing import List

from icarus_simulator.strategies.traffic_select_simulation.base_bw_select_simulation import (
    BaseBwSelectSimulation,
)
from icarus_simulator.structure_definitions import GridPos, PathData, PathIdCost
from icarus_simulator.utils import get_ordered_idx


# Computes a sampled traffic matrix. IMPORTANT: this strategy assumes that all paths are symmetrical, and path_data
# only stores the ordered pairs for space and performance reasons.
class RandomTrafficSelectStrat(BaseBwSelectSimulation):
    def __init__(self, actual_quanta: int, max_data_per_user: int, average_data_per_user: int, **kwargs):
        super().__init__()
        self.actual_quanta = actual_quanta
        self.max_data_per_user = max_data_per_user
        self.average_data_per_user = average_data_per_user
        if len(kwargs) > 0:
            pass  # Appease the unused param inspection

    @property
    def name(self) -> str:
        return "RandomTrafficSamp"

    @property
    def param_description(self) -> str:
        return f"{self.actual_quanta}"

    def calculate_weighted_random_data_amount(self, grid_pos: GridPos, ord_sample):
        weight_a = grid_pos[ord_sample[0]].weight
        weight_b = grid_pos[ord_sample[1]].weight
        weighted_avg_weight = (weight_a + weight_b) / 2
        
        # Gamma distribution
        k = 1.1
        theta = self.average_data_per_user / k
        adjusted_theta = theta * (1 + (self.max_data_per_user / self.average_data_per_user))
        data_amount = np.random.gamma(k, adjusted_theta)
        
        # reorgnize amount
        data_amount = data_amount * weighted_avg_weight
        if data_amount > 2:
            data_amount = int(data_amount)
        else:
            data_amount = round(data_amount, 2)
        data_amount = min(data_amount, self.max_data_per_user)
        
        return data_amount
    
    def get_random_samples(self, grid_pos):
        # Generate a random list of selections considering the weights
        weights = [val.weight for val in grid_pos.values()]
        keys = list(grid_pos.keys())
        samples = random.choices(keys, weights, k=self.actual_quanta * 2)

        # Function to randomly select a different item based on weights, excluding a specific item
        def get_different_item(exclude_item):
            temp_keys = [k for k in keys if k != exclude_item]
            temp_weights = [weight for key, weight in zip(keys, weights) if key != exclude_item]
            return random.choices(temp_keys, temp_weights, k=1)[0]

        # Iterate over the list in pairs
        for i in range(0, self.actual_quanta * 2, 2):
            # If the two items of the pair are the same, replace the second one
            while samples[i] == samples[i + 1]:
                samples[i + 1] = get_different_item(samples[i])

        return samples
        
    def compute(self, grid_pos: GridPos, path_data: PathData) -> List[PathIdCost]:
        # Sample communication pairs
        # random.seed("BGU")
        # samples = random.choices(
        #     list(grid_pos.keys()),
        #     [val.weight for val in grid_pos.values()],
        #     k=self.actual_quanta * 2,
        # )
        samples = self.get_random_samples(grid_pos)
        
        # If the pair exists, sample a suitable path
        path_ids = []
        for i in range(0, len(samples), 2):
            ord_sample = get_ordered_idx((samples[i], samples[i + 1]))[0]
            # If the sample is not in the paths, or there is no path between the pair, the sample is dropped
            if ord_sample not in path_data or len(path_data[ord_sample]) == 0:
                continue
            lbset_size = len(path_data[ord_sample])
            id_in_lbset = random.randrange(0, lbset_size)
            data_amount = self.calculate_weighted_random_data_amount(grid_pos, ord_sample)
            path_ids.append((ord_sample[0], ord_sample[1], id_in_lbset, data_amount))
        return path_ids
