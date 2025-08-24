#!/usr/bin/env python3
"""Test script to add sample nodes with signal strength data."""

import sys
sys.path.insert(0, '.')

from app.device.message_store import message_store
from datetime import datetime

# Add some test nodes with varying signal strengths
test_nodes = [
    {
        "id": "test_node_1",
        "long_name": "Test Node Excellent",
        "short_name": "TN1",
        "rssi": -55,  # Excellent signal
        "snr": 10.5,
        "hops": 0,
        "is_direct": True,
        "last_updated": datetime.now().isoformat(),
        "distance_km": 0.5,
        "battery_level": 95
    },
    {
        "id": "test_node_2",
        "long_name": "Test Node Good",
        "short_name": "TN2",
        "rssi": -72,  # Good signal
        "snr": 8.2,
        "hops": 0,
        "is_direct": True,
        "last_updated": datetime.now().isoformat(),
        "distance_km": 1.2,
        "battery_level": 75
    },
    {
        "id": "test_node_3",
        "long_name": "Test Node Fair",
        "short_name": "TN3",
        "rssi": -82,  # Fair signal
        "snr": 5.1,
        "hops": 1,
        "is_direct": False,
        "last_updated": datetime.now().isoformat(),
        "distance_km": 3.5,
        "battery_level": 50
    },
    {
        "id": "test_node_4",
        "long_name": "Test Node Poor",
        "short_name": "TN4",
        "rssi": -95,  # Poor signal
        "snr": 2.3,
        "hops": 2,
        "is_direct": False,
        "last_updated": datetime.now().isoformat(),
        "distance_km": 8.7,
        "battery_level": 25
    },
    {
        "id": "test_node_5",
        "long_name": "Test Node No Signal",
        "short_name": "TN5",
        "rssi": None,  # No signal data
        "snr": None,
        "hops": 3,
        "is_direct": False,
        "last_updated": datetime.now().isoformat(),
        "distance_km": 15.2,
        "battery_level": 60
    }
]

# Add nodes to the message store
for node in test_nodes:
    message_store.nodes[node["id"]] = node
    print(f"Added test node: {node['long_name']} with RSSI: {node.get('rssi', 'None')}")

print(f"\nTotal nodes in store: {len(message_store.nodes)}")
print("Test nodes added successfully! Check the dashboard.")