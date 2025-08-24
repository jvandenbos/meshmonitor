import asyncio
import logging
from typing import Optional, Callable, Any, Dict
from datetime import datetime
import json

import meshtastic
import meshtastic.serial_interface
import meshtastic.tcp_interface
from pubsub import pub

from app.config import settings
from app.utils.error_handler import error_handler, DeviceConnectionError, MessageProcessingError

logger = logging.getLogger(__name__)


class MeshtasticDevice:
    """Manages connection to a Meshtastic device via USB serial."""
    
    def __init__(self):
        self.interface: Optional[meshtastic.serial_interface.SerialInterface] = None
        self.connected = False
        self.node_id: Optional[str] = None
        self.device_info: Dict[str, Any] = {}
        self._message_handlers: Dict[str, list] = {}
        self._reconnect_task: Optional[asyncio.Task] = None
        
    async def connect(self, port: Optional[str] = None) -> bool:
        """Connect to Meshtastic device via serial port."""
        try:
            port = port or settings.serial_port
            
            logger.info(f"Attempting to connect to Meshtastic device on {port or 'auto-detected port'}...")
            
            # Create interface (will auto-detect if port is None)
            self.interface = meshtastic.serial_interface.SerialInterface(
                devPath=port,
                debugOut=self._debug_output if settings.debug else None
            )
            
            # Wait for connection
            await asyncio.sleep(2)  # Give it time to initialize
            
            # Get our node info
            if self.interface and self.interface.myInfo:
                self.node_id = self.interface.myInfo.my_node_num
                self.device_info = {
                    "node_id": self.node_id,
                    "hw_model": self.interface.myInfo.hw_model if hasattr(self.interface.myInfo, 'hw_model') else None,
                    "firmware_version": self.interface.myInfo.firmware_version if hasattr(self.interface.myInfo, 'firmware_version') else None,
                }
                self.connected = True
                
                # Subscribe to message topics
                self._subscribe_to_messages()
                
                logger.info(f"Successfully connected to Meshtastic device: {self.device_info}")
                return True
            else:
                logger.error("Failed to get device information")
                return False
                
        except Exception as e:
            error_handler.handle_error(e, "device_connection", {"port": port}, critical=True)
            self.connected = False
            raise DeviceConnectionError(f"Failed to connect to Meshtastic device: {e}")
    
    def _subscribe_to_messages(self):
        """Subscribe to Meshtastic message topics."""
        # Text messages
        pub.subscribe(self._on_text_message, "meshtastic.receive.text")
        
        # Position updates
        pub.subscribe(self._on_position, "meshtastic.receive.position")
        
        # Node info updates
        pub.subscribe(self._on_node_info, "meshtastic.receive.nodeinfo")
        
        # Telemetry data
        pub.subscribe(self._on_telemetry, "meshtastic.receive.telemetry")
        
        # Connection events
        pub.subscribe(self._on_connection_lost, "meshtastic.connection.lost")
        pub.subscribe(self._on_connection_established, "meshtastic.connection.established")
        
        # Generic packet handler for all messages
        pub.subscribe(self._on_packet, "meshtastic.receive")
    
    def _on_text_message(self, packet, interface):
        """Handle incoming text messages."""
        try:
            message_data = {
                "type": "text",
                "from": packet.get("fromId", "unknown"),
                "to": packet.get("toId", "all"),
                "text": packet.get("decoded", {}).get("text", ""),
                "channel": packet.get("channel", 0),
                "timestamp": datetime.now().isoformat(),
                "rssi": packet.get("rxRssi"),
                "snr": packet.get("rxSnr"),
                "hop_limit": packet.get("hopLimit"),
                "raw": packet
            }
            
            logger.info(f"Text message from {message_data['from']}: {message_data['text']}")
            self._emit_message("text", message_data)
            
        except Exception as e:
            error_handler.handle_error(e, "text_message_handler", {"packet": packet})
    
    def _on_position(self, packet, interface):
        """Handle position updates."""
        try:
            position = packet.get("decoded", {}).get("position", {})
            position_data = {
                "type": "position",
                "from": packet.get("fromId", "unknown"),
                "latitude": position.get("latitudeI", 0) / 1e7,
                "longitude": position.get("longitudeI", 0) / 1e7,
                "altitude": position.get("altitude", 0),
                "timestamp": datetime.now().isoformat(),
                "raw": packet
            }
            
            logger.debug(f"Position update from {position_data['from']}: {position_data['latitude']}, {position_data['longitude']}")
            self._emit_message("position", position_data)
            
        except Exception as e:
            logger.error(f"Error handling position update: {e}")
    
    def _on_node_info(self, packet, interface):
        """Handle node info updates."""
        try:
            user = packet.get("decoded", {}).get("user", {})
            node_data = {
                "type": "nodeinfo",
                "node_id": packet.get("fromId", "unknown"),
                "long_name": user.get("longName", ""),
                "short_name": user.get("shortName", ""),
                "hw_model": user.get("hwModel", ""),
                "role": user.get("role", ""),
                "timestamp": datetime.now().isoformat(),
                "raw": packet
            }
            
            logger.info(f"Node info update: {node_data['long_name']} ({node_data['node_id']})")
            self._emit_message("nodeinfo", node_data)
            
        except Exception as e:
            logger.error(f"Error handling node info: {e}")
    
    def _on_telemetry(self, packet, interface):
        """Handle telemetry data."""
        try:
            telemetry = packet.get("decoded", {}).get("telemetry", {})
            telemetry_data = {
                "type": "telemetry",
                "from": packet.get("fromId", "unknown"),
                "battery_level": telemetry.get("deviceMetrics", {}).get("batteryLevel"),
                "voltage": telemetry.get("deviceMetrics", {}).get("voltage"),
                "air_util_tx": telemetry.get("deviceMetrics", {}).get("airUtilTx"),
                "channel_utilization": telemetry.get("deviceMetrics", {}).get("channelUtilization"),
                "temperature": telemetry.get("environmentMetrics", {}).get("temperature"),
                "humidity": telemetry.get("environmentMetrics", {}).get("relativeHumidity"),
                "pressure": telemetry.get("environmentMetrics", {}).get("barometricPressure"),
                "timestamp": datetime.now().isoformat(),
                "raw": packet
            }
            
            logger.debug(f"Telemetry from {telemetry_data['from']}: Battery {telemetry_data['battery_level']}%")
            self._emit_message("telemetry", telemetry_data)
            
        except Exception as e:
            logger.error(f"Error handling telemetry: {e}")
    
    def _on_packet(self, packet, interface):
        """Handle any packet (for logging all traffic)."""
        try:
            packet_data = {
                "type": "packet",
                "from": packet.get("fromId", "unknown"),
                "to": packet.get("toId", "all"),
                "port_num": packet.get("decoded", {}).get("portnum"),
                "channel": packet.get("channel", 0),
                "timestamp": datetime.now().isoformat(),
                "raw": packet
            }
            
            self._emit_message("packet", packet_data)
            
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    def _on_connection_lost(self, interface):
        """Handle connection lost event."""
        logger.warning("Connection to Meshtastic device lost")
        self.connected = False
        self._emit_message("connection", {"status": "lost", "timestamp": datetime.now().isoformat()})
        
        # Start reconnection task
        if not self._reconnect_task or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect())
    
    def _on_connection_established(self, interface):
        """Handle connection established event."""
        logger.info("Connection to Meshtastic device established")
        self.connected = True
        self._emit_message("connection", {"status": "established", "timestamp": datetime.now().isoformat()})
    
    async def _reconnect(self):
        """Attempt to reconnect to the device."""
        retry_count = 0
        max_retries = 10
        
        while not self.connected and retry_count < max_retries:
            retry_count += 1
            wait_time = min(30, 2 ** retry_count)  # Exponential backoff, max 30 seconds
            
            logger.info(f"Attempting to reconnect (attempt {retry_count}/{max_retries}) in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            
            if await self.connect():
                logger.info("Successfully reconnected to Meshtastic device")
                break
        
        if not self.connected:
            logger.error(f"Failed to reconnect after {max_retries} attempts")
    
    def _emit_message(self, message_type: str, data: Dict[str, Any]):
        """Emit message to registered handlers."""
        handlers = self._message_handlers.get(message_type, [])
        handlers.extend(self._message_handlers.get("*", []))  # Wildcard handlers
        
        for handler in handlers:
            try:
                # Check if handler is async
                if asyncio.iscoroutinefunction(handler):
                    # Try to get the current event loop
                    try:
                        loop = asyncio.get_running_loop()
                        asyncio.create_task(handler(message_type, data))
                    except RuntimeError:
                        # No running loop, call synchronously (best effort)
                        asyncio.run(handler(message_type, data))
                else:
                    # Synchronous handler
                    handler(message_type, data)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler for a specific message type or '*' for all."""
        if message_type not in self._message_handlers:
            self._message_handlers[message_type] = []
        self._message_handlers[message_type].append(handler)
    
    async def send_text(self, text: str, channel: int = 0, destination: str = "^all") -> bool:
        """Send a text message."""
        try:
            if not self.connected or not self.interface:
                logger.error("Not connected to device")
                return False
            
            self.interface.sendText(text, destinationId=destination, channelIndex=channel)
            logger.info(f"Sent text message to {destination} on channel {channel}: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
            return False
    
    async def get_nodes(self) -> Dict[str, Any]:
        """Get all known nodes."""
        try:
            if not self.connected or not self.interface:
                return {}
            
            nodes = {}
            for node_id, node in self.interface.nodes.items():
                nodes[node_id] = {
                    "id": node_id,
                    "user": node.get("user", {}),
                    "position": node.get("position", {}),
                    "lastHeard": node.get("lastHeard"),
                    "snr": node.get("snr"),
                    "deviceMetrics": node.get("deviceMetrics", {})
                }
            
            return nodes
            
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            return {}
    
    def _debug_output(self, msg: str):
        """Debug output handler."""
        logger.debug(f"[Meshtastic Debug] {msg}")
    
    async def disconnect(self):
        """Disconnect from the device."""
        try:
            if self.interface:
                self.interface.close()
                self.interface = None
            
            self.connected = False
            logger.info("Disconnected from Meshtastic device")
            
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")


# Global device instance
device = MeshtasticDevice()