import networkx as nx
from typing import Dict, Set, Tuple, List, Optional

class CityGraph:
    def __init__(self):
        """Initialize an empty city graph with all necessary attributes"""
        self.graph = nx.Graph()
        self.node_coords: Dict[str, Tuple[float, float]] = {}
        self.time_weights: Dict[Tuple[str, str], Dict[str, float]] = {}
        self.user_reports: Dict[Tuple[str, str], float] = {}
        self.congestion_zones: Set[Tuple[str, str]] = set()
        self.traffic_alerts: Set[Tuple[str, str]] = set()
    
    def add_edge(self, node1: str, node2: str, weight: float):
        """Add an edge between two nodes with given weight"""
        self.graph.add_edge(node1, node2, weight=weight)
    
    def add_time_weight(self, node1: str, node2: str, time_weights: Dict[str, float]):
        """Add time-based weights for an edge"""
        self.time_weights[(node1, node2)] = time_weights
        self.time_weights[(node2, node1)] = time_weights
    
    def add_congestion_zone(self, node1: str, node2: str) -> bool:
        """Mark a road as congested"""
        if self.graph.has_edge(node1, node2):
            self.congestion_zones.add((node1, node2))
            self.congestion_zones.add((node2, node1))
            return True
        return False
    
    def remove_congestion_zone(self, node1: str, node2: str) -> bool:
        """Remove congestion mark from a road"""
        if (node1, node2) in self.congestion_zones:
            self.congestion_zones.remove((node1, node2))
            self.congestion_zones.remove((node2, node1))
            return True
        return False
    
    def add_user_report(self, node1: str, node2: str, delay: float) -> bool:
        """Add user-reported traffic delay"""
        if self.graph.has_edge(node1, node2):
            self.user_reports[(node1, node2)] = delay
            self.user_reports[(node2, node1)] = delay
            
            base_weight = self.graph[node1][node2]['weight']
            if (base_weight + delay) > base_weight * 1.5:
                self.traffic_alerts.add((node1, node2))
            return True
        return False
    
    def clear_user_reports(self):
        """Clear all user-reported delays"""
        self.user_reports.clear()
        self.traffic_alerts.clear()
    
    def calculate_center(self) -> Tuple[float, float]:
        """Calculate the center point of all nodes"""
        lats = [coords[0] for coords in self.node_coords.values()]
        lons = [coords[1] for coords in self.node_coords.values()]
        return (sum(lats)/len(lats), sum(lons)/len(lons))