"""Simplified Playwright tests for Streamlit dashboard."""

import pytest
from playwright.sync_api import Page, expect
import time
import subprocess
import os
import signal


@pytest.fixture(scope="module")
def dashboard_server():
    """Start and stop the dashboard server for testing."""
    # Dashboard is already running on port 8501
    yield "http://localhost:8501"


def test_dashboard_loads(page: Page, dashboard_server):
    """Test that the dashboard loads successfully."""
    page.goto(dashboard_server)
    
    # Check title is present
    expect(page).to_have_title("Meshtastic Monitor")
    
    # Check main header is visible
    header = page.locator("text=📡 Meshtastic Network Monitor")
    expect(header).to_be_visible()
    
    # Check connection status is shown
    # Could be either Connected or Disconnected
    status = page.locator("text=/Connected|Disconnected/")
    expect(status).to_be_visible()


def test_view_switching(page: Page, dashboard_server):
    """Test that view switching works."""
    page.goto(dashboard_server)
    page.wait_for_timeout(2000)
    
    # Check that we can see the view mode selector
    view_selector = page.locator("text=View Mode")
    expect(view_selector).to_be_visible()
    
    # Click on Messages Only
    page.locator("text=Messages Only").click()
    page.wait_for_timeout(1000)
    
    # Verify Messages header appears
    messages_header = page.locator("text=📨 Message Traffic")
    expect(messages_header).to_be_visible()


def test_sidebar_present(page: Page, dashboard_server):
    """Test that sidebar controls are present."""
    page.goto(dashboard_server)
    page.wait_for_timeout(1000)
    
    # Check key sidebar elements
    expect(page.locator("text=⚙️ Controls")).to_be_visible()
    expect(page.locator("text=🔍 Filters")).to_be_visible()
    expect(page.locator("text=📤 Send Message")).to_be_visible()
    expect(page.locator("text=📊 Statistics")).to_be_visible()


def test_metrics_display(page: Page, dashboard_server):
    """Test that metrics are displayed."""
    page.goto(dashboard_server)
    page.wait_for_timeout(1000)
    
    # Check Nodes and Messages metrics are shown
    nodes_text = page.locator("text=/Nodes/")
    expect(nodes_text.first).to_be_visible()
    
    messages_text = page.locator("text=/Messages/")
    expect(messages_text.first).to_be_visible()


def test_auto_refresh_toggle(page: Page, dashboard_server):
    """Test auto-refresh checkbox exists."""
    page.goto(dashboard_server)
    page.wait_for_timeout(1000)
    
    # Check auto-refresh option is present
    auto_refresh = page.locator("text=Auto Refresh")
    expect(auto_refresh).to_be_visible()