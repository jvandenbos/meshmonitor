#!/usr/bin/env python3
"""Streamlit dashboard for Meshtastic monitoring - FIXED VERSION."""

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
from app.device.hop_tracker import hop_tracker

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

def get_theme_css(theme: str = "dark") -> str:
    """Get CSS for the selected theme."""
    if theme == "light":
        return """
        <style>
            .stApp {
                background-color: #FFFFFF;
            }
            /* Light theme text colors */
            h1, h2, h3, h4, h5, h6 {
                color: #1F1F1F !important;
                opacity: 1 !important;
            }
            .element-container h1, .element-container h2, .element-container h3 {
                color: #1F1F1F !important;
            }
            .message-box {
                background-color: #F8F9FA;
                border: 1px solid #0080FF44;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
                color: #1F1F1F;
            }
            .node-card {
                background-color: #F8F9FA;
                border: 1px solid #00AA0044;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
                color: #1F1F1F;
            }
            .node-card strong {
                color: #1F1F1F !important;
                font-weight: bold;
            }
            .stat-box {
                background-color: #F0F2F6;
                border: 1px solid #9333EA44;
                border-radius: 5px;
                padding: 15px;
                text-align: center;
            }
            .online-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background-color: #00AA00;
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
            .signal-bar-container {
                display: inline-block;
                width: 100%;
                max-width: 200px;
                height: 12px;
                background: linear-gradient(to right, 
                    #FF000022 0%, #FF000022 25%,
                    #FFA50022 25%, #FFA50022 50%,
                    #FFD70022 50%, #FFD70022 75%,
                    #00AA0022 75%, #00AA0022 100%);
                border: 1px solid #00AA0066;
                border-radius: 6px;
                position: relative;
                overflow: hidden;
                margin: 4px 0;
            }
            .signal-bar-fill {
                height: 100%;
                background: linear-gradient(to right, #FF0000, #FFA500, #FFD700, #00AA00);
                border-radius: 5px;
                transition: width 0.3s ease;
                box-shadow: 0 0 8px currentColor;
            }
            .signal-value {
                position: absolute;
                right: 8px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 10px;
                font-weight: bold;
                color: #1F1F1F;
                text-shadow: 0 0 4px #FFFFFF;
                z-index: 10;
            }
            .signal-label {
                display: inline-block;
                margin-left: 8px;
                font-size: 11px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 3px;
            }
            .signal-excellent {
                color: #00AA00;
                background: #00AA0022;
            }
            .signal-good {
                color: #FFB000;
                background: #FFB00022;
            }
            .signal-fair {
                color: #FF8000;
                background: #FF800022;
            }
            .signal-poor {
                color: #FF0000;
                background: #FF000022;
            }
            /* Sidebar text fix for light theme */
            .css-1d391kg, .css-1d391kg p {
                color: #1F1F1F !important;
            }
        </style>
        """
    else:  # dark theme (default)
        return """
        <style>
            .stApp {
                background-color: #0A0A0A;
            }
            /* Dark theme text colors */
            h1, h2, h3, h4, h5, h6 {
                color: #FFFFFF !important;
                opacity: 1 !important;
            }
            .element-container h1, .element-container h2, .element-container h3 {
                color: #FFFFFF !important;
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
                color: #FFFFFF;
            }
            .node-card strong {
                color: #FFFFFF !important;
                font-weight: bold;
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
            .signal-bar-container {
                display: inline-block;
                width: 100%;
                max-width: 200px;
                height: 12px;
                background: linear-gradient(to right, 
                    #FF000033 0%, #FF000033 25%,
                    #FFA50033 25%, #FFA50033 50%,
                    #FFD70033 50%, #FFD70033 75%,
                    #39FF1433 75%, #39FF1433 100%);
                border: 1px solid #39FF1444;
                border-radius: 6px;
                position: relative;
                overflow: hidden;
                margin: 4px 0;
            }
            .signal-bar-fill {
                height: 100%;
                background: linear-gradient(to right, #FF0000, #FFA500, #FFD700, #39FF14);
                border-radius: 5px;
                transition: width 0.3s ease;
                box-shadow: 0 0 8px currentColor;
            }
            .signal-value {
                position: absolute;
                right: 8px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 10px;
                font-weight: bold;
                color: #FFFFFF;
                text-shadow: 0 0 4px #000000;
                z-index: 10;
            }
            .signal-label {
                display: inline-block;
                margin-left: 8px;
                font-size: 11px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 3px;
            }
            .signal-excellent {
                color: #39FF14;
                background: #39FF1422;
            }
            .signal-good {
                color: #FFD700;
                background: #FFD70022;
            }
            .signal-fair {
                color: #FFA500;
                background: #FFA50022;
            }
            .signal-poor {
                color: #FF0000;
                background: #FF000022;
            }
        </style>
        """




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


