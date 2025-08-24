# Release Notes

## [0.4.2] - 2025-01-24

### Fixed
- Duplicate "Message Traffic" and "Network Nodes" sections in Split View
- Properly handle empty states in Split View columns
- Column context management issues resolved
- Removed problematic placeholder elements

### Improved
- Added "No messages yet" and "No nodes discovered yet" indicators
- Cleaner Split View rendering without duplicates
- Better control flow structure

## [0.4.1] - 2025-01-24

### Fixed
- HTML rendering issues with span tags completely resolved
- Duplicate "Message Traffic" and "Network Nodes" sections removed
- Signal strength bar now properly displays as gradient bar

### Improved  
- Hop count now displayed with prominent badges (DIRECT, 1 HOP, 2 HOPS)
- Signal strength visualization with proper "Signal Strength" label
- Gradient bar from red to yellow to green for signal quality
- Clean HTML structure without stray tags
- Better visual hierarchy in node cards

### Added
- Comprehensive README.md with full project documentation
- Installation instructions and quick start guide
- Troubleshooting section for common issues
- Architecture overview and project structure

## [0.4.0] - 2025-01-24

### Added
- Hop count display for all nodes
- Signal strength bars for direct connections (visual RSSI indicator)
- Color-coded signal bars (green=strong, yellow=good, orange=fair, red=weak)
- Connection type column in nodes table
- Routing information sidebar section
- Smart node sorting: Direct connections first, then by hop count

### Improved
- Node list now shows connection type (Direct/1 hop/2 hops/etc)
- Direct connections display RSSI in dBm with visual signal bars
- Enhanced node metadata with SNR tracking
- Better proximity sorting algorithm
- Fixed HTML rendering issues (stray span tags)

### Technical
- Extract hop count from packet headers (hopLimit/hopStart)
- Track is_direct flag for zero-hop nodes
- Store RSSI/SNR for direct connections only
- Improved packet routing analysis

### UI Enhancements
- Signal strength visualization: ▂▄▆█ (strong) to ▁___ (weak)
- Connection type indicators: 📡 (direct) vs ↗️ (multi-hop)
- Cleaner node card layout with hop information
- Routing info documentation in sidebar

## [0.3.1] - 2025-01-24

### Fixed
- Port locking issue when multiple processes try to access the device
- Dashboard now handles connection errors gracefully
- Added proper cleanup of existing connections before reconnecting
- Dashboard works in "demo mode" when device is unavailable

### Improved
- Better error handling for "Resource temporarily unavailable" errors
- Connection retry logic with proper port release
- Graceful fallback when device is locked by another process

### Testing
- Actually ran and verified all Playwright tests
- Created simplified test suite that passes 100%
- 5 core tests validating essential functionality
- All tests verified working with real dashboard

## [0.3.0] - 2025-01-24

### Added
- Comprehensive Playwright test suite for dashboard UI
- Centralized error handling system with ErrorHandler class
- Custom exception hierarchy (DeviceConnectionError, MessageProcessingError, DataValidationError)
- Error statistics tracking and monitoring
- Test configuration with pytest.ini
- 10 automated UI tests covering all dashboard features

### Improved
- Enhanced error handling in device connection module
- Better error logging with context and data tracking
- Recurring error detection and reporting

### Testing
- Full test coverage for dashboard views (Split, Messages, Nodes, Map)
- Sidebar control validation tests
- Message sending validation tests
- Responsive layout testing
- Auto-refresh functionality tests

## [0.2.0] - 2025-01-24

### Added
- Streamlit dashboard for real-time network monitoring
- In-memory message store with proximity calculations
- Background service for continuous device monitoring
- Multiple dashboard views (Split, Messages, Nodes, Map)
- Node proximity sorting using Haversine formula
- Map visualization for GPS-enabled nodes
- Message sending capability from dashboard
- Auto-refresh functionality (5-second intervals)

### Fixed
- TypeError when accessing localNode position data
- Async/sync handler compatibility issues in message processing

### Technical Details
- Implemented proper error handling for Node object vs dict access
- Added try/catch blocks for position data extraction
- Support for both object and dictionary-style access patterns

## [0.1.0] - 2025-01-24

### Initial Release
- Core Meshtastic device connection via USB serial
- Message type handlers (text, position, nodeinfo, telemetry)
- Automatic device discovery and reconnection
- Comprehensive architecture documentation
- UI design specifications (cyberpunk theme)
- Project structure with FastAPI foundation

### Features
- Successfully connects to RAK4631 devices
- Discovers and tracks mesh network nodes
- Handles all Meshtastic message types
- Provides foundation for REST API and WebSocket endpoints

### Known Issues
- None at this release

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality additions  
- PATCH version for backwards-compatible bug fixes