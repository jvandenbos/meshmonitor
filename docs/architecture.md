# Meshtastic Server Application Architecture

## Overview
A comprehensive server application for monitoring and interacting with Meshtastic mesh networks via USB-connected RAK 4631 nodes. The system provides real-time message logging, node tracking, network topology visualization, and a framework for network services.

## Core Requirements

1. **USB Connection Management**: Connect to RAK 4631 Meshtastic nodes via USB serial
2. **Message Monitoring**: Log all channel traffic with timestamps and metadata
3. **Node Tracking**: Discover and track nodes, including position, telemetry, and network metrics
4. **Network Visualization**: Build and maintain a graph of the mesh network topology
5. **Service Framework**: Support command-based services on dedicated channels

## Technology Stack

### Core Components
- **Language**: Python 3.11+
- **Framework**: FastAPI (async, high-performance, WebSocket support)
- **Database**: PostgreSQL (time-series data, spatial types, graph relationships)
- **Cache**: Redis (pub/sub, real-time updates, topology caching)
- **Serial**: pyserial-asyncio (async USB communication)

### Supporting Libraries
- **Meshtastic**: Official Python library for device communication
- **SQLAlchemy**: Async ORM with PostgreSQL support
- **Asyncpg**: High-performance PostgreSQL driver
- **Pydantic**: Data validation and serialization
- **WebSockets**: Real-time client communication

## System Architecture

### 1. Device Communication Layer
```
┌─────────────────────────────────────┐
│     USB Serial Connection Manager    │
├─────────────────────────────────────┤
│ • Auto-discovery of devices         │
│ • Connection health monitoring       │
│ • Automatic reconnection            │
│ • Message queue buffering           │
└─────────────────────────────────────┘
```

**Key Components**:
- `SerialInterface` wrapper for Meshtastic library
- Connection pool for multiple devices
- Event-driven message handling via pubsub
- Async task for continuous monitoring

### 2. Message Processing Pipeline
```
USB Device → Serial Reader → Message Queue → Parser → Database → API/WebSocket
```

**Message Types** (from Meshtastic protocol):
- `TEXT_MESSAGE_APP (1)`: Text messages between nodes
- `POSITION_APP (3)`: GPS location updates
- `NODEINFO_APP (4)`: Node metadata and capabilities
- `TELEMETRY_APP (67)`: Sensor data (battery, temperature, etc.)
- `ROUTING_APP (5)`: Mesh routing information
- `ADMIN_APP (6)`: Administrative commands

### 3. Data Storage Schema

#### Nodes Table
```sql
CREATE TABLE nodes (
    id VARCHAR PRIMARY KEY,           -- Node ID (e.g., !abcd1234)
    long_name VARCHAR,                 -- Human-readable name
    short_name VARCHAR(4),             -- 4-char short name
    hw_model VARCHAR,                  -- Hardware model
    role VARCHAR,                      -- Node role in mesh
    position GEOGRAPHY(POINT),         -- Spatial position data
    altitude FLOAT,                    -- Elevation in meters
    battery_level INTEGER,             -- Battery percentage
    last_heard TIMESTAMP,              -- Last activity time
    snr FLOAT,                        -- Signal-to-noise ratio
    hop_limit INTEGER,                 -- Max hop count
    metadata JSONB,                   -- Additional node data
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    from_node VARCHAR REFERENCES nodes(id),
    to_node VARCHAR REFERENCES nodes(id),
    channel INTEGER,                  -- Channel number
    port_num INTEGER,                 -- Message type/port
    payload TEXT,                     -- Message content
    encrypted BOOLEAN,
    hop_count INTEGER,                -- Hops taken
    rssi INTEGER,                     -- Signal strength
    snr FLOAT,                       -- Signal quality
    timestamp TIMESTAMP,              -- Message time
    raw_data JSONB                   -- Complete packet data
);
```

#### Network Topology Table
```sql
CREATE TABLE network_edges (
    from_node VARCHAR REFERENCES nodes(id),
    to_node VARCHAR REFERENCES nodes(id),
    distance FLOAT,                   -- Physical distance
    hop_count INTEGER,                -- Network hops
    rssi INTEGER,                     -- Link quality
    last_seen TIMESTAMP,
    PRIMARY KEY (from_node, to_node)
);
```

