"""
AI-NEXUS CO-LOCATION MANAGER
Geographic optimization for sub-millisecond blockchain access
"""

import gevent
import socket
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from geolite2 import geolite2

@dataclass
class NodeLocation:
    provider: str
    region: str
    city: str
    latitude: float
    longitude: float
    latency: float
    health_score: float

class CoLocationManager:
    def __init__(self, config):
        self.config = config
        self.reader = geolite2.reader()
        self.node_locations = {}
        self.optimal_nodes = {}
        self.logger = logging.getLogger(__name__)
        
    def discover_optimal_locations(self, blockchain_peers: List[str]) -> Dict:
        """Discover geographically optimal node locations"""
        location_analysis = {}
        
        for peer in blockchain_peers:
            location_data = self.analyze_peer_location(peer)
            if location_data:
                location_analysis[peer] = location_data
                self.node_locations[peer] = location_data
        
        # Rank nodes by latency and health score
        ranked_nodes = self.rank_nodes_by_performance(location_analysis)
        self.optimal_nodes = ranked_nodes
        
        return ranked_nodes
    
    def analyze_peer_location(self, peer_address: str) -> Optional[NodeLocation]:
        """Analyze geographic location and latency of blockchain peer"""
        try:
            # Extract IP from peer address
            ip = self.extract_ip_from_peer(peer_address)
            if not ip:
                return None
            
            # Get geographic information
            geo_info = self.reader.get(ip)
            if not geo_info:
                return None
            
            # Measure latency
            latency = self.measure_latency(ip)
            
            location = NodeLocation(
                provider=peer_address,
                region=geo_info.get('country', {}).get('names', {}).get('en', 'Unknown'),
                city=geo_info.get('city', {}).get('names', {}).get('en', 'Unknown'),
                latitude=geo_info.get('location', {}).get('latitude', 0),
                longitude=geo_info.get('location', {}).get('longitude', 0),
                latency=latency,
                health_score=self.calculate_health_score(latency, geo_info)
            )
            
            return location
            
        except Exception as e:
            self.logger.warning(f"Failed to analyze peer {peer_address}: {e}")
            return None
    
    def extract_ip_from_peer(self, peer_address: str) -> Optional[str]:
        """Extract IP address from peer address string"""
        try:
            # Handle different peer address formats
            if '://' in peer_address:
                # URL format: https://1.2.3.4:8545
                parts = peer_address.split('://')
                if len(parts) > 1:
                    address_part = parts[1].split(':')[0]
                    return address_part
            else:
                # IP:port format
                return peer_address.split(':')[0]
                
        except Exception as e:
            self.logger.error(f"Failed to extract IP from {peer_address}: {e}")
            return None
    
    def measure_latency(self, ip: str, port: int = 8545, samples: int = 3) -> float:
        """Measure network latency to node"""
        latencies = []
        
        for _ in range(samples):
            try:
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)  # 2 second timeout
                sock.connect((ip, port))
                end_time = time.time()
                sock.close()
                
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                latencies.append(latency)
                
            except socket.timeout:
                latencies.append(1000)  # Penalize timeout with high latency
            except Exception as e:
                self.logger.debug(f"Latency measurement failed for {ip}:{port}: {e}")
                latencies.append(2000)  # Penalize connection errors
        
        return sum(latencies) / len(latencies) if latencies else 1000
    
    def calculate_health_score(self, latency: float, geo_info: Dict) -> float:
        """Calculate health score based on latency and geographic stability"""
        # Base score from latency (lower latency = higher score)
        latency_score = max(0, 100 - (latency / 10))
        
        # Geographic stability bonus (known regions get higher scores)
        country = geo_info.get('country', {}).get('iso_code', '')
        stable_regions = ['US', 'DE', 'SG', 'NL', 'GB']  # Known stable regions
        stability_bonus = 10 if country in stable_regions else 0
        
        return min(100, latency_score + stability_bonus)
    
    def rank_nodes_by_performance(self, location_analysis: Dict) -> Dict:
        """Rank nodes by performance score"""
        scored_nodes = {}
        
        for peer, location in location_analysis.items():
            # Combined score: 70% latency, 30% health
            performance_score = (
                (100 - min(location.latency, 100)) * 0.7 +  # Lower latency better
                location.health_score * 0.3
            )
            
            scored_nodes[peer] = {
                'performance_score': performance_score,
                'latency': location.latency,
                'region': location.region,
                'city': location.city,
                'health_score': location.health_score
            }
        
        # Sort by performance score (descending)
        sorted_nodes = dict(sorted(
            scored_nodes.items(), 
            key=lambda x: x[1]['performance_score'], 
            reverse=True
        ))
        
        return sorted_nodes
    
    def get_optimal_node(self, region_preference: str = None) -> str:
        """Get optimal node based on performance and optional region preference"""
        if not self.optimal_nodes:
            return None
        
        if region_preference:
            # Filter by preferred region
            regional_nodes = {
                peer: data for peer, data in self.optimal_nodes.items()
                if data['region'].lower() == region_preference.lower()
            }
            if regional_nodes:
                return next(iter(regional_nodes.keys()))
        
        # Return highest performing node
        return next(iter(self.optimal_nodes.keys()))
    
    def optimize_node_selection(self, target_regions: List[str] = None) -> List[str]:
        """Optimize node selection for multi-region deployment"""
        if not target_regions:
            # Use top 3 performing regions
            regions = set(data['region'] for data in self.optimal_nodes.values())
            target_regions = list(regions)[:3]
        
        optimized_nodes = []
        for region in target_regions:
            regional_node = self.get_optimal_node(region)
            if regional_node:
                optimized_nodes.append(regional_node)
        
        return optimized_nodes
    
    def get_performance_report(self) -> Dict:
        """Generate performance report for all monitored nodes"""
        return {
            'total_nodes': len(self.optimal_nodes),
            'optimal_nodes': self.optimal_nodes,
            'average_latency': sum(
                data['latency'] for data in self.optimal_nodes.values()
            ) / len(self.optimal_nodes) if self.optimal_nodes else 0,
            'top_performer': next(iter(self.optimal_nodes.items())) if self.optimal_nodes else None
        }