def create_network_graph():
    """Create an interactive radial/radar network graph visualization."""
    import networkx as nx
    import plotly.graph_objects as go
    import math
    import numpy as np
    
    # Get all nodes
    nodes = message_store.get_nodes()
    
    if not nodes:
        st.info("No nodes available for visualization")
        return None
    
    # Get user's node ID if available
    my_node_id = str(device.device_info.get('node_id')) if device.device_info else None
    
    # Organize nodes by hop count
    nodes_by_hop = {}
    max_hops = 0
    
    for node in nodes:
        node_id = node.get('id', 'unknown')
        hops = node.get('hops', -1)
        
        # Handle special cases
        if node_id == my_node_id:
            hop_level = 0  # Center position for our node
        elif hops < 0:
            hop_level = 999  # Unknown nodes go to outer ring
        else:
            hop_level = hops
            if hops < 999:
                max_hops = max(max_hops, hops)
        
        if hop_level not in nodes_by_hop:
            nodes_by_hop[hop_level] = []
        nodes_by_hop[hop_level].append(node)
    
    # Create traces for radial grid lines first
    grid_traces = []
    
    # Add concentric circles for each hop level
    for hop_level in range(max_hops + 2):
        radius = (hop_level + 1) * 2.0
        theta = np.linspace(0, 2 * np.pi, 100)
        x_circle = radius * np.cos(theta)
        y_circle = radius * np.sin(theta)
        
        grid_traces.append(go.Scatter(
            x=x_circle,
            y=y_circle,
            mode='lines',
            line=dict(color='rgba(125, 125, 125, 0.2)', width=1, dash='dot'),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Add radial lines (spokes)
    for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        x_line = [0, (max_hops + 2) * 2.0 * np.cos(angle)]
        y_line = [0, (max_hops + 2) * 2.0 * np.sin(angle)]
        
        grid_traces.append(go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            line=dict(color='rgba(125, 125, 125, 0.1)', width=0.5),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Create radial positions for nodes
    node_positions = {}
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_labels = []
    node_hover = []
    
    # Position our node at center if available
    if my_node_id and 0 in nodes_by_hop:
        my_nodes = [n for n in nodes_by_hop[0] if n['id'] == my_node_id]
        if my_nodes:
            node = my_nodes[0]
            node_positions[node['id']] = (0, 0)
            node_x.append(0)
            node_y.append(0)
            node_colors.append(0)  # Will use colorscale
            node_sizes.append(20)
            
            name = node.get('long_name') or node.get('id', 'unknown')[:8]
            short = node.get('short_name', '')
            if short:
                node_labels.append(short)
            elif name:
                node_labels.append(name[:8] if len(name) > 8 else name)
            else:
                node_labels.append(node.get('id', 'unknown')[:8])
            node_hover.append(f"<b>YOUR NODE</b><br>{name}<br>ID: {node.get('id', 'unknown')[:8]}")
    
    # Position other nodes in concentric circles
    for hop_level in sorted([h for h in nodes_by_hop.keys() if h >= 0 and h < 999]):
        nodes_at_level = nodes_by_hop.get(hop_level, [])
        
        # Skip center node if it's our node
        if hop_level == 0 and my_node_id:
            nodes_at_level = [n for n in nodes_at_level if n['id'] != my_node_id]
        
        if not nodes_at_level:
            continue
            
        radius = (hop_level + 1) * 2.0  # Each hop level gets progressively larger radius
        count = len(nodes_at_level)
        
        for i, node in enumerate(nodes_at_level):
            # Distribute nodes evenly around the circle
            angle = (2 * math.pi * i) / count - math.pi/2  # Start from top
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            node_positions[node['id']] = (x, y)
            node_x.append(x)
            node_y.append(y)
            
            # Create label and hover text
            name = node.get('long_name') or node.get('id', 'unknown')[:8]
            short = node.get('short_name', '')
            hops = node.get('hops', -1)
            rssi = node.get('rssi')
            snr = node.get('snr')
            battery = node.get('battery_level')
            distance = node.get('distance_km')
            
            # Use short name or truncated long name for label
            if short:
                node_labels.append(short)
            elif name:
                node_labels.append(name[:8] if len(name) > 8 else name)
            else:
                node_labels.append(node.get('id', 'unknown')[:8])
            
            # Create detailed hover text
            hover_text = f"<b>{name}</b>"
            hover_text += f"<br>ID: {node.get('id', 'unknown')[:8]}"
            if hops >= 0:
                hover_text += f"<br>Hops: {hops}"
            if rssi is not None:
                hover_text += f"<br>RSSI: {rssi} dBm"
            if snr is not None:
                hover_text += f"<br>SNR: {snr} dB"
            if battery is not None:
                hover_text += f"<br>Battery: {battery}%"
            if distance is not None:
                hover_text += f"<br>Distance: {distance} km"
            
            node_hover.append(hover_text)
            
            # Color value based on hop count (normalized for colorscale)
            if hops >= 0:
                node_colors.append(min(hops / 4.0, 1.0))
            else:
                node_colors.append(1.0)  # Unknown = max color
            
            node_sizes.append(12)
    
    # Handle unknown nodes (place them in outer ring)
    if 999 in nodes_by_hop:
        radius = (max_hops + 2) * 2.0
        unknown_nodes = nodes_by_hop[999]
        count = len(unknown_nodes)
        
        for i, node in enumerate(unknown_nodes):
            angle = (2 * math.pi * i) / count - math.pi/2 if count > 0 else 0
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            node_positions[node['id']] = (x, y)
            node_x.append(x)
            node_y.append(y)
            
            name = node.get('long_name') or node.get('id', 'unknown')[:8]
            short = node.get('short_name', '')
            if short:
                node_labels.append(short)
            elif name:
                node_labels.append(name[:8] if len(name) > 8 else name)
            else:
                node_labels.append(node.get('id', 'unknown')[:8])
            node_hover.append(f"<b>{name}</b><br>ID: {node.get('id', 'unknown')[:8]}<br>Hops: Unknown")
            
            node_colors.append(1.0)  # Max color for unknown
            node_sizes.append(10)
    
    # Create edge traces connecting nodes between hop levels
    edge_x = []
    edge_y = []
    
    # Connect nodes from each hop level to adjacent levels
    for hop_level in sorted([h for h in nodes_by_hop.keys() if h >= 0 and h < 999]):
        next_hop = hop_level + 1
        if next_hop in nodes_by_hop and next_hop < 999:
            # Connect some nodes between levels for visual clarity
            current_nodes = nodes_by_hop[hop_level]
            next_nodes = nodes_by_hop[next_hop]
            
            # Limit connections to avoid clutter
            for curr_node in current_nodes[:5]:  # Limit to first 5 nodes
                if curr_node['id'] in node_positions:
                    x0, y0 = node_positions[curr_node['id']]
                    for next_node in next_nodes[:3]:  # Connect to up to 3 nodes in next level
                        if next_node['id'] in node_positions:
                            x1, y1 = node_positions[next_node['id']]
                            edge_x.extend([x0, x1, None])
                            edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=1, color='rgba(125, 125, 125, 0.3)'),
        hoverinfo='none',
        showlegend=False
    )
    
    # Create node trace with colorscale
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale=[
                [0, 'green'],
                [0.25, 'yellowgreen'],
                [0.5, 'yellow'],
                [0.75, 'orange'],
                [1, 'red']
            ],
            showscale=True,
            colorbar=dict(
                thickness=15,
                title="Hop Distance",
                xanchor='left',
                titleside='right',
                tickmode='array',
                tickvals=[0, 0.25, 0.5, 0.75, 1],
                ticktext=['0', '1', '2', '3', '4+']
            ),
            line=dict(color='white', width=2)
        ),
        text=node_labels,
        textposition='top center',
        textfont=dict(size=9),
        hoverinfo='text',
        hovertext=node_hover,
        showlegend=False
    )
    
    # Add hop level annotations
    annotations = []
    for hop_level in range(min(max_hops + 1, 5)):  # Limit to 5 levels for clarity
        if hop_level == 0:
            continue  # Skip center
        radius = (hop_level + 1) * 2.0
        annotations.append(dict(
            x=0,
            y=-radius - 0.3,
            text=f"{hop_level} hop{'s' if hop_level != 1 else ''}",
            showarrow=False,
            font=dict(size=10, color='gray'),
            xanchor='center'
        ))
    
    # Create figure with all traces
    all_traces = grid_traces + [edge_trace, node_trace]
    fig = go.Figure(data=all_traces)
    
    # Calculate plot range
    plot_range = (max_hops + 2) * 2.2 if max_hops > 0 else 10
    
    # Update layout with enhanced interactivity
    fig.update_layout(
        title='<b>Network Topology - Radar View</b>',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=annotations,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-plot_range, plot_range],
            fixedrange=False  # Allow zooming on x-axis
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-plot_range, plot_range],
            scaleanchor='x',
            scaleratio=1,
            fixedrange=False  # Allow zooming on y-axis
        ),
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        dragmode='pan',  # Default to pan mode
        clickmode='event+select',
        modebar=dict(
            orientation='v',
            bgcolor='rgba(255, 255, 255, 0.7)'
        )
    )
    
    # Enable wheel zoom
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)
    
    return fig


