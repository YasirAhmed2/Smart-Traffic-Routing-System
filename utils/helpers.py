from typing import Dict, List, Optional, Tuple
from graph.core import CityGraph
from utils.constants import SAMPLE_INTERSECTIONS, SAMPLE_ROADS, NODE_COORDS, TIME_WEIGHTS

def initialize_sample_city() -> CityGraph:
    """Initialize a sample city with intersections and roads"""
    city_graph = CityGraph()
    
    # Add nodes
    city_graph.graph.add_nodes_from(SAMPLE_INTERSECTIONS)
    
    # Add edges
    for u, v, weight in SAMPLE_ROADS:
        city_graph.add_edge(u, v, weight)
    
    # Set coordinates
    city_graph.node_coords = NODE_COORDS
    
    # Initialize time-based weights
    for u, v, _ in SAMPLE_ROADS:
        city_graph.add_time_weight(u, v, {
            time: weight * factor 
            for time, factor in TIME_WEIGHTS.items()
        })
    
    return city_graph

def generate_route_summary(
    city_graph: CityGraph,
    path: List[str],
    time_of_day: Optional[str] = None,
    use_case: Optional[str] = None
) -> str:
    """Generate a summary of the route"""
    if not path:
        return "No path found"
    
    summary = f"Route from {path[0]} to {path[-1]}:\n\n"
    total_time = 0
    
    for i in range(len(path)-1):
        u = path[i]
        v = path[i+1]
        weight = _calculate_route_segment_weight(city_graph, u, v, time_of_day, use_case)
        summary += f"{u} → {v}: {weight:.1f} minutes\n"
        total_time += weight
    
    summary += f"\nTotal Travel Time: {total_time:.1f} minutes"
    
    if use_case:
        summary += f"\nUse Case: {use_case}"
    if time_of_day:
        summary += f"\nTime of Day: {time_of_day.capitalize()}"
    
    # Check for traffic alerts
    alert_edges = [
        f"{path[i]}-{path[i+1]}" 
        for i in range(len(path)-1) 
        if (path[i], path[i+1]) in city_graph.traffic_alerts
    ]
    
    if alert_edges:
        summary += "\n\n🚨 Traffic Alerts on: " + ", ".join(alert_edges)
    
    return summary

def _calculate_route_segment_weight(
    city_graph: CityGraph,
    u: str,
    v: str,
    time_of_day: Optional[str],
    use_case: Optional[str]
) -> float:
    """Calculate weight for a route segment considering all factors"""
    weight = city_graph.graph[u][v]['weight']
    
    if time_of_day and (u, v) in city_graph.time_weights:
        weight = city_graph.time_weights[(u, v)][time_of_day]
    
    if (u, v) in city_graph.user_reports:
        weight += city_graph.user_reports[(u, v)]
    
    return weight