### 4. API Layer

#### REST Endpoints
- `GET /api/nodes` - List all discovered nodes
- `GET /api/nodes/{node_id}` - Get specific node details
- `GET /api/messages` - Query message history
- `POST /api/messages` - Send a message
- `GET /api/topology` - Get network graph data
- `GET /api/stats` - Network statistics

#### WebSocket Endpoints
- `/ws/messages` - Real-time message stream
- `/ws/nodes` - Node status updates
- `/ws/topology` - Network topology changes

### 5. Service Framework

#### Command Processing
Services listen on a dedicated channel (e.g., channel 7) for commands:

```python
@command_handler("!ping")
async def handle_ping(message):
    return f"pong from {node_id}"

@command_handler("!weather")
async def handle_weather(message):
    # Query weather API
    return weather_report

@command_handler("!relay")
async def handle_relay(message):
    # Forward message to another network
    return confirmation
```

#### Service Registry
- Dynamic service registration
- Command routing and validation
- Rate limiting and access control
- Response queueing and delivery

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [x] Initialize project structure
- [ ] Set up Python environment with dependencies
- [ ] Create database schemas
- [ ] Implement USB connection manager
- [ ] Basic message receiving and logging

### Phase 2: Data Processing (Week 2)
- [ ] Message parsing and storage
- [ ] Node discovery and tracking
- [ ] Position and telemetry handling
- [ ] Network edge detection
- [ ] Basic REST API

### Phase 3: Real-time Features (Week 3)
- [ ] WebSocket implementation
- [ ] Live message streaming
- [ ] Node status broadcasting
- [ ] Redis pub/sub integration
- [ ] Client notification system

### Phase 4: Network Analysis (Week 4)
- [ ] Topology graph building
- [ ] Path analysis algorithms
- [ ] Network metrics calculation
- [ ] Visualization data export
- [ ] Graph API endpoints

### Phase 5: Service Framework (Week 5)
- [ ] Command parser implementation
- [ ] Service registration system
- [ ] Built-in service handlers
- [ ] Response routing
- [ ] Access control

### Phase 6: Production Readiness (Week 6)
- [ ] Error handling and recovery
- [ ] Performance optimization
- [ ] Monitoring and logging
- [ ] Documentation
- [ ] Deployment configuration

## Deployment Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  RAK 4631    │────▶│   Server     │────▶│  PostgreSQL  │
│  USB Device  │     │   FastAPI    │     │   Database   │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐     ┌──────────────┐
                     │    Redis     │     │   Grafana    │
                     │  Cache/Queue │     │  Monitoring  │
                     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Web Clients │
                     │  (WebSocket) │
                     └──────────────┘
```

## Configuration

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/meshtastic
REDIS_URL=redis://localhost:6379

# Meshtastic
SERIAL_PORT=/dev/ttyUSB0  # Auto-detect if not set
DEVICE_BAUD=115200

# Server
API_PORT=8000
WS_PORT=8001
LOG_LEVEL=INFO

# Services
SERVICE_CHANNEL=7
COMMAND_PREFIX=!
```

## Security Considerations

1. **Message Encryption**: Respect Meshtastic's built-in encryption
2. **API Authentication**: JWT tokens for API access
3. **Rate Limiting**: Prevent service abuse
4. **Input Validation**: Sanitize all command inputs
5. **Access Control**: Role-based permissions for services

## Performance Targets

- Message processing: < 10ms latency
- Node discovery: < 1 second
- API response time: < 100ms
- WebSocket latency: < 50ms
- Database queries: < 50ms
- Network graph update: < 500ms

## Monitoring & Observability

- Prometheus metrics export
- Grafana dashboards for visualization
- Structured logging with correlation IDs
- Health check endpoints
- Performance profiling hooks

## Future Enhancements

1. **Multi-device Support**: Connect to multiple USB devices
2. **Geographic Mapping**: Real-time node position visualization
3. **Message Routing**: Intelligent message forwarding
4. **Plugin System**: Extensible service framework
5. **Mobile App**: Native mobile client
6. **Cloud Sync**: Optional cloud backup and sync
7. **AI Analysis**: Network pattern recognition
8. **Emergency Mode**: Priority message handling