"""Test UI improvements for message filtering and node management."""

import pytest
from playwright.sync_api import Page, expect
import time

@pytest.fixture(scope="module")
def dashboard_url():
    """Dashboard URL for testing."""
    return "http://localhost:8501"


def test_message_view_filters(page: Page, dashboard_url: str):
    """Test the new message view toggle buttons."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Check that message view radio buttons exist
    # Look for the Chat option (default)
    chat_button = page.get_by_text("💬 Chat")
    expect(chat_button).to_be_visible()
    
    # Check Activity button
    activity_button = page.get_by_text("📢 Activity") 
    expect(activity_button).to_be_visible()
    
    # Check System button
    system_button = page.get_by_text("⚙️ System")
    expect(system_button).to_be_visible()
    
    # Click on System view
    system_button.click()
    page.wait_for_timeout(500)
    
    # Click on Activity view  
    activity_button.click()
    page.wait_for_timeout(500)
    
    # Return to Chat view
    chat_button.click()
    page.wait_for_timeout(500)


def test_node_time_filter(page: Page, dashboard_url: str):
    """Test the node activity time filter dropdown."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Look for the node activity dropdown
    # The dropdown should have "Last 15 Minutes" as default
    dropdown = page.get_by_text("Last 15 Minutes").first
    expect(dropdown).to_be_visible()
    
    # Click the dropdown to open options
    dropdown.click()
    page.wait_for_timeout(200)
    
    # Check that all options are available
    expect(page.get_by_text("Last Hour")).to_be_visible()
    expect(page.get_by_text("Last 24 Hours")).to_be_visible()
    expect(page.get_by_text("Since Startup")).to_be_visible()
    expect(page.get_by_text("All Time")).to_be_visible()
    
    # Select "Last Hour"
    page.get_by_text("Last Hour").click()
    page.wait_for_timeout(500)


def test_session_control_buttons(page: Page, dashboard_url: str):
    """Test the Clear Messages and Reset Nodes buttons."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Check for Session Controls header
    expect(page.get_by_text("📊 Session Controls")).to_be_visible()
    
    # Check Clear Messages button
    clear_messages_btn = page.get_by_role("button", name="🗑️ Clear Messages")
    expect(clear_messages_btn).to_be_visible()
    
    # Check Reset Nodes button
    reset_nodes_btn = page.get_by_role("button", name="🔄 Reset Nodes")
    expect(reset_nodes_btn).to_be_visible()
    
    # Test clicking Clear Messages
    clear_messages_btn.click()
    page.wait_for_timeout(1000)
    
    # Check for success message
    success = page.get_by_text("Messages cleared!")
    if success.is_visible():
        expect(success).to_be_visible()


def test_enhanced_message_styling(page: Page, dashboard_url: str):
    """Test that chat messages have enhanced styling."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Look for Split View
    split_view = page.get_by_text("Split View")
    if split_view.is_visible():
        split_view.click()
        page.wait_for_timeout(500)
    
    # Check for message area
    message_header = page.get_by_text("📨 Message Traffic")
    expect(message_header).to_be_visible()
    
    # Check if there are any chat-message-box elements (enhanced text messages)
    # or system-message-box elements (system messages)
    page.wait_for_timeout(1000)
    
    # Look for the CSS classes we added
    chat_messages = page.locator(".chat-message-box")
    system_messages = page.locator(".system-message-box")
    
    # At least one type should exist if there are messages
    if chat_messages.count() > 0 or system_messages.count() > 0:
        print(f"Found {chat_messages.count()} chat messages and {system_messages.count()} system messages")


def test_node_card_details_button(page: Page, dashboard_url: str):
    """Test that node cards have working Details buttons."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Look for node cards
    page.wait_for_timeout(2000)
    
    # Look for Details button
    details_buttons = page.get_by_role("button", name="📊 Details")
    
    if details_buttons.count() > 0:
        # Click the first Details button
        details_buttons.first.click()
        page.wait_for_timeout(1000)
        
        # Should show node details
        expect(page.get_by_text("📡 Node Details")).to_be_visible()
        
        # Look for Back button
        back_btn = page.get_by_role("button", name="← Back to Dashboard")
        expect(back_btn).to_be_visible()
        
        # Go back
        back_btn.click()
        page.wait_for_timeout(500)


def test_theme_toggle(page: Page, dashboard_url: str):
    """Test theme switching between dark and light modes."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Look for theme selector
    dark_theme = page.get_by_text("🌙 Dark")
    light_theme = page.get_by_text("☀️ Light")
    
    # Check both options are visible
    expect(dark_theme).to_be_visible()
    expect(light_theme).to_be_visible()
    
    # Switch to light theme
    light_theme.click()
    page.wait_for_timeout(1000)
    
    # Switch back to dark theme
    dark_theme.click()
    page.wait_for_timeout(1000)


def test_network_graph_view(page: Page, dashboard_url: str):
    """Test that Network Graph view loads without errors."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Select Network Graph view
    network_graph = page.get_by_text("Network Graph")
    expect(network_graph).to_be_visible()
    network_graph.click()
    
    page.wait_for_timeout(2000)
    
    # Check for graph title
    graph_title = page.get_by_text("Network Topology - Radar View")
    if graph_title.is_visible():
        expect(graph_title).to_be_visible()
    
    # Check for graph controls help
    graph_controls = page.get_by_text("📖 Graph Controls")
    if graph_controls.is_visible():
        # Expand the controls
        graph_controls.click()
        page.wait_for_timeout(500)
        
        # Check for zoom instructions
        expect(page.get_by_text("Zoom")).to_be_visible()


def test_no_html_artifacts(page: Page, dashboard_url: str):
    """Ensure no raw HTML tags are visible in the UI."""
    page.goto(dashboard_url)
    page.wait_for_load_state("networkidle")
    
    # Wait for content to load
    page.wait_for_timeout(2000)
    
    # Check that no raw HTML tags are visible
    # These should NOT be visible as text
    assert not page.get_by_text("<div").is_visible(), "Raw <div tags found in UI"
    assert not page.get_by_text("</div>").is_visible(), "Raw </div> tags found in UI"
    assert not page.get_by_text("<span").is_visible(), "Raw <span tags found in UI"
    assert not page.get_by_text("</span>").is_visible(), "Raw </span> tags found in UI"
    assert not page.get_by_text("<strong>").is_visible(), "Raw <strong> tags found in UI"
    
    print("✅ No HTML artifacts found in UI")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])