"""Message and node store with SQLite persistence."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
import json
import math
import logging
from app.database.db import db

logger = logging.getLogger(__name__)


class MessageStore:
    """Message and node store with SQLite persistence."""
    
    def __init__(self, max_messages: int = 10000):
        self.messages = deque(maxlen=max_messages)
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.my_position: Optional[Dict[str, float]] = None
        self.db = db  # Database instance
        
        # Load existing data from database on startup
        self._load_from_db()
        logger.info("MessageStore initialized with database persistence")
        
    def _load_from_db(self):
        """Load existing data from database on startup."""
        try:
            # Load recent messages
            db_messages = self.db.get_messages(limit=1000)
            for msg in reversed(db_messages):  # Add in chronological order
                self.messages.appendleft(msg)
            
            # Load all nodes
            db_nodes = self.db.get_nodes()
            for node in db_nodes:
                self.nodes[node['id']] = node
            
            logger.info(f"Loaded {len(self.messages)} messages and {len(self.nodes)} nodes from database")
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
    
    def add_message(self, message: Dict[str, Any]):
        """Add a message to the store and persist to database."""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        # Add to memory
        self.messages.appendleft(message)  # Most recent first
        
        # Persist to database
        try:
            self.db.save_message(message)
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
        
    def add_or_update_node(self, node_id: str, data: Dict[str, Any]):
        """Add or update node information with database persistence."""
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "first_seen": datetime.now().isoformat()
            }
        
        # Update node data
        self.nodes[node_id].update(data)
        self.nodes[node_id]["last_updated"] = datetime.now().isoformat()
        self.nodes[node_id]["last_seen"] = datetime.now().isoformat()
        
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
                
                # Update position fields for database
                self.nodes[node_id]["latitude"] = pos["latitude"]
                self.nodes[node_id]["longitude"] = pos["longitude"]
                self.nodes[node_id]["altitude"] = pos.get("altitude")
                self.nodes[node_id]["position_updated_at"] = datetime.now().isoformat()
        
        # Update telemetry timestamp if we have telemetry data
        if "telemetry" in data or "battery_level" in data:
            self.nodes[node_id]["telemetry_updated_at"] = datetime.now().isoformat()
        
        # Persist to database
        try:
            self.db.save_node(self.nodes[node_id])
        except Exception as e:
            logger.error(f"Failed to save node to database: {e}")
    
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
            # Sort by: 1) Direct connections first, 2) Number of hops, 3) Distance
            def sort_key(node):
                # Handle None values properly
                hops = node.get("hops")
                if hops is None:
                    hops = 999  # Treat None as unknown/far
                
                # First priority: Direct connection (hop count 0)
                is_direct = node.get("is_direct", False) or hops == 0
                
                # Third priority: Distance (for nodes at same hop level)
                distance = node.get("distance_km")
                if distance is None:
                    distance = 9999
                
                # Return tuple for sorting (direct connections first, then by hops, then by distance)
                return (not is_direct, hops, distance)
            
            nodes.sort(key=sort_key)
        else:
            # Sort by last updated
            nodes.sort(key=lambda n: n.get("last_updated", ""), reverse=True)
        
        return nodes
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific node by ID."""
        return self.nodes.get(node_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the stored data including database stats."""
        message_types = {}
        for msg in self.messages:
            msg_type = msg.get("type", "unknown")
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        # Get database statistics
        db_stats = {}
        try:
            db_stats = self.db.get_stats()
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
        
        return {
            "total_messages": len(self.messages),
            "total_nodes": len(self.nodes),
            "message_types": message_types,
            "nodes_with_position": sum(1 for n in self.nodes.values() if "position" in n),
            "nodes_with_telemetry": sum(1 for n in self.nodes.values() if "telemetry" in n),
            "db_total_nodes": db_stats.get("total_nodes", 0),
            "db_active_nodes": db_stats.get("active_nodes", 0),
            "db_total_messages": db_stats.get("total_messages", 0),
            "db_size_mb": db_stats.get("database_size_mb", 0)
        }
    
    def get_node_history(self, node_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for a node from database."""
        try:
            return self.db.get_node_history(node_id, hours)
        except Exception as e:
            logger.error(f"Failed to get node history: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 30) -> tuple[int, int]:
        """Clean up old data from database."""
        try:
            return self.db.cleanup_old_data(days)
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0, 0


# Global store instance
message_store = MessageStore()