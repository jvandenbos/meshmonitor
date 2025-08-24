# Claude Development Guidelines

## Project Overview
Meshtastic network monitoring dashboard with real-time node tracking and signal visualization.

## Development Standards

### Code Style
- Use modern Python 3.12+ features
- Follow PEP 8 conventions
- Type hints for function signatures
- Descriptive variable names
- Keep functions focused and small

### Testing Commands
```bash
# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_dashboard.py -v

# Check code formatting (if available)
# python -m black --check .
# python -m isort --check .
```

### Running the Dashboard
```bash
# Start the dashboard
streamlit run dashboard.py

# Run in headless mode for testing
streamlit run dashboard.py --server.headless true --server.port 8501
```

### Project Structure
```
/Volumes/External/code/meshtastic/server/
├── app/                    # Core application modules
│   ├── device/            # Device connection and management
│   │   ├── connection.py  # Serial device connection
│   │   ├── hop_tracker.py # Hop count tracking
│   │   ├── message_store.py # Message storage
│   │   └── service.py     # Main service controller
│   └── utils/             # Utility functions
├── dashboard.py           # Main Streamlit dashboard
├── logs/                  # Runtime logs
│   ├── hop_tracker.log   # Hop tracking logs
│   ├── node_updates.log  # Node update logs
│   └── packets.jsonl     # Raw packet logs
└── tests/                 # Test suite
```

## Recent Updates

### Signal Strength Visualization (2025-08-24)
- Added horizontal progress bars with gradient colors
- Color-coded signal quality (Poor/Fair/Good/Excellent)
- Shows RSSI in dBm and SNR values
- Smooth animations and transitions
- Accessibility-friendly high contrast design

### Hop Tracking System (2025-08-24)
- Comprehensive hop count calculation
- Direct vs indirect node detection
- Real-time packet logging
- Hop distribution statistics

## Key Features
- Real-time node discovery and tracking
- Message traffic monitoring
- Signal strength visualization
- Battery level tracking
- Position/GPS support
- Split view, messages-only, nodes-only, and map views
- Auto-refresh capabilities
- Dark theme optimized UI

## Development Notes
- Dashboard uses Streamlit for reactive UI
- WebSocket connections for real-time updates
- Async/await patterns for device communication
- Message store acts as central data repository
- Hop tracker maintains network topology

## Git Workflow
```bash
# Always check status before committing
git status

# Add and commit changes
git add -A
git commit -m "Descriptive commit message"

# Push to remote
git push origin main
```

## Performance Considerations
- Dashboard auto-refreshes every 5 seconds
- Message store limits to 1000 recent messages
- Hop tracker runs background summary every 5 seconds
- Efficient node update batching

## Debugging
- Check `logs/hop_tracker.log` for hop calculations
- Check `logs/node_updates.log` for node changes
- Check `logs/packets.jsonl` for raw packet data
- Use browser developer tools for UI issues

## Common Tasks

### Add New Node Fields
1. Update `message_store.py` to store new fields
2. Update dashboard.py node display section
3. Test with `test_signal_bars.py` script

### Modify Signal Thresholds
Edit thresholds in `dashboard.py`:
- Excellent: > -60 dBm
- Good: -60 to -75 dBm  
- Fair: -75 to -85 dBm
- Poor: < -85 dBm

### Test With Sample Data
```bash
python test_signal_bars.py  # Adds test nodes with various signal strengths
```

## Dependencies
- streamlit
- pandas
- folium
- streamlit-folium
- meshtastic
- asyncio
- pyserial