def show_node_details(node_id: str):
    """Show detailed information for a specific node."""
    node = message_store.get_node(node_id)
    if not node:
        st.error(f"Node {node_id} not found")
        return
    
    # Node header
    st.header(f"📡 Node Details: {node.get('long_name', node_id)}")
    
    # Basic info in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Node ID", node.get('id', 'Unknown'))
        st.metric("Short Name", node.get('short_name', 'N/A'))
        if node.get('hw_model'):
            st.metric("Hardware", node.get('hw_model'))
    
    with col2:
        st.metric("First Seen", format_time_ago(node.get('first_seen', '')))
        st.metric("Last Seen", format_time_ago(node.get('last_seen', '')))
        if node.get('hops') is not None:
            st.metric("Hop Count", node.get('hops', 'Unknown'))
    
    with col3:
        if node.get('battery_level'):
            st.metric("Battery", f"{node.get('battery_level')}%")
        if node.get('rssi'):
            st.metric("RSSI", f"{node.get('rssi')} dBm")
        if node.get('snr'):
            st.metric("SNR", f"{node.get('snr')} dB")
    
    # Signal strength bar if available
    if node.get('rssi'):
        st.markdown("### Signal Strength")
        signal_html = create_signal_bar(node.get('rssi'), node.get('snr'))
        st.markdown(signal_html, unsafe_allow_html=True)
    
    # Position info if available
    if node.get('latitude') and node.get('longitude'):
        st.markdown("### 📍 Position")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latitude", f"{node.get('latitude', 0):.6f}")
        with col2:
            st.metric("Longitude", f"{node.get('longitude', 0):.6f}")
        with col3:
            if node.get('altitude'):
                st.metric("Altitude", f"{node.get('altitude', 0):.1f} m")
            if node.get('distance_km'):
                st.metric("Distance", f"{node.get('distance_km', 0):.2f} km")
    
    # Tabs for different data views
    tab1, tab2, tab3 = st.tabs(["📊 Metrics History", "💬 Messages", "📈 Graphs"])
    
    with tab1:
        st.subheader("Historical Metrics (Last 24 Hours)")
        history = message_store.get_node_history(node_id, hours=24)
        
        if history:
            # Convert to DataFrame for display
            import pandas as pd
            df = pd.DataFrame(history)
            if not df.empty:
                # Format timestamp
                df['recorded_at'] = pd.to_datetime(df['recorded_at'])
                df = df.sort_values('recorded_at', ascending=False)
                
                # Display relevant columns
                display_cols = ['recorded_at', 'rssi', 'snr', 'battery_level', 'hops']
                display_cols = [col for col in display_cols if col in df.columns]
                
                st.dataframe(
                    df[display_cols].head(50),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No historical data available for this node")
    
    with tab2:
        st.subheader("Recent Messages")
        # Get messages from this node
        all_messages = message_store.get_messages(limit=100)
        node_messages = [msg for msg in all_messages if msg.get('from') == node_id]
        
        if node_messages:
            for msg in node_messages[:20]:  # Show last 20 messages
                msg_type = msg.get('type', 'unknown')
                timestamp = format_timestamp(msg.get('timestamp', ''))
                
                if msg_type == 'text':
                    st.markdown(f"**💬 {timestamp}**: {msg.get('text', '')}")
                else:
                    st.markdown(f"**📦 {msg_type.upper()}** at {timestamp}")
        else:
            st.info("No messages from this node")
    
    with tab3:
        st.subheader("Signal & Battery Trends")
        history = message_store.get_node_history(node_id, hours=24)
        
        if history and len(history) > 1:
            import pandas as pd
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            df = pd.DataFrame(history)
            df['recorded_at'] = pd.to_datetime(df['recorded_at'])
            df = df.sort_values('recorded_at')
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Signal Strength (RSSI)', 'Battery Level'),
                vertical_spacing=0.15
            )
            
            # RSSI plot
            if 'rssi' in df.columns and df['rssi'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df['recorded_at'],
                        y=df['rssi'],
                        mode='lines+markers',
                        name='RSSI',
                        line=dict(color='#00FFFF', width=2),
                        marker=dict(size=6)
                    ),
                    row=1, col=1
                )
            
            # Battery plot
            if 'battery_level' in df.columns and df['battery_level'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=df['recorded_at'],
                        y=df['battery_level'],
                        mode='lines+markers',
                        name='Battery %',
                        line=dict(color='#39FF14', width=2),
                        marker=dict(size=6)
                    ),
                    row=2, col=1
                )
            
            # Update layout based on theme
            bg_color = '#FFFFFF' if st.session_state.theme == 'light' else '#0A0A0A'
            text_color = '#1F1F1F' if st.session_state.theme == 'light' else '#FFFFFF'
            grid_color = '#E0E0E0' if st.session_state.theme == 'light' else '#333333'
            
            fig.update_layout(
                height=500,
                showlegend=False,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=text_color)
            )
            
            fig.update_xaxes(gridcolor=grid_color)
            fig.update_yaxes(gridcolor=grid_color)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough historical data for graphs (need at least 2 data points)")
    
    # Close button
    if st.button("← Back to Node List", type="secondary"):
        st.session_state.show_node_details = False
        st.session_state.selected_node = None
        st.rerun()


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


