#!/usr/bin/env python3
"""Test script to see raw packet structure."""

import sys
import asyncio
import json
from datetime import datetime

sys.path.insert(0, '.')

import meshtastic.serial_interface
from pubsub import pub


def on_packet(packet, interface):
    """Log raw packet structure."""
    print("\n" + "="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Packet Type: {type(packet)}")
    print(f"Packet Content:")
    print(json.dumps(packet, indent=2, default=str))
    print("="*60)


async def main():
    """Connect and listen for packets."""
    print("Connecting to Meshtastic device...")
    
    # Subscribe to all packets
    pub.subscribe(on_packet, "meshtastic.receive")
    
    # Create interface
    interface = meshtastic.serial_interface.SerialInterface()
    
    print("Connected! Listening for packets...")
    print("Press Ctrl+C to stop")
    
    # Wait and listen
    try:
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        interface.close()


if __name__ == "__main__":
    asyncio.run(main())