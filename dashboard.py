#!/usr/bin/env python3
"""Streamlit dashboard for Meshtastic monitoring."""

import streamlit as st
import pandas as pd
import asyncio
import sys
import logging
from datetime import datetime
import folium
from streamlit_folium import st_folium
import time

# Add app to path
sys.path.insert(0, '.')

from app.device.service import meshtastic_service
from app.device.message_store import message_store
from app.device.connection import device

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Meshtastic Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0A0A0A;
    }
    .message-box {
        background-color: #161B22;
        border: 1px solid #00FFFF33;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    .node-card {
        background-color: #161B22;
        border: 1px solid #39FF1433;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
    }
    .stat-box {
        background-color: #0D1117;
        border: 1px solid #FF00FF33;
        border-radius: 5px;
        padding: 15px;
        text-align: center;
    }
    .online-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #39FF14;
        margin-right: 5px;
    }
    .offline-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #FF0000;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)


async def ensure_service_running():
    """Ensure the Meshtastic service is running."""
    if not meshtastic_service.running:
        try:
            await meshtastic_service.start()
        except Exception as e:
            logger.warning(f"Could not connect to device: {e}")
            # Continue anyway - dashboard can work in demo mode


def format_timestamp(timestamp_str):
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%H:%M:%S")
    except:
        return timestamp_str