def create_signal_bar(rssi, snr=None):
    """Create a horizontal signal strength bar with gradient colors."""
    if not rssi:
        return ""
    
    # Calculate percentage (RSSI typically ranges from -120 to -30 dBm)
    # Map to 0-100% where -120 = 0% and -30 = 100%
    percentage = max(0, min(100, ((rssi + 120) / 90) * 100))
    
    # Determine signal quality
    if rssi > -60:
        quality = "Excellent"
        label_class = "signal-excellent"
    elif rssi > -75:
        quality = "Good"
        label_class = "signal-good"
    elif rssi > -85:
        quality = "Fair"
        label_class = "signal-fair"
    else:
        quality = "Poor"
        label_class = "signal-poor"
    
    # Build the signal bar HTML
    snr_text = f" / {snr:.1f}dB SNR" if snr else ""
    
    return f'<div style="margin: 8px 0;"><div class="signal-bar-container"><div class="signal-bar-fill" style="width: {percentage:.0f}%;"></div><span class="signal-value">{rssi}dBm{snr_text}</span></div><span class="signal-label {label_class}">{quality}</span></div>'


def main():
    """Main dashboard function."""
    
    # Initialize session state
    if "service_started" not in st.session_state:
        st.session_state.service_started = False
    
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = None
    
    if "show_node_details" not in st.session_state:
        st.session_state.show_node_details = False
    
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"  # Default to dark theme
    
    # Apply theme CSS
    st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
    
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
        
        # Theme selector at the top
        st.subheader("🎨 Theme")
        theme_options = ["🌙 Dark", "☀️ Light"]
        current_theme_index = 0 if st.session_state.theme == "dark" else 1
        selected_theme = st.radio(
            "Choose theme",
            theme_options,
            index=current_theme_index,
            key="theme_selector"
        )
        
        # Update theme if changed
        new_theme = "dark" if selected_theme == "🌙 Dark" else "light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
        
        st.divider()
        
        # View selector
        view = st.radio(
            "View Mode",
            ["Split View", "Messages Only", "Nodes Only", "Map View", "Network Graph"],
            index=0
        )
        
        # Auto-refresh
        auto_refresh = st.checkbox("Auto Refresh (5s)", value=True)
        
        # Message filters
        st.header("🔍 Filters")
        message_type_filter = st.selectbox(
            "Message Type",
            ["All", "text", "position", "nodeinfo", "telemetry", "packet"],
            index=0
        )
        
        # Send message
        st.header("📤 Send Message")
        
        # Add test mode toggle
        test_mode = st.checkbox("Test Mode (Channel 7)", value=True,
                               help="When enabled, messages are sent on Channel 7 for testing")
        
        message_text = st.text_input("Message")
        
        if test_mode:
            channel = 7
            st.info("🧪 Test Mode: Messages will be sent on Channel 7")
        else:
            channel = st.number_input("Channel", min_value=0, max_value=7, value=0,
                                    help="Select channel 0-7. Channel 0 is the default public channel.")
        
        # Show current channel
        st.caption(f"Will send on Channel {channel}")
        
        if st.button("Send", type="primary"):
            if message_text:
                # Add test prefix if in test mode
                if test_mode:
                    message_text = f"[TEST] {message_text}"
                
                success = asyncio.run(device.send_text(message_text, channel))
                if success:
                    st.success(f"✅ Message sent on Channel {channel}!")
                else:
                    st.error("❌ Failed to send message - check device connection")
        
        # Stats
        st.header("📊 Statistics")
        for msg_type, count in stats["message_types"].items():
            st.text(f"{msg_type}: {count}")
        
        # Database Persistence Stats
        st.header("💾 Database Persistence")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("DB Nodes", stats.get("db_total_nodes", 0))
            st.metric("Active (24h)", stats.get("db_active_nodes", 0))
        with col2:
            st.metric("DB Messages", stats.get("db_total_messages", 0))
            st.metric("DB Size", f"{stats.get('db_size_mb', 0)} MB")
        
        st.success("✅ Data persisted to SQLite database")
        
        # Hop Tracking Statistics
        st.header("🛣️ Hop Tracking Statistics")
        hop_summary = hop_tracker.get_hop_summary()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Direct Nodes", hop_summary.get("direct_nodes", 0))
            st.metric("Indirect Nodes", hop_summary.get("indirect_nodes", 0))
        with col2:
            st.metric("Unknown Hops", hop_summary.get("unknown_nodes", 0))
            st.metric("Total Tracked", hop_summary.get("total_nodes", 0))
        
        # Hop distribution
        if hop_summary.get("hop_distribution"):
            st.subheader("Hop Distribution")
            for hops, count in sorted(hop_summary["hop_distribution"].items()):
                if hops == 0:
                    st.text(f"Direct (0 hops): {count} nodes")
                else:
                    st.text(f"{hops} hop{'s' if hops > 1 else ''}: {count} nodes")
        
        st.info("""
        **Hop Tracking Active:**
        • All packets are being logged to `logs/`
        • Node updates tracked in `node_updates.log`
        • Hop calculations in `hop_tracker.log`
        • Raw packets in `packets.jsonl`
        
        **Note:** Meshtastic doesn't expose full routing 
        paths, only hop counts and direct neighbor info.
        """)
    
    # Check if we should show node details
    if st.session_state.show_node_details and st.session_state.selected_node:
        show_node_details(st.session_state.selected_node)
        return  # Don't show the normal views
    
    # Main content area - FIXED: Properly structured if/elif blocks
    if view == "Split View":
        col1, col2 = st.columns([1, 1])
        
        # Messages column
        with col1:
            st.header("📨 Message Traffic")
            
            # Get messages
            msg_type = None if message_type_filter == "All" else message_type_filter
            messages = message_store.get_messages(limit=50, message_type=msg_type)
            
            if messages:
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
            else:
                st.info("No messages yet")
        
        # Nodes column
        with col2:
            st.header("🌐 Network Nodes")
            
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                sort_proximity = st.checkbox("Sort by proximity", value=True)
            with col_filter2:
                show_only_with_packets = st.checkbox("Only show nodes with packets", value=True, 
                                                    help="Show only nodes we've received packets from")
            
            # Get nodes
            nodes = message_store.get_nodes(sort_by_proximity=sort_proximity)
            
            # Filter nodes if requested
            if show_only_with_packets:
                # Only show nodes that have hop data (hops >= 0)
                nodes = [n for n in nodes if n.get("hops", -1) >= 0]
            
            if nodes:
                # Show count
                total_nodes = len(message_store.nodes)
                visible_nodes = len(nodes)
                if show_only_with_packets:
                    st.caption(f"Showing {visible_nodes} nodes with packets (out of {total_nodes} total)")
                else:
                    st.caption(f"Showing all {visible_nodes} nodes")
                
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
                    
                    # Get hop and signal info
                    hops = node.get("hops", -1)
                    is_direct = node.get("is_direct", False) or hops == 0
                    rssi = node.get("rssi")
                    snr = node.get("snr")
                    
                    # Simple, clean hop display without nested HTML
                    if is_direct:
                        hop_str = '<span style="background: #00FFFF22; padding: 2px 6px; border-radius: 3px; font-weight: bold;">📡 DIRECT</span>'
                        # Add signal strength bar if available
                        signal_bar = create_signal_bar(rssi, snr) if rssi else ""
                    elif hops >= 0:
                        hop_str = f'<span style="background: #FF00FF22; padding: 2px 6px; border-radius: 3px; font-weight: bold;">↗️ {hops} HOP{"S" if hops != 1 else ""}</span>'
                        # For indirect nodes, show signal bar if we have RSSI
                        signal_bar = create_signal_bar(rssi, snr) if rssi else ""
                    else:
                        hop_str = '<span style="background: #80808022; padding: 2px 6px; border-radius: 3px;">❓ UNKNOWN</span>'
                        signal_bar = ""
                    
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
                    
                    # Simplified node card using Streamlit columns for proper button placement
                    with st.container():
                        col1, col2 = st.columns([5, 1])
                        
                        with col1:
                            # Node information in a clean card
                            card_html = f'<div class="node-card"><strong>{name}</strong> ({short_name})<br>{hop_str}{signal_bar}<div style="color: #8B949E; font-size: 0.9em; margin-top: 5px;">{node_id} • {time_ago}<br>{distance_str} {battery_str} {pos_str}</div></div>'
                            st.markdown(card_html, unsafe_allow_html=True)
                        
                        with col2:
                            # Properly positioned button that's actually clickable
                            st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)  # Spacer
                            if st.button("📊 Details", key=f"node_{node_id}"):
                                st.session_state.selected_node = node_id
                                st.session_state.show_node_details = True
                                st.rerun()
            else:
                st.info("No nodes discovered yet")
    
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
                hops = node.get("hops", "?")
                is_direct = node.get("is_direct", False) or hops == 0
                rssi = node.get("rssi")
                
                # Format connection type
                if is_direct:
                    connection = f"Direct ({rssi}dBm)" if rssi else "Direct"
                elif hops != "?":
                    connection = f"{hops} hop{'s' if hops != 1 else ''}"
                else:
                    connection = "Unknown"
                
                df_data.append({
                    "Name": node.get("long_name", node.get("id")),
                    "ID": node.get("id"),
                    "Short": node.get("short_name", ""),
                    "Connection": connection,
                    "Distance (km)": node.get("distance_km", ""),
                    "Battery (%)": telemetry.get("battery_level", ""),
                    "SNR": node.get("snr", ""),
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
    
    elif view == "Network Graph":
        st.header("🌐 Network Topology")
        
        # Add info about the visualization
        with st.expander("ℹ️ How to read this graph"):
            st.markdown("""
            **Node Colors:**
            - 🟡 **Gold**: Your node (the connected device)
            - 🔵 **Cyan**: Direct connections (0 hops)
            - 🟢 **Green**: 1 hop away
            - 🟡 **Yellow**: 2 hops away
            - 🟠 **Orange**: 3 hops away
            - 🔴 **Red**: 4+ hops away
            - ⚫ **Gray**: Unknown hop count
            
            **Node Size:** Larger nodes are closer to you in the network
            
            **Lines:** Show connections between nodes
            
            **Hover:** Over nodes to see details (name, hops, signal, battery)
            """)
        
        # Create and display the network graph with full interactivity
        fig = create_network_graph()
        if fig:
            # Display with config for enhanced interaction
            config = {
                'displayModeBar': True,  # Always show the modebar
                'displaylogo': False,
                'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'network_topology',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            }
            st.plotly_chart(fig, use_container_width=True, config=config)
            
            # Add instructions for interactivity
            with st.expander("📖 Graph Controls", expanded=False):
                st.markdown("""
                **Interactive Controls:**
                - 🔍 **Zoom**: Scroll or use zoom buttons
                - ✋ **Pan**: Click and drag to move around
                - 🏠 **Reset**: Double-click to reset view
                - 📷 **Save**: Click camera icon to download image
                - 🎯 **Hover**: Point at nodes for details
                """)
            
            # Statistics about the network
            nodes = message_store.get_nodes()
            if nodes:
                col1, col2, col3 = st.columns(3)
                with col1:
                    direct_nodes = sum(1 for n in nodes if n.get('is_direct', False) or n.get('hops', -1) == 0)
                    st.metric("Direct Connections", direct_nodes)
                with col2:
                    multi_hop = sum(1 for n in nodes if n.get('hops', -1) > 0)
                    st.metric("Multi-hop Nodes", multi_hop)
                with col3:
                    max_hops = max((n.get('hops', 0) for n in nodes if n.get('hops', -1) >= 0), default=0)
                    st.metric("Max Hop Distance", max_hops)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()