"""
Hop Tracker Module - Centralized hop calculation and logging for Meshtastic nodes.
Rebuilds hop tracking from scratch with comprehensive file system logging.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import threading
from collections import defaultdict

# Configure module logger
logger = logging.getLogger(__name__)


class HopTracker:
    """Tracks and logs hop counts for all Meshtastic nodes."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the hop tracker with file logging."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # In-memory hop storage (node_id -> hop_data)
        self.node_hops: Dict[str, Dict[str, Any]] = {}
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
        
        # Setup file loggers
        self._setup_loggers()
        
        # Log startup
        self._log_event("startup", {"message": "Hop tracker initialized"})
        
    def _setup_loggers(self):
        """Setup different log files for different purposes."""
        # Main hop tracker log
        hop_handler = logging.FileHandler(self.log_dir / "hop_tracker.log")
        hop_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        # Create specific logger for hop tracking
        self.hop_logger = logging.getLogger("hop_tracker")
        self.hop_logger.addHandler(hop_handler)
        self.hop_logger.setLevel(logging.DEBUG)
        
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to the appropriate log file."""
        timestamp = datetime.now().isoformat()
        
        # Log to hop tracker log
        self.hop_logger.info(f"{event_type}: {json.dumps(data)}")
        
        # Also log to JSON Lines file for easy parsing
        jsonl_path = self.log_dir / "packets.jsonl"
        with open(jsonl_path, "a") as f:
            log_entry = {
                "timestamp": timestamp,
                "event": event_type,
                **data
            }
            f.write(json.dumps(log_entry) + "\n")
    
    def _log_node_update(self, node_id: str, update_data: Dict[str, Any]):
        """Log node metadata updates."""
        log_path = self.log_dir / "node_updates.log"
        timestamp = datetime.now().isoformat()
        
        with open(log_path, "a") as f:
            log_entry = {
                "timestamp": timestamp,
                "node_id": node_id,
                "update": update_data
            }
            f.write(json.dumps(log_entry) + "\n")
    
    def normalize_node_id(self, node_id: Any) -> str:
        """
        Normalize node ID to consistent string format.
        Handles various formats: int, string, with/without "!" prefix.
        """
        if node_id is None:
            return "unknown"
        
        # Convert to string
        node_id_str = str(node_id)
        
        # Remove "!" prefix if present (from packet IDs)
        if node_id_str.startswith("!"):
            node_id_str = node_id_str[1:]
        
        return node_id_str
    
    def extract_hop_data(self, packet: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Extract hop count and related data from a packet.
        Returns (hop_count, metadata_dict)
        """
        # Get hop fields with defaults
        hop_limit = packet.get("hopLimit", None)
        hop_start = packet.get("hopStart", None)
        
        # Log raw hop fields for debugging
        self._log_event("hop_extraction", {
            "from": packet.get("fromId", "unknown"),
            "hop_limit": hop_limit,
            "hop_start": hop_start,
            "packet_type": packet.get("decoded", {}).get("portnum", "unknown")
        })
        
        # Calculate hop count
        hop_count = -1  # -1 means unknown
        
        if hop_limit is not None and hop_start is not None:
            # Both fields present - calculate hops taken
            hop_count = hop_start - hop_limit
            
            # Sanity check
            if hop_count < 0:
                self.hop_logger.warning(f"Negative hop count calculated: start={hop_start}, limit={hop_limit}")
                hop_count = -1
            elif hop_count > 7:  # Max hops in Meshtastic is typically 7
                self.hop_logger.warning(f"Unusually high hop count: {hop_count}")
        elif hop_limit is not None and hop_start is None:
            # Only hop_limit present - common for some packet types
            # Assume hopStart is the default max (3 or 7 depending on config)
            # If hopLimit == 3, it's likely direct (no hops consumed)
            # If hopLimit < 3, some hops were consumed
            default_max_hops = 3  # Default in Meshtastic
            
            if hop_limit == default_max_hops:
                # Likely a direct packet (no hops consumed)
                hop_count = 0
                self.hop_logger.debug(f"Assuming direct connection (hopLimit={hop_limit}, no hopStart)")
            elif hop_limit < default_max_hops:
                # Some hops consumed
                hop_count = default_max_hops - hop_limit
                self.hop_logger.debug(f"Estimating {hop_count} hops (hopLimit={hop_limit}, assumed start={default_max_hops})")
            else:
                # hopLimit > default, unusual
                self.hop_logger.warning(f"Unusual hopLimit {hop_limit} without hopStart")
        
        # Collect metadata
        metadata = {
            "hop_count": hop_count,
            "hop_limit": hop_limit,
            "hop_start": hop_start,
            "is_direct": hop_count == 0,
            "rssi": packet.get("rxRssi"),
            "snr": packet.get("rxSnr"),
            "via_mqtt": packet.get("viaMqtt", False),
            "channel": packet.get("channel", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        return hop_count, metadata
    
    def update_node_hops(self, node_id: Any, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update hop information for a node based on a packet.
        Returns the updated hop data for the node.
        """
        # Normalize node ID
        node_id = self.normalize_node_id(node_id)
        
        # Extract hop data
        hop_count, metadata = self.extract_hop_data(packet)
        
        with self.lock:
            # Get existing data or create new entry
            if node_id not in self.node_hops:
                self.node_hops[node_id] = {
                    "node_id": node_id,
                    "first_seen": datetime.now().isoformat(),
                    "hop_history": [],
                    "current_hops": -1,
                    "min_hops": -1,
                    "max_hops": -1,
                    "is_direct": False,
                    "last_rssi": None,
                    "last_snr": None,
                    "packet_count": 0
                }
            
            node_data = self.node_hops[node_id]
            
            # Update packet count
            node_data["packet_count"] += 1
            
            # Update hop count if valid
            if hop_count >= 0:
                # Add to history (keep last 10)
                node_data["hop_history"].append({
                    "hops": hop_count,
                    "timestamp": metadata["timestamp"],
                    "rssi": metadata["rssi"],
                    "snr": metadata["snr"]
                })
                if len(node_data["hop_history"]) > 10:
                    node_data["hop_history"].pop(0)
                
                # Update current hop count
                node_data["current_hops"] = hop_count
                node_data["is_direct"] = hop_count == 0
                
                # Update min/max
                if node_data["min_hops"] == -1 or hop_count < node_data["min_hops"]:
                    node_data["min_hops"] = hop_count
                if hop_count > node_data["max_hops"]:
                    node_data["max_hops"] = hop_count
                
                # Log significant changes
                self._log_event("hop_update", {
                    "node_id": node_id,
                    "hop_count": hop_count,
                    "is_direct": hop_count == 0,
                    "min_hops": node_data["min_hops"],
                    "max_hops": node_data["max_hops"]
                })
            
            # Update signal info if direct connection
            if hop_count == 0 and metadata["rssi"] is not None:
                node_data["last_rssi"] = metadata["rssi"]
                node_data["last_snr"] = metadata["snr"]
            
            # Update last seen
            node_data["last_seen"] = metadata["timestamp"]
            
            # Log the update
            self._log_node_update(node_id, {
                "hops": hop_count if hop_count >= 0 else "unknown",
                "rssi": metadata["rssi"],
                "snr": metadata["snr"],
                "packet_count": node_data["packet_count"]
            })
            
            return node_data.copy()
    
    def get_node_hop_data(self, node_id: Any) -> Dict[str, Any]:
        """Get hop data for a specific node."""
        node_id = self.normalize_node_id(node_id)
        
        with self.lock:
            if node_id in self.node_hops:
                return self.node_hops[node_id].copy()
            return {
                "node_id": node_id,
                "current_hops": -1,
                "is_direct": False,
                "packet_count": 0
            }
    
    def get_all_nodes_hop_data(self) -> Dict[str, Dict[str, Any]]:
        """Get hop data for all tracked nodes."""
        with self.lock:
            return {k: v.copy() for k, v in self.node_hops.items()}
    
    def get_hop_summary(self) -> Dict[str, Any]:
        """Get a summary of hop tracking statistics."""
        with self.lock:
            total_nodes = len(self.node_hops)
            direct_nodes = sum(1 for n in self.node_hops.values() if n["is_direct"])
            indirect_nodes = sum(1 for n in self.node_hops.values() 
                               if n["current_hops"] > 0)
            unknown_nodes = sum(1 for n in self.node_hops.values() 
                              if n["current_hops"] == -1)
            
            hop_distribution = defaultdict(int)
            for node in self.node_hops.values():
                if node["current_hops"] >= 0:
                    hop_distribution[node["current_hops"]] += 1
            
            summary = {
                "total_nodes": total_nodes,
                "direct_nodes": direct_nodes,
                "indirect_nodes": indirect_nodes,
                "unknown_nodes": unknown_nodes,
                "hop_distribution": dict(hop_distribution),
                "timestamp": datetime.now().isoformat()
            }
            
            # Log summary
            self._log_event("hop_summary", summary)
            
            return summary
    
    def reset_node(self, node_id: Any):
        """Reset hop data for a specific node."""
        node_id = self.normalize_node_id(node_id)
        
        with self.lock:
            if node_id in self.node_hops:
                del self.node_hops[node_id]
                self._log_event("node_reset", {"node_id": node_id})


# Global hop tracker instance
hop_tracker = HopTracker()