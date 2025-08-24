# Meshtastic Server

A comprehensive server application for monitoring and interacting with Meshtastic mesh networks via USB-connected nodes.

## Features

- **USB Device Connection**: Auto-connect to RAK 4631 and other Meshtastic nodes
- **Message Monitoring**: Real-time logging of all mesh network traffic
- **Node Tracking**: Discover and track all nodes with position and telemetry data
- **Network Visualization**: Build and maintain mesh network topology graphs
- **Service Framework**: Extensible command-based services on dedicated channels
- **REST API**: Query historical data and send messages
- **WebSocket Support**: Real-time updates for connected clients

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- RAK 4631 or compatible Meshtastic device

### Installation

```bash
# Clone the repository
git clone [repository-url]
cd meshtastic-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb meshtastic
python -m app.database.init

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Running the Server

```bash
# Start the server
python -m app.main

# Or with uvicorn for development
uvicorn app.main:app --reload --port 8000
```

### Basic Usage

1. **Connect Device**: Plug in your Meshtastic device via USB
2. **Access API**: Navigate to http://localhost:8000/docs for API documentation
3. **Monitor Messages**: Connect to WebSocket at ws://localhost:8000/ws/messages
4. **Send Commands**: Use channel 7 (configurable) for service commands like `!ping`

## Documentation

- [Architecture Overview](docs/architecture.md) - System design and implementation details

## Project Structure

```
meshtastic-server/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── config.py             # Configuration management
│   ├── api/                 # REST API endpoints
│   ├── websocket/           # WebSocket handlers
│   ├── device/              # Meshtastic device communication
│   ├── database/            # Database models and queries
│   ├── services/            # Command-based services
│   └── utils/               # Utility functions
├── docs/                    # Documentation
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## API Examples

### Get All Nodes
```bash
curl http://localhost:8000/api/nodes
```

### Send a Message
```bash
curl -X POST http://localhost:8000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello mesh!", "channel": 0}'
```

### WebSocket Connection (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/messages');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('New message:', message);
};
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
# Format code
black app/

# Lint
pylint app/
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

[MIT License](LICENSE)

## Support

For issues and questions, please use the GitHub issue tracker.