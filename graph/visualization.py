from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from PIL import Image
import folium
from .core import CityGraph

def visualize_graph(
    city_graph: CityGraph,
    highlight_path: Optional[List[str]] = None,
    time_of_day: Optional[str] = None,
    congestion_info: bool = False
) -> Image.Image:
    """Visualize the graph with optional path highlighting"""
    plt.figure(figsize=(14, 10))
    pos = {node: (city_graph.node_coords[node][1], city_graph.node_coords[node][0]) 
           for node in city_graph.graph.nodes()}
    
    # Prepare edge weights
    edges = list(city_graph.graph.edges())
    weights = []
    for u, v in edges:
        weight = _get_visualization_weight(city_graph, u, v, time_of_day)
        weights.append(weight)
    
    max_weight = max(weights) if weights else 1
    norm = mcolors.Normalize(vmin=0, vmax=max_weight)
    cmap = plt.cm.get_cmap('RdYlGn_r')
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Draw nodes
    node_colors = []
    node_sizes = []
    for node in city_graph.graph.nodes():
        if node in ['Hospital', 'Airport']:
            node_colors.append('red')
            node_sizes.append(700)
        elif node in ['Downtown', 'Shopping Mall']:
            node_colors.append('orange')
            node_sizes.append(600)
        else:
            node_colors.append('skyblue')
            node_sizes.append(500)
    
    nx.draw_networkx_nodes(
        city_graph.graph, pos, 
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        ax=ax
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        city_graph.graph, pos,
        font_size=10,
        font_weight='bold',
        ax=ax
    )
    
    # Draw edges
    edge_collection = nx.draw_networkx_edges(
        city_graph.graph, pos, 
        edgelist=edges,
        width=3,
        alpha=0.7,
        edge_color=weights,
        edge_cmap=cmap,
        edge_vmin=0,
        edge_vmax=max_weight,
        ax=ax
    )
    
    # Highlight path
    if highlight_path:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
        nx.draw_networkx_edges(
            city_graph.graph, pos,
            edgelist=path_edges,
            edge_color='blue',
            width=6,
            alpha=0.9,
            ax=ax
        )
    
    # Add congestion info
    if congestion_info:
        _draw_congestion_info(city_graph, pos, ax)
    
    # Add colorbar
    if edge_collection:
        plt.colorbar(edge_collection, ax=ax, label='Travel Time (minutes)')
    
    plt.title("City Road Network (Green = Fast, Red = Congested)", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('graph.png', bbox_inches='tight', dpi=300)
    plt.close()
    return Image.open('graph.png')

def visualize_on_map(city_graph: CityGraph, path: Optional[List[str]] = None) -> folium.Map:
    """Visualize the graph on a real map"""
    city_center = city_graph.calculate_center()
    m = folium.Map(location=city_center, zoom_start=14)
    
    # Add nodes
    for node, coords in city_graph.node_coords.items():
        folium.Marker(
            coords,
            popup=f"<b>{node}</b>",
            tooltip=node
        ).add_to(m)
    
    # Add edges
    for u, v, data in city_graph.graph.edges(data=True):
        weight = data['weight']
        max_weight = max(d['weight'] for _, _, d in city_graph.graph.edges(data=True))
        hue = 120 - (weight / max_weight * 120)
        color = f"hsl({hue}, 100%, 50%)"
        
        folium.PolyLine(
            [city_graph.node_coords[u], city_graph.node_coords[v]],
            color=color,
            weight=5,
            opacity=0.7,
            tooltip=f"{u} to {v}: {weight} min"
        ).add_to(m)
    
    # Highlight path
    if path:
        path_coords = [city_graph.node_coords[node] for node in path]
        folium.PolyLine(
            path_coords,
            color='blue',
            weight=8,
            opacity=0.9,
            tooltip="Selected Route"
        ).add_to(m)
    
    return m

def _get_visualization_weight(city_graph: CityGraph, u: str, v: str, time_of_day: Optional[str]) -> float:
    """Get weight for visualization considering time and user reports"""
    weight = city_graph.graph[u][v]['weight']
    
    if time_of_day and (u, v) in city_graph.time_weights:
        weight = city_graph.time_weights[(u, v)][time_of_day]
    
    if (u, v) in city_graph.user_reports:
        weight += city_graph.user_reports[(u, v)]
    
    return weight

def _draw_congestion_info(city_graph: CityGraph, pos, ax):
    """Draw congestion zones and user reports"""
    edges = list(city_graph.graph.edges())
    
    # Draw congestion zones
    congestion_edges = [edge for edge in edges if edge in city_graph.congestion_zones]
    nx.draw_networkx_edges(
        city_graph.graph, pos,
        edgelist=congestion_edges,
        edge_color='black',
        width=2,
        style='dashed',
        alpha=0.7,
        ax=ax
    )
    
    # Draw user reports
    report_edges = [edge for edge in edges if edge in city_graph.user_reports]
    nx.draw_networkx_edges(
        city_graph.graph, pos,
        edgelist=report_edges,
        edge_color='purple',
        width=2,
        style='dotted',
        alpha=0.7,
        ax=ax
    )