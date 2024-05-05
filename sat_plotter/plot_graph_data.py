import os
import torch
from torch_geometric.data import Data
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go

# Step 1: Define the directory path and find .pt files
def find_pt_files(folder_path):
    """Find all .pt files in the specified folder."""
    pt_files = [f for f in os.listdir(folder_path) if f.endswith('.pt')]
    return pt_files

# Step 2: Load a graph file using PyTorch Geometric
def load_graph(filepath):
    """Load a PyTorch Geometric graph from a .pt file."""
    graph = torch.load(filepath)
    return graph

# Step 3: Extract necessary data from the graph
def extract_data(data):
    """Extract positions, edges, and edge attributes from the graph."""
    positions = {i: (data.x[i][0].item(), data.x[i][1].item()) for i in range(data.x.size(0))}
    edges = [(data.edge_index[0][i].item(), data.edge_index[1][i].item()) for i in range(data.edge_index.size(1))]
    edge_attributes = {(data.edge_index[0][i].item(), data.edge_index[1][i].item()): 
                       {'current_bandwidth': data.edge_attr[i][0].item(), 
                        'max_bandwidth': data.edge_attr[i][1].item()} 
                       for i in range(data.edge_attr.size(0))}
    return positions, edges, edge_attributes

# Step 4: Draw the network on a 2D Earth map
def draw_network_on_map_plotly(positions, edges, edge_attributes):
    satellites = go.Scattergeo(
        lon=[positions[id][0] for id in positions],
        lat=[positions[id][1] for id in positions],
        mode='markers',
        marker=dict(size=4, color='black'),
        name='Satellites'
    )
    lon=[positions[id][0] for id in positions]
    print(len(lon))
    lat=[positions[id][1] for id in positions]
    print(len(lat))
    connection_lines = []
    for edge in edges:
        sat1_id, sat2_id = edge
        lon1, lat1 = positions[sat1_id]
        lon2, lat2 = positions[sat2_id]

        # Adjusting this line to modify width based on bandwidth usage
        line_width = edge_attributes[edge]['current_bandwidth'] / edge_attributes[edge]['max_bandwidth'] * 2  # Example calculation, adjust as needed

        connection_lines.append(
            go.Scattergeo(
                lon=[lon1, lon2],
                lat=[lat1, lat2],
                mode='lines',
                line=dict(width=line_width, color='gray'),
                showlegend=False
            )
        )

    fig = go.Figure(data=[satellites] + connection_lines)

    fig.update_geos(
        projection_type='mercator',
        landcolor='white',
        lakecolor='white',
        oceancolor='white',
        coastlinecolor='black',
        countrycolor='black',
    )
    fig.update_layout(
        title='Satellite Network on Simplified Earth Map',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    # print(len(positions))
    fig.show()
    
# Main execution block
folder_path = '/dt/shabtaia/DT_Satellite/icarus_data/graphs/weightedDetectability/raw/'
pt_files = find_pt_files(folder_path)
if pt_files:
    selected_file_path = os.path.join(folder_path, pt_files[12])  # Select the first file for this example
    data = load_graph(selected_file_path)
    positions, edges, edge_attributes = extract_data(data)
    draw_network_on_map_plotly(positions, edges, edge_attributes)
else:
    print("No .pt files found in the specified folder.")
