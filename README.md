# 📡 Meshtastic Network Monitor

A real-time monitoring dashboard for Meshtastic mesh networks with advanced node tracking, message logging, and network visualization capabilities.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Meshtastic](https://img.shields.io/badge/meshtastic-2.2%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🌟 Features

### Real-Time Monitoring
- **Live Message Feed**: Track all mesh network traffic including text messages, position updates, telemetry data
- **Node Discovery**: Automatically discovers and tracks all nodes in the mesh network
- **Signal Strength Visualization**: Color-coded signal bars for direct connections
- **Hop Count Display**: See how many hops each packet takes through the network
- **Smart Sorting**: Nodes sorted by connection type (direct first, then by hop count)

### Visual Dashboard
- **Split View**: Monitor messages and nodes side-by-side
- **Messages View**: Full message history with type-based filtering
- **Nodes View**: Detailed table with connection info, battery levels, positions
- **Map View**: Geographic visualization of GPS-enabled nodes
- **Dark Theme**: Cyberpunk-inspired UI with neon accents

### Network Analysis
- **Proximity Sorting**: Nodes sorted by physical distance (GPS-based)
- **Connection Quality**: RSSI and SNR tracking for direct connections
- **Battery Monitoring**: Track battery levels across the network
- **Position Tracking**: GPS coordinates with altitude data
- **Routing Information**: Hop counts and connection paths

## 📸 Screenshots

### Dashboard Views
- **Split View**: Messages and nodes displayed simultaneously
- **Signal Strength**: Visual bars showing connection quality (Red → Yellow → Green)
- **Hop Count**: Prominent badges showing "DIRECT", "1 HOP", "2 HOPS", etc.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- RAK4631 or compatible Meshtastic device
- USB connection to the device

### Installation

1. **Clone the repository**
```bash
git clone [repository-url]
cd meshtastic-server
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Connect your Meshtastic device**
- Plug in your RAK4631 or compatible device via USB
- The dashboard will auto-detect the device

### Running the Dashboard

```bash
# Start the monitoring dashboard
streamlit run dashboard.py
```

The dashboard will be available at: **http://localhost:8501**

### Alternative: Test Connection First

```bash
# Test device connection
python test_connection.py
```

## 🎮 Usage

### Dashboard Controls

#### Sidebar
- **View Mode**: Switch between Split, Messages, Nodes, and Map views
- **Auto Refresh**: Toggle 5-second auto-refresh
- **Message Filter**: Filter by message type (text, position, telemetry, etc.)
- **Send Message**: Send text messages to the mesh network
- **Statistics**: View message counts and network stats

#### Node Display
- **📡 DIRECT**: Direct connection with signal strength bar
- **↗️ X HOPS**: Multi-hop connection with hop count
- **Signal Bar**: Visual indicator from red (weak) to green (strong)
- **Battery**: 🔋 (>75%) to 🪫 (<25%)
- **Position**: 📍 indicates GPS-enabled node

### Sending Messages

1. Enter message text in the sidebar
2. Select channel (0-7)
3. Click "Send" button
4. Message will be broadcast to all nodes

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python with FastAPI foundation
- **Device Communication**: Meshtastic Python library
- **UI**: Streamlit with custom CSS theming
- **Database**: In-memory store (PostgreSQL ready)
- **Testing**: Playwright for UI testing

### Project Structure
```
meshtastic-server/
├── app/
│   ├── device/           # Meshtastic device communication
│   │   ├── connection.py # USB serial interface
│   │   ├── service.py    # Background monitoring service
│   │   └── message_store.py # Message and node storage
│   ├── utils/            # Utility functions
│   │   └── error_handler.py # Centralized error handling
│   └── config.py         # Configuration management
├── tests/                # Playwright UI tests
├── docs/                 # Documentation
│   ├── architecture.md   # System design
│   └── ui-design.md      # UI specifications
├── dashboard.py          # Streamlit dashboard
├── test_connection.py    # Connection test script
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Device Configuration
SERIAL_PORT=              # Leave empty for auto-detect
DEVICE_BAUD=115200       # Serial baud rate

# Server Configuration  
API_PORT=8000            # API server port
LOG_LEVEL=INFO           # Logging level

# Service Configuration
SERVICE_CHANNEL=7        # Channel for service commands
COMMAND_PREFIX=!         # Command prefix
```

## 📊 Data Tracking

### Message Types
- **Text Messages**: Human-readable messages between nodes
- **Position Updates**: GPS coordinates and altitude
- **Telemetry Data**: Battery, temperature, humidity, pressure
- **Node Info**: Device metadata and capabilities
- **Routing Info**: Hop counts and signal strength

### Node Metrics
- **Connection Type**: Direct or multi-hop with hop count
- **Signal Strength**: RSSI in dBm for direct connections
- **Signal-to-Noise Ratio**: SNR for link quality
- **Battery Level**: Percentage remaining
- **Position**: Latitude, longitude, altitude
- **Distance**: Calculated distance from your node

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/

# Run with browser visible
pytest tests/ --headed

# Run specific test
pytest tests/test_dashboard_simple.py
```

### Test Coverage
- Dashboard loading and navigation
- View mode switching
- Message filtering
- Node sorting
- Signal strength visualization
- Auto-refresh functionality

## 🛠️ Development

### Adding New Features

1. **Message Handlers**: Add to `app/device/connection.py`
2. **UI Components**: Modify `dashboard.py`
3. **Data Storage**: Update `app/device/message_store.py`
4. **Services**: Extend `app/device/service.py`

### Future Enhancements
- [ ] PostgreSQL persistence
- [ ] REST API endpoints
- [ ] WebSocket real-time updates
- [ ] Command-based services framework
- [ ] Network graph visualization
- [ ] Message encryption status
- [ ] Advanced filtering and search
- [ ] Export functionality (CSV/JSON)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill existing Streamlit processes
pkill -f "streamlit run dashboard.py"
```

### Device Not Found
- Check USB connection
- Verify permissions: `sudo usermod -a -G dialout $USER`
- Try specifying port in .env: `SERIAL_PORT=/dev/ttyUSB0`

### Connection Errors
- Dashboard continues in "demo mode" if device is unavailable
- Check that no other application is using the serial port
- Try unplugging and reconnecting the device

## 📝 Release Notes

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for version history and changes.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Update documentation
5. Submit a pull request

## 📜 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Meshtastic project for the excellent mesh networking protocol
- Streamlit for the rapid dashboard development framework
- The ham radio and mesh networking community

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review test files for usage examples

---

**Built with ❤️ for the Meshtastic community**