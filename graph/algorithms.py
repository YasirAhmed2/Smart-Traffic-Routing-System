import heapq
from typing import List, Tuple, Optional, Dict, Set
from .core import CityGraph

def dijkstra(
    city_graph: CityGraph,
    start: str,
    end: str,
    time_of_day: Optional[str] = None,
    use_case: Optional[str] = None
) -> Tuple[float, List[str]]:
    """Find shortest path using Dijkstra's algorithm with time and use case considerations"""
    heap = []
    heapq.heappush(heap, (0, start, []))
    
    visited = {node: float('inf') for node in city_graph.graph.nodes()}
    visited[start] = 0
    paths = {start: []}
    
    while heap:
        current_dist, current_node, path = heapq.heappop(heap)
        
        if current_node == end:
            return current_dist, path + [current_node]
        
        if current_dist > visited[current_node]:
            continue
            
        for neighbor, edge_data in city_graph.graph[current_node].items():
            weight = _calculate_adjusted_weight(
                city_graph, current_node, neighbor, edge_data['weight'], 
                time_of_day, use_case
            )
            
            distance = current_dist + weight
            
            if distance < visited[neighbor]:
                visited[neighbor] = distance
                paths[neighbor] = path + [current_node]
                heapq.heappush(heap, (distance, neighbor, path + [current_node]))
    
    return float('inf'), []



def yen_k_shortest_paths(
    city_graph: CityGraph,
    start: str,
    end: str,
    k: int = 3,
    time_of_day: Optional[str] = None,
    use_case: Optional[str] = None
) -> List[Tuple[float, List[str]]]:
    """Find k shortest paths using Yen's algorithm"""
    paths = []
    
    # Get shortest path
    dist, path = dijkstra(city_graph, start, end, time_of_day, use_case)
    if path:
        paths.append((dist, path))
    
    # Find k-1 more paths
    for i in range(1, k):
        for j in range(len(paths[i-1][1]) - 1):
            spur_node = paths[i-1][1][j]
            root_path = paths[i-1][1][:j+1]
            
            edges_removed = []
            for prev_path in paths:
                if len(prev_path[1]) > j and root_path == prev_path[1][:j+1]:
                    u = prev_path[1][j]
                    v = prev_path[1][j+1]
                    if city_graph.graph.has_edge(u, v):
                        edges_removed.append((u, v, city_graph.graph[u][v]['weight']))
                        city_graph.graph.remove_edge(u, v)
            
            spur_dist, spur_path = dijkstra(city_graph, spur_node, end, time_of_day, use_case)
            
            for u, v, w in edges_removed:
                city_graph.graph.add_edge(u, v, weight=w)
            
            if spur_path:
                total_path = root_path[:-1] + spur_path
                total_dist = 0
                
                for x in range(len(total_path)-1):
                    u = total_path[x]
                    v = total_path[x+1]
                    weight = _calculate_adjusted_weight(
                        city_graph, u, v, city_graph.graph[u][v]['weight'],
                        time_of_day, use_case
                    )
                    total_dist += weight
                
                if not any(p[1] == total_path for p in paths):
                    paths.append((total_dist, total_path))
        
        if len(paths) <= i:
            break
    
    return sorted(paths, key=lambda x: x[0])[:k]

def _calculate_adjusted_weight(
    city_graph: CityGraph,
    u: str,
    v: str,
    base_weight: float,
    time_of_day: Optional[str],
    use_case: Optional[str]
) -> float:
    """Calculate adjusted weight considering time, use case, and traffic conditions"""
    weight = base_weight
    
    # Apply time-based weight
    if time_of_day and (u, v) in city_graph.time_weights:
        weight = city_graph.time_weights[(u, v)][time_of_day]
    
    # Apply use case adjustments
    if use_case == "Ambulance":
        if (u, v) in city_graph.congestion_zones:
            weight *= 0.5
        if (u, v) in city_graph.traffic_alerts:
            weight *= 0.7
    elif use_case == "Delivery Truck":
        if (u, v) in city_graph.congestion_zones:
            weight *= 2
        if v in ["Residential A", "Residential B"]:
            weight *= 1.3
    elif use_case == "Cyclist":
        if base_weight > 10:
            weight *= 1.5
        if v == "Central Park" or u == "Central Park":
            weight *= 0.8
    
    # Apply user reports
    if (u, v) in city_graph.user_reports:
        weight += city_graph.user_reports[(u, v)]
    
    return weight