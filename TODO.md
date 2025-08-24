# TODO - Meshtastic Network Monitor

## Priority Order

### 1. ✅ Signal Strength Visualization (COMPLETED)
- Horizontal progress bars with gradient colors
- RSSI and SNR display
- Quality labels

### 2. ✅ Safe Message Testing (COMPLETED)
- Test mode on Channel 7
- Default "Only show nodes with packets" to ON

### 3. 🔄 Message & Node Persistence (IN PROGRESS)
- Add SQLite/PostgreSQL database
- Persist message history across restarts
- Store node information with timestamps
- Track last_seen, first_seen timestamps for aging
- Add pagination for historical messages
- Date/time range filtering
- Graceful data aging/cleanup options

### 4. ⏳ Node Details Modal
- Click node to see detailed information
- Message history from that specific node
- Signal strength over time graph
- Position history on map
- Connection quality metrics

### 5. ⏳ IRC-Style Node Commands
- Nodes can send commands to register
- `/login` - authenticate a node
- `/last <node>` - get last seen time
- `/info <node>` - get node information
- `/help` - list available commands
- Command prefix detection (e.g., "!")
- Response system back to nodes

### 6. ⏳ Network Graph Visualization
- Visual mesh topology showing connections
- Interactive graph with hop paths
- Signal strength on edges
- Real-time topology updates
- Force-directed layout
- Click nodes for details

### 7. ⏳ Dark/Light Theme Toggle
- User preference toggle
- Save preference in browser localStorage
- Additional theme options
- High contrast mode

### 8. ⏳ Export Functionality
- Export messages to CSV/JSON
- Export node list with metrics
- Download buttons in UI
- Configurable export formats
- Scheduled exports

### 9. ⏳ Message Search & Filtering
- Search messages by content/sender
- Advanced filters (date, node, channel)
- Regex pattern matching
- Save filter presets
- Quick filter buttons

### 10. ⏳ Alert System
- Keyword alerts in messages
- Low battery warnings
- Node disconnect notifications
- Browser notification support
- Alert history log

### 11. ⏳ Performance Metrics
- Network statistics over time
- Message throughput graphs
- Node availability tracking
- Packet loss statistics
- Network health score

## Technical Debt

### Testing
- Add more comprehensive Playwright tests
- Unit tests for message store
- Integration tests for database

### Documentation
- API documentation
- User guide
- Deployment guide

### Performance
- Optimize message rendering for large volumes
- Add message batching
- Implement virtual scrolling

### Security
- Add authentication for dashboard
- Encrypt sensitive data in database
- Rate limiting for commands

## Future Ideas

### Advanced Features
- Multi-device support (manage multiple radios)
- Message forwarding rules
- Automated responses
- Plugin system for extensions
- REST API for external integrations
- Mobile app companion

### Analytics
- Message frequency analysis
- Network coverage mapping
- Propagation predictions
- Traffic pattern analysis

### Integrations
- MQTT bridge
- Discord/Slack notifications
- Weather overlay on map
- APRS gateway
- Emergency alert system

## Notes

- Persistence is critical - users lose data on every restart
- Node details modal would greatly improve usability
- IRC-style commands enable remote management
- Network visualization helps understand mesh topology
- Theme toggle improves accessibility

## Implementation Order Rationale

1. **Persistence first** - Solves the biggest current limitation
2. **Node details** - Natural extension once we have historical data
3. **Commands** - Enables remote node management
4. **Visualization** - Provides network insights
5. **Theme** - Polish and user preference

---
*Last Updated: 2025-08-24*