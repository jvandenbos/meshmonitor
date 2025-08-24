"""Playwright tests for Streamlit dashboard."""

import pytest
from playwright.sync_api import Page, expect
import time
import subprocess
import os
import signal


@pytest.fixture(scope="module")
def dashboard_server():
    """Start and stop the dashboard server for testing."""
    # Start the dashboard
    env = os.environ.copy()
    env["PATH"] = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/venv/bin:" + env["PATH"]
    
    process = subprocess.Popen(
        ["streamlit", "run", "dashboard.py", "--server.port", "8502", "--server.headless", "true"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    yield "http://localhost:8502"
    
    # Stop the server
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=5)


def test_dashboard_loads(page: Page, dashboard_server):
    """Test that the dashboard loads successfully."""
    page.goto(dashboard_server)
    
    # Check title is present
    expect(page).to_have_title("Meshtastic Monitor")
    
    # Check main header is visible
    header = page.get_by_role("heading", name="📡 Meshtastic Network Monitor")
    expect(header).to_be_visible()
    
    # Check connection status is shown
    # Could be either Connected or Disconnected
    status = page.locator("text=/Connected|Disconnected/")
    expect(status).to_be_visible()


def test_view_modes(page: Page, dashboard_server):
    """Test switching between different view modes."""
    page.goto(dashboard_server)
    
    # Check Split View is default
    split_view = page.get_by_label("Split View")
    expect(split_view).to_be_checked()
    
    # Switch to Messages Only
    messages_only = page.get_by_label("Messages Only")
    messages_only.click()
    
    # Check Messages header is visible
    messages_header = page.get_by_role("heading", name="📨 Message Traffic")
    expect(messages_header).to_be_visible()
    
    # Switch to Nodes Only
    nodes_only = page.get_by_label("Nodes Only")
    nodes_only.click()
    
    # Check Nodes header is visible
    nodes_header = page.get_by_role("heading", name="🌐 Network Nodes")
    expect(nodes_header).to_be_visible()
    
    # Switch to Map View
    map_view = page.get_by_label("Map View")
    map_view.click()
    
    # Check Map header is visible
    map_header = page.get_by_role("heading", name="🗺️ Node Map")
    expect(map_header).to_be_visible()


def test_sidebar_controls(page: Page, dashboard_server):
    """Test sidebar controls are present."""
    page.goto(dashboard_server)
    
    # Check Controls header
    controls_header = page.get_by_role("heading", name="⚙️ Controls")
    expect(controls_header).to_be_visible()
    
    # Check Auto Refresh checkbox
    auto_refresh = page.get_by_label("Auto Refresh (5s)")
    expect(auto_refresh).to_be_visible()
    
    # Check Filters section
    filters_header = page.get_by_role("heading", name="🔍 Filters")
    expect(filters_header).to_be_visible()
    
    # Check Message Type filter
    message_filter = page.get_by_label("Message Type")
    expect(message_filter).to_be_visible()
    
    # Check Send Message section
    send_header = page.get_by_role("heading", name="📤 Send Message")
    expect(send_header).to_be_visible()
    
    # Check message input field
    message_input = page.get_by_label("Message")
    expect(message_input).to_be_visible()
    
    # Check channel input
    channel_input = page.get_by_label("Channel")
    expect(channel_input).to_be_visible()
    
    # Check Send button
    send_button = page.get_by_role("button", name="Send")
    expect(send_button).to_be_visible()
    
    # Check Statistics section
    stats_header = page.get_by_role("heading", name="📊 Statistics")
    expect(stats_header).to_be_visible()


def test_message_type_filter(page: Page, dashboard_server):
    """Test message type filtering."""
    page.goto(dashboard_server)
    
    # Open message type filter dropdown
    filter_dropdown = page.get_by_label("Message Type")
    filter_dropdown.click()
    
    # Check filter options are available
    expect(page.get_by_text("All")).to_be_visible()
    expect(page.get_by_text("text")).to_be_visible()
    expect(page.get_by_text("position")).to_be_visible()
    expect(page.get_by_text("nodeinfo")).to_be_visible()
    expect(page.get_by_text("telemetry")).to_be_visible()
    expect(page.get_by_text("packet")).to_be_visible()
    
    # Select text filter
    page.get_by_text("text", exact=True).click()
    
    # Verify filter is applied (checking the select value)
    expect(filter_dropdown).to_have_value("1")  # "text" is at index 1


def test_metrics_display(page: Page, dashboard_server):
    """Test that metrics are displayed."""
    page.goto(dashboard_server)
    
    # Check Nodes metric is displayed
    nodes_metric = page.locator("text=/Nodes/").first
    expect(nodes_metric).to_be_visible()
    
    # Check Messages metric is displayed  
    messages_metric = page.locator("text=/Messages/").first
    expect(messages_metric).to_be_visible()


def test_send_message_validation(page: Page, dashboard_server):
    """Test message sending validation."""
    page.goto(dashboard_server)
    
    # Try to send empty message
    send_button = page.get_by_role("button", name="Send")
    send_button.click()
    
    # Message should not be sent (no success message)
    success_message = page.locator("text=Message sent!")
    expect(success_message).not_to_be_visible()
    
    # Enter a message
    message_input = page.get_by_label("Message")
    message_input.fill("Test message from Playwright")
    
    # Click send
    send_button.click()
    
    # Check for success message (if connected) or just that it didn't error
    # Note: Success depends on device connection status
    # We're just testing the UI works, not the actual sending


def test_responsive_layout(page: Page, dashboard_server):
    """Test dashboard responsiveness."""
    page.goto(dashboard_server)
    
    # Test desktop view
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    # In desktop, split view should show two columns
    split_view = page.get_by_label("Split View")
    split_view.click()
    
    # Both message and node sections should be visible
    expect(page.get_by_role("heading", name="📨 Message Traffic")).to_be_visible()
    expect(page.get_by_role("heading", name="🌐 Network Nodes")).to_be_visible()
    
    # Test mobile view
    page.set_viewport_size({"width": 375, "height": 667})
    
    # Content should still be accessible (may be stacked)
    expect(page.get_by_role("heading", name="📡 Meshtastic Network Monitor")).to_be_visible()


def test_proximity_sorting_toggle(page: Page, dashboard_server):
    """Test proximity sorting checkbox in Nodes view."""
    page.goto(dashboard_server)
    
    # Switch to Split View to see the checkbox
    split_view = page.get_by_label("Split View")
    split_view.click()
    
    # Check proximity sorting checkbox exists
    proximity_checkbox = page.get_by_label("Sort by proximity")
    expect(proximity_checkbox).to_be_visible()
    
    # Toggle it
    initial_state = proximity_checkbox.is_checked()
    proximity_checkbox.click()
    
    # Verify state changed
    expect(proximity_checkbox).to_have_attribute("aria-checked", str(not initial_state).lower())


def test_auto_refresh_toggle(page: Page, dashboard_server):
    """Test auto-refresh functionality."""
    page.goto(dashboard_server)
    
    # Check auto-refresh checkbox
    auto_refresh = page.get_by_label("Auto Refresh (5s)")
    expect(auto_refresh).to_be_visible()
    
    # Should be checked by default
    expect(auto_refresh).to_be_checked()
    
    # Uncheck it
    auto_refresh.click()
    expect(auto_refresh).not_to_be_checked()
    
    # Re-check it
    auto_refresh.click()
    expect(auto_refresh).to_be_checked()