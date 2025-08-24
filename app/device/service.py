"""Background service for Meshtastic device monitoring."""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from app.device.connection import device
from app.device.message_store import message_store

logger = logging.getLogger(__name__)


class MeshtasticService:
    """Service to manage Meshtastic device connection and data collection."""
    
    def __init__(self):
        self.running = False
        self.task = None
        
    async def start(self):
        """Start the service."""
        if self.running:
            logger.warning("Service already running")
            return
        
        self.running = True
        
        # Register message handlers
        device.register_handler("*", self._handle_all_messages)
        device.register_handler("text", self._handle_text_message)
        device.register_handler("position", self._handle_position)
        device.register_handler("nodeinfo", self._handle_node_info)
        device.register_handler("telemetry", self._handle_telemetry)
        
        # Connect to device
        logger.info("Starting Meshtastic service...")
        if await device.connect():
            logger.info("Successfully connected to Meshtastic device")
            
            # Get initial node list
            nodes = await device.get_nodes()
            for node_id, node_data in nodes.items():
                self._process_node_data(node_id, node_data)
            
            # Set our position if available
            if device.interface and hasattr(device.interface, 'localNode'):
                try:
                    local_node = device.interface.localNode
                    # Check if localNode is a dict-like object
                    if local_node and hasattr(local_node, 'position'):
                        pos = local_node.position
                        if hasattr(pos, 'latitudeI') and hasattr(pos, 'longitudeI'):
                            lat = pos.latitudeI / 1e7
                            lon = pos.longitudeI / 1e7
                            message_store.set_my_position(lat, lon)
                            logger.info(f"Set local position: {lat}, {lon}")
                    elif local_node and isinstance(local_node, dict) and "position" in local_node:
                        pos = local_node["position"]
                        if "latitudeI" in pos and "longitudeI" in pos:
                            lat = pos["latitudeI"] / 1e7
                            lon = pos["longitudeI"] / 1e7
                            message_store.set_my_position(lat, lon)
                            logger.info(f"Set local position: {lat}, {lon}")
                except Exception as e:
                    logger.warning(f"Could not get local position: {e}")
            
            # Start monitoring task
            self.task = asyncio.create_task(self._monitor_loop())
        else:
            logger.error("Failed to connect to Meshtastic device")
            self.running = False
    
    async def stop(self):
        """Stop the service."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        await device.disconnect()
        logger.info("Meshtastic service stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Check connection health
                if not device.connected:
                    logger.warning("Device disconnected, attempting reconnect...")
                    await device.connect()
                
                # Periodic node refresh (every 60 seconds)
                await asyncio.sleep(60)
                
                if device.connected:
                    nodes = await device.get_nodes()
                    for node_id, node_data in nodes.items():
                        self._process_node_data(node_id, node_data)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)
    
    async def _handle_all_messages(self, message_type: str, data: Dict[str, Any]):
        """Handle all messages for logging."""
        # Store all messages
        message_data = {
            "type": message_type,
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            **data
        }
        message_store.add_message(message_data)
    
    async def _handle_text_message(self, message_type: str, data: Dict[str, Any]):
        """Handle text messages."""
        logger.info(f"Text from {data.get('from', 'unknown')}: {data.get('text', '')}")
    
    async def _handle_position(self, message_type: str, data: Dict[str, Any]):
        """Handle position updates."""
        node_id = data.get("from")
        if node_id:
            position_data = {
                "position": {
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "altitude": data.get("altitude")
                },
                "position_updated": data.get("timestamp")
            }
            message_store.add_or_update_node(node_id, position_data)
            logger.debug(f"Position update for {node_id}")
    
    async def _handle_node_info(self, message_type: str, data: Dict[str, Any]):
        """Handle node info updates."""
        node_id = data.get("node_id")
        if node_id:
            node_data = {
                "long_name": data.get("long_name"),
                "short_name": data.get("short_name"),
                "hw_model": data.get("hw_model"),
                "role": data.get("role")
            }
            message_store.add_or_update_node(node_id, node_data)
            logger.info(f"Node info update: {data.get('long_name')} ({node_id})")
    
    async def _handle_telemetry(self, message_type: str, data: Dict[str, Any]):
        """Handle telemetry data."""
        node_id = data.get("from")
        if node_id:
            telemetry_data = {
                "telemetry": {
                    "battery_level": data.get("battery_level"),
                    "voltage": data.get("voltage"),
                    "temperature": data.get("temperature"),
                    "humidity": data.get("humidity"),
                    "pressure": data.get("pressure")
                },
                "telemetry_updated": data.get("timestamp")
            }
            message_store.add_or_update_node(node_id, telemetry_data)
            logger.debug(f"Telemetry update for {node_id}")
    
    def _process_node_data(self, node_id: str, node_data: Dict[str, Any]):
        """Process node data from the device."""
        processed_data = {
            "id": node_id
        }
        
        # Extract user info
        if "user" in node_data:
            user = node_data["user"]
            processed_data.update({
                "long_name": user.get("longName"),
                "short_name": user.get("shortName"),
                "hw_model": user.get("hwModel"),
                "role": user.get("role")
            })
        
        # Extract position
        if "position" in node_data:
            pos = node_data["position"]
            if "latitudeI" in pos and "longitudeI" in pos:
                processed_data["position"] = {
                    "latitude": pos["latitudeI"] / 1e7,
                    "longitude": pos["longitudeI"] / 1e7,
                    "altitude": pos.get("altitude", 0)
                }
        
        # Extract device metrics
        if "deviceMetrics" in node_data:
            metrics = node_data["deviceMetrics"]
            processed_data["telemetry"] = {
                "battery_level": metrics.get("batteryLevel"),
                "voltage": metrics.get("voltage"),
                "air_util_tx": metrics.get("airUtilTx"),
                "channel_utilization": metrics.get("channelUtilization")
            }
        
        # Other metadata
        processed_data["last_heard"] = node_data.get("lastHeard")
        processed_data["snr"] = node_data.get("snr")
        
        message_store.add_or_update_node(node_id, processed_data)


# Global service instance
meshtastic_service = MeshtasticService()