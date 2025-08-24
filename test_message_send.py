#!/usr/bin/env python3
"""Test script to verify message sending functionality."""

import asyncio
import sys
sys.path.insert(0, '.')

from app.device.connection import device
from datetime import datetime

async def test_send_message():
    """Test sending a message on channel 7."""
    print("Testing message send functionality...")
    print("-" * 50)
    
    # First ensure we're connected
    if not device.connected:
        print("❌ Device not connected. Attempting to connect...")
        connected = await device.connect()
        if not connected:
            print("❌ Failed to connect to device")
            return False
    else:
        print("✅ Device already connected")
    
    # Device info
    if device.device_info:
        print(f"📡 Connected to node: {device.device_info.get('node_id', 'Unknown')}")
    
    # Test message on channel 7
    test_channel = 7
    test_message = f"Dashboard test at {datetime.now().strftime('%H:%M:%S')}"
    
    print(f"\n📤 Sending test message on Channel {test_channel}...")
    print(f"   Message: '{test_message}'")
    
    # Send the message
    success = await device.send_text(test_message, test_channel)
    
    if success:
        print(f"✅ Message sent successfully on Channel {test_channel}!")
        print("\nNote: Channel 7 is typically unused, so this shouldn't spam anyone.")
        print("      You can monitor this channel in the dashboard to verify receipt.")
        return True
    else:
        print("❌ Failed to send message")
        print("   Check that the device is properly connected")
        return False

async def main():
    """Main test function."""
    print("\n" + "="*50)
    print("Meshtastic Message Send Test")
    print("="*50 + "\n")
    
    # Run the test
    success = await test_send_message()
    
    print("\n" + "="*50)
    if success:
        print("✅ Test completed successfully!")
        print("\nNext steps:")
        print("1. Check the dashboard to see if the message appears")
        print("2. Try sending a message from the dashboard UI")
        print("3. Use Test Mode (Channel 7) to avoid spamming public channels")
    else:
        print("❌ Test failed")
        print("\nTroubleshooting:")
        print("1. Ensure your Meshtastic device is connected via USB")
        print("2. Check that no other process is using the device")
        print("3. Try restarting the dashboard")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())