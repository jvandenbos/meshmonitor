#!/usr/bin/env python3
"""Test script to verify connection to RAK4631 Meshtastic device."""

import asyncio
import logging
import sys
from rich.console import Console
from rich.logging import RichHandler

# Add app to path
sys.path.insert(0, '.')

from app.device.connection import MeshtasticDevice

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

console = Console()


async def message_handler(message_type: str, data: dict):
    """Handle incoming messages."""
    console.print(f"[green]Received {message_type}:[/green]", data)


async def main():
    """Test connection to Meshtastic device."""
    console.print("[bold cyan]Meshtastic Device Connection Test[/bold cyan]\n")
    
    device = MeshtasticDevice()
    
    # Register message handler
    device.register_handler("*", message_handler)
    
    # Try to connect
    console.print("[yellow]Attempting to connect to RAK4631...[/yellow]")
    
    if await device.connect():
        console.print("[bold green]✓ Successfully connected![/bold green]")
        console.print(f"[cyan]Device Info:[/cyan] {device.device_info}")
        
        # Get all nodes
        nodes = await device.get_nodes()
        console.print(f"\n[cyan]Found {len(nodes)} nodes in the mesh:[/cyan]")
        
        for node_id, node_info in nodes.items():
            user = node_info.get("user", {})
            name = user.get("longName", "Unknown")
            console.print(f"  • {name} ({node_id})")
        
        # Send a test message
        console.print("\n[yellow]Sending test message...[/yellow]")
        if await device.send_text("Hello from Meshtastic Server!", channel=0):
            console.print("[green]✓ Message sent successfully![/green]")
        
        # Listen for messages for 30 seconds
        console.print("\n[cyan]Listening for messages for 30 seconds...[/cyan]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        try:
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping...[/yellow]")
        
        # Disconnect
        await device.disconnect()
        console.print("[green]✓ Disconnected[/green]")
        
    else:
        console.print("[bold red]✗ Failed to connect to device[/bold red]")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("1. Make sure RAK4631 is connected via USB")
        console.print("2. Check that you have permission to access the serial port")
        console.print("3. On Linux/Mac, you may need to run: sudo usermod -a -G dialout $USER")
        console.print("4. Try specifying the port in .env file (e.g., SERIAL_PORT=/dev/ttyUSB0)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logging.exception("Unhandled exception")