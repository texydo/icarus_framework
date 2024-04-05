#  2020 Tommaso Ciussani and Giacomo Giuliari

import os
import torch
from torch_geometric.data import Data
from typing import List

from icarus_simulator.strategies.training_data_creation.base_training_data import (
    BaseDataCreation,
)
from icarus_simulator.structure_definitions import GridPos, BwData
from icarus_simulator.utils import get_ordered_idx


# Computes a sampled traffic matrix. IMPORTANT: this strategy assumes that all paths are symmetrical, and path_data
# only stores the ordered pairs for space and performance reasons.
class BasicTrainingDataStrat(BaseDataCreation):
    def __init__(self, **kwargs):
        super().__init__()
        # TODO change this
        self.store_path = "/dt/shabtaia/DT_Satellite/icarus_data/graphs/basic"
        if len(kwargs) > 0:
            pass  # Appease the unused param inspection
    @property
    def name(self) -> str:
        return "BasicTrainingDataStrat"

    @property
    def param_description(self) -> str:
        return ""
    
    def process_edges_numeric(self, edges):
        edge_index_list = []
        edge_attr_list = []
        processed_nodes = set()  # Keep track of nodes for which self-loop has been added

        for (node_start, node_end), edge_obj in edges.items():
            # Convert edges marked with -1 to self-loops and ensure they are added only once
            if -1 in [node_start, node_end]:
                real_node_id = node_start if node_end == -1 else node_end
                if real_node_id not in processed_nodes:
                    edge_index_list.append([real_node_id, real_node_id])
                    edge_attr_list.append([edge_obj.idle_bw, edge_obj.capacity])
                    processed_nodes.add(real_node_id)
            else:
                edge_index_list.append([node_start, node_end])
                edge_attr_list.append([edge_obj.idle_bw, edge_obj.capacity])

        # Convert the lists to PyTorch tensors
        edge_index = torch.tensor(edge_index_list, dtype=torch.long).t().contiguous()
        edge_attr = torch.tensor(edge_attr_list, dtype=torch.float)

        return edge_index, edge_attr
    
    def process_nodes(self, nodes):
        # Assuming node indices are continuous and start from 1
        # Adjust based on your actual node indexing
        node_attr_list = []
        for i in sorted(nodes):
            node_obj = nodes[i]
            node_attr_list.append([node_obj.lon, node_obj.lat])
        x = torch.tensor(node_attr_list, dtype=torch.float)
        return x
    
    
    def compute(self, grid_pos: GridPos, bw_data: BwData, y: int):
        edge_index, edge_attr = self.process_edges_numeric(bw_data)
        x = self.process_nodes(grid_pos)
        data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=[y])
        save_graph(data,self.store_path)


def get_largest_graph_id(folder_path):
    largest_id = 0
    found = False
    for filename in os.listdir(folder_path):
        if filename.startswith("graph_") and filename.endswith(".pt"):
            try:
                graph_id = int(filename.split("_")[1].split(".")[0])
                largest_id = max(largest_id, graph_id)
                found = True
            except ValueError:
                # Skip files with invalid format
                continue
    if not found:
        return 0
    return largest_id
    
def save_graph(data, path):
    """
    Saves a single graph to a file.
    
    Parameters:
    - data: The Data object to save.
    - path: Base directory to save the graph.
    - graph_id: An identifier for the graph.
    """
    graph_id = get_largest_graph_id(path) + 1
    file_name = f"graph_{graph_id}.pt"
    file_path = os.path.join(path, file_name)
    torch.save(data, file_path)