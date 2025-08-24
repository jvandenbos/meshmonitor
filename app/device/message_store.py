"""Simple in-memory message and node store."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
import json
import math


class MessageStore:
    """In-memory store for messages and nodes."""
    
    def __init__(self, max_messages: int = 10000):
        self.messages = deque(maxlen=max_messages)
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.my_position: Optional[Dict[str, float]] = None
        
    def add_message(self, message: Dict[str, Any]):
        """Add a message to the store."""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        self.messages.appendleft(message)  # Most recent first
        
    def add_or_update_node(self, node_id: str, data: Dict[str, Any]):
        """Add or update node information."""
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "first_seen": datetime.now().isoformat()
            }
        
        # Update node data
        self.nodes[node_id].update(data)
        self.nodes[node_id]["last_updated"] = datetime.now().isoformat()
        
        # Calculate distance if we have positions
        if self.my_position and "position" in data:
            pos = data["position"]
            if isinstance(pos, dict) and "latitude" in pos and "longitude" in pos:
                distance = self._calculate_distance(
                    self.my_position["latitude"],
                    self.my_position["longitude"],
                    pos["latitude"],
                    pos["longitude"]
                )
                self.nodes[node_id]["distance_km"] = distance
    
    def set_my_position(self, latitude: float, longitude: float):
        """Set our own position for distance calculations."""
        self.my_position = {"latitude": latitude, "longitude": longitude}
        # Recalculate all distances
        for node_id, node in self.nodes.items():
            if "position" in node:
                pos = node["position"]
                if isinstance(pos, dict) and "latitude" in pos and "longitude" in pos:
                    distance = self._calculate_distance(
                        latitude, longitude,
                        pos["latitude"], pos["longitude"]
                    )
                    node["distance_km"] = distance
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula."""
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return round(distance, 2)
    
    def get_messages(self, limit: int = 100, message_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent messages, optionally filtered by type."""
        messages = list(self.messages)
        if message_type:
            messages = [m for m in messages if m.get("type") == message_type]
        return messages[:limit]
    
    def get_nodes(self, sort_by_proximity: bool = False) -> List[Dict[str, Any]]:
        """Get all nodes, optionally sorted by proximity."""
        nodes = list(self.nodes.values())
        
        if sort_by_proximity:
            # Sort by distance if available, otherwise by last_updated
            def sort_key(node):
                if "distance_km" in node:
                    return (0, node["distance_km"])
                else:
                    return (1, node.get("last_updated", ""))
            
            nodes.sort(key=sort_key)
        else:
            # Sort by last updated
            nodes.sort(key=lambda n: n.get("last_updated", ""), reverse=True)
        
        return nodes
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific node by ID."""
        return self.nodes.get(node_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the stored data."""
        message_types = {}
        for msg in self.messages:
            msg_type = msg.get("type", "unknown")
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        return {
            "total_messages": len(self.messages),
            "total_nodes": len(self.nodes),
            "message_types": message_types,
            "nodes_with_position": sum(1 for n in self.nodes.values() if "position" in n),
            "nodes_with_telemetry": sum(1 for n in self.nodes.values() if "telemetry" in n)
        }


# Global store instance
message_store = MessageStore()