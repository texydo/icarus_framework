#  2020 Tommaso Ciussani and Giacomo Giuliari
import random
import numpy as np
from typing import List

from icarus_simulator.strategies.traffic_select_attack_simulation.base_attack_select_simulation import (
    BaseAttackSelectSimulation,
)
from icarus_simulator.structure_definitions import PathData, PathIdCost, AttackFlowsetData
from icarus_simulator.utils import get_ordered_idx


# Computes a sampled traffic matrix. IMPORTANT: this strategy assumes that all paths are symmetrical, and path_data
# only stores the ordered pairs for space and performance reasons.
class AttackTrafficSelectStrat(BaseAttackSelectSimulation):
    def __init__(self, **kwargs):
        super().__init__()
        if len(kwargs) > 0:
            pass  # Appease the unused param inspection

    @property
    def name(self) -> str:
        return "AttackTrafficSelect"

    @property
    def param_description(self) -> str:
        return ""

        
    def compute(self, path_data: PathData, atkflowset: AttackFlowsetData, traffic_paths: PathIdCost) -> List[PathIdCost]:
        path_ids = []
        for value in atkflowset:
            ord_value = get_ordered_idx((value[0][0], value[0][1]))[0]
            if ord_value not in path_data or len(path_data[ord_value]) == 0:
                print(f"error {ord_value}")
                continue
            data_amount = value[1]
            path_ids.append((ord_value[0], ord_value[1], 0, data_amount))
            
        path_ids.extend(traffic_paths)
        return path_ids