def format_time_ago(timestamp_str):
    """Format time as 'X minutes ago'."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        delta = datetime.now() - dt
        
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}m ago"
        elif delta.total_seconds() < 86400:
            return f"{int(delta.total_seconds() / 3600)}h ago"
        else:
            return f"{int(delta.total_seconds() / 86400)}d ago"
    except:
        return "unknown"


def main():
    """Main dashboard function."""
    
    # Initialize session state
    if "service_started" not in st.session_state:
        st.session_state.service_started = False
    
    # Start service if not running
    if not st.session_state.service_started:
        with st.spinner("Connecting to Meshtastic device..."):
            try:
                asyncio.run(ensure_service_running())
                st.session_state.service_started = True
                time.sleep(2)  # Give it time to collect initial data
            except Exception as e:
                st.warning(f"Could not connect to device: {e}. Running in demo mode.")
                st.session_state.service_started = True
    
    # Header
    st.title("📡 Meshtastic Network Monitor")
    
    # Connection status
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        if device.connected:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")
    
    # Statistics
    stats = message_store.get_stats()
    with col2:
        st.metric("Nodes", stats["total_nodes"])
    with col3:
        st.metric("Messages", stats["total_messages"])
    with col4:
        if device.device_info:
            st.info(f"Device: {device.device_info.get('node_id', 'Unknown')}")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # View selector
        view = st.radio(
            "View Mode",
            ["Split View", "Messages Only", "Nodes Only", "Map View"],
            index=0
        )
        
        # Auto-refresh
        auto_refresh = st.checkbox("Auto Refresh (5s)", value=True)
        if auto_refresh:
            st.empty()  # Placeholder for auto-refresh
        
        # Message filters
        st.header("🔍 Filters")
        message_type_filter = st.selectbox(
            "Message Type",
            ["All", "text", "position", "nodeinfo", "telemetry", "packet"],
            index=0
        )
        
        # Send message
        st.header("📤 Send Message")
        message_text = st.text_input("Message")
        channel = st.number_input("Channel", min_value=0, max_value=7, value=0)
        if st.button("Send", type="primary"):
            if message_text:
                asyncio.run(device.send_text(message_text, channel))
                st.success("Message sent!")
        
        # Stats
        st.header("📊 Statistics")
        for msg_type, count in stats["message_types"].items():
            st.text(f"{msg_type}: {count}")
    
    # Main content area
    if view == "Split View":
        col1, col2 = st.columns([1, 1])
        
        # Messages column
        with col1:
            st.header("📨 Message Traffic")
            
            # Get messages
            msg_type = None if message_type_filter == "All" else message_type_filter
            messages = message_store.get_messages(limit=50, message_type=msg_type)
            
            # Display messages
            for msg in messages:
                msg_type = msg.get("type", "unknown")
                
                # Color code by type
                if msg_type == "text":
                    emoji = "💬"
                    color = "#00FFFF"
                elif msg_type == "position":
                    emoji = "📍"
                    color = "#FF00FF"
                elif msg_type == "telemetry":
                    emoji = "📊"
                    color = "#39FF14"
                elif msg_type == "nodeinfo":
                    emoji = "ℹ️"
                    color = "#FFD700"
                else:
                    emoji = "📦"
                    color = "#808080"
                
                # Format message
                from_node = msg.get("from", "unknown")
                timestamp = format_timestamp(msg.get("timestamp", ""))
                
                # Create message display
                if msg_type == "text":
                    text = msg.get("text", "")
                    st.markdown(f"""
                    <div class="message-box">
                        <strong style="color: {color}">{emoji} {from_node}</strong> 
                        <span style="color: #8B949E; font-size: 0.9em">{timestamp}</span><br>
                        {text}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message-box">
                        <strong style="color: {color}">{emoji} {msg_type.upper()}</strong> 
                        from {from_node}
                        <span style="color: #8B949E; font-size: 0.9em">{timestamp}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Nodes column
        with col2:
            st.header("🌐 Network Nodes")
            
            # Sort by proximity toggle
            sort_proximity = st.checkbox("Sort by proximity", value=True)
            
            # Get nodes
            nodes = message_store.get_nodes(sort_by_proximity=sort_proximity)
            
            # Display nodes
            for node in nodes:
                node_id = node.get("id", "unknown")
                name = node.get("long_name", node_id)
                short_name = node.get("short_name", "")
                
                # Get status info
                last_updated = node.get("last_updated", "")
                time_ago = format_time_ago(last_updated) if last_updated else "never"
                
                # Get telemetry
                telemetry = node.get("telemetry", {})
                battery = telemetry.get("battery_level")
                
                # Get position
                position = node.get("position", {})
                has_position = bool(position.get("latitude"))
                
                # Distance
                distance = node.get("distance_km")
                distance_str = f"📏 {distance:.1f} km" if distance else ""
                
                # Battery indicator
                battery_str = ""
                if battery:
                    if battery > 75:
                        battery_emoji = "🔋"
                    elif battery > 50:
                        battery_emoji = "🔋"
                    elif battery > 25:
                        battery_emoji = "🪫"
                    else:
                        battery_emoji = "🪫"
                    battery_str = f"{battery_emoji} {battery}%"
                
                # Position indicator
                pos_str = "📍" if has_position else ""
                
                # Node card
                st.markdown(f"""
                <div class="node-card">
                    <strong>{name}</strong> ({short_name})<br>
                    <span style="color: #8B949E; font-size: 0.9em">
                        {node_id} • {time_ago} {distance_str}<br>
                        {battery_str} {pos_str}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    elif view == "Messages Only":
        st.header("📨 Message Traffic")
        
        # Get all messages
        msg_type = None if message_type_filter == "All" else message_type_filter
        messages = message_store.get_messages(limit=100, message_type=msg_type)
        
        # Convert to DataFrame for better display
        if messages:
            df_data = []
            for msg in messages:
                df_data.append({
                    "Time": format_timestamp(msg.get("timestamp", "")),
                    "Type": msg.get("type", "unknown"),
                    "From": msg.get("from", "unknown"),
                    "To": msg.get("to", ""),
                    "Content": msg.get("text", "") if msg.get("type") == "text" else f"[{msg.get('type')} data]",
                    "Channel": msg.get("channel", 0),
                    "RSSI": msg.get("rssi", ""),
                    "SNR": msg.get("snr", "")
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, height=600)
        else:
            st.info("No messages received yet")
    
    elif view == "Nodes Only":
        st.header("🌐 Network Nodes")
        
        # Get all nodes
        nodes = message_store.get_nodes(sort_by_proximity=True)
        
        if nodes:
            # Convert to DataFrame
            df_data = []
            for node in nodes:
                telemetry = node.get("telemetry", {})
                position = node.get("position", {})
                
                df_data.append({
                    "Name": node.get("long_name", node.get("id")),
                    "ID": node.get("id"),
                    "Short": node.get("short_name", ""),
                    "Distance (km)": node.get("distance_km", ""),
                    "Battery (%)": telemetry.get("battery_level", ""),
                    "Latitude": position.get("latitude", ""),
                    "Longitude": position.get("longitude", ""),
                    "Altitude (m)": position.get("altitude", ""),
                    "Last Heard": format_time_ago(node.get("last_updated", "")),
                    "Hardware": node.get("hw_model", ""),
                    "Role": node.get("role", "")
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, height=600)
        else:
            st.info("No nodes discovered yet")
    
    elif view == "Map View":
        st.header("🗺️ Node Map")
        
        # Get nodes with positions
        nodes = message_store.get_nodes()
        nodes_with_pos = [n for n in nodes if "position" in n and n["position"].get("latitude")]
        
        if nodes_with_pos:
            # Create map centered on first node or my position
            if message_store.my_position:
                center_lat = message_store.my_position["latitude"]
                center_lon = message_store.my_position["longitude"]
            else:
                first_node = nodes_with_pos[0]
                center_lat = first_node["position"]["latitude"]
                center_lon = first_node["position"]["longitude"]
            
            # Create folium map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=10,
                tiles="OpenStreetMap"
            )
            
            # Add my position if available
            if message_store.my_position:
                folium.Marker(
                    [message_store.my_position["latitude"], message_store.my_position["longitude"]],
                    popup="My Position",
                    tooltip="My Position",
                    icon=folium.Icon(color="red", icon="home")
                ).add_to(m)
            
            # Add nodes
            for node in nodes_with_pos:
                pos = node["position"]
                name = node.get("long_name", node.get("id"))
                distance = node.get("distance_km")
                telemetry = node.get("telemetry", {})
                battery = telemetry.get("battery_level")
                
                # Create popup text
                popup_text = f"""
                <b>{name}</b><br>
                ID: {node.get("id")}<br>
                """
                if distance:
                    popup_text += f"Distance: {distance:.1f} km<br>"
                if battery:
                    popup_text += f"Battery: {battery}%<br>"
                popup_text += f"Alt: {pos.get('altitude', 0)}m"
                
                # Determine marker color based on battery
                if battery:
                    if battery > 75:
                        color = "green"
                    elif battery > 50:
                        color = "blue"
                    elif battery > 25:
                        color = "orange"
                    else:
                        color = "red"
                else:
                    color = "gray"
                
                folium.Marker(
                    [pos["latitude"], pos["longitude"]],
                    popup=popup_text,
                    tooltip=name,
                    icon=folium.Icon(color=color, icon="signal")
                ).add_to(m)
            
            # Display map
            st_folium(m, height=600, width=None, returned_objects=[])
        else:
            st.info("No nodes with GPS positions yet")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()