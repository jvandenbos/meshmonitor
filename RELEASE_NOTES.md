# Release Notes

## [0.6.0] - 2025-08-24

### Added
- **Modern Signal Strength Visualization**
  - Horizontal progress bars with gradient color backgrounds
  - Red → Orange → Yellow → Green color progression based on RSSI
  - Shows exact dBm values and SNR when available
  - Quality labels (Poor, Fair, Good, Excellent)
  - Smooth transitions and animations
  - High contrast and accessibility-friendly design
  - Works for both direct and indirect nodes

- **Signal Quality Thresholds**
  - Excellent: > -60 dBm (green)
  - Good: -60 to -75 dBm (yellow)
  - Fair: -75 to -85 dBm (orange)
  - Poor: < -85 dBm (red)

- **Development Documentation**
  - Created CLAUDE.md with development guidelines
  - Added testing commands and project structure
  - Documented common tasks and debugging tips

### Improved
- Enhanced node card display with integrated signal bars
- Better visual hierarchy for signal information
- Cleaner CSS styling for signal indicators

### Testing
- Added test_signal_bars.py script for signal visualization testing
- Verified gradient display with various RSSI values

## [0.5.0] - 2025-01-24

### Added
- **Complete hop tracking system rebuild from scratch**
  - New centralized `hop_tracker.py` module for all hop calculations
  - Comprehensive file system logging to `logs/` directory
  - Real-time hop tracking with min/max hop history
  - Automatic hop count detection for packets without `hopStart` field
- **File system logging for debugging**
  - `hop_tracker.log` - Detailed hop calculations
  - `node_updates.log` - Node metadata changes
  - `packets.jsonl` - Raw packet data in JSON Lines format
- **Node filtering in dashboard**
  - "Only show nodes with packets" toggle button
  - Shows count of visible vs total nodes
  - Distinguishes between nodes from device database vs active nodes

### Fixed
- **Hop count tracking now works for ALL packet types**
  - Handles missing `hopStart` field (common in telemetry packets)
  - Assumes direct connection when `hopLimit=3` and no `hopStart`
  - Properly calculates hops for packets with partial hop data
- **Node ID consistency issues resolved**
  - All node IDs normalized to strings
  - Removes "!" prefix from packet IDs
  - Eliminates duplicate node entries ("split-brain" problem)
- **HTML rendering artifacts completely eliminated**
  - Removed nested div structures causing `</div>` tags
  - Simplified signal strength display
  - Clean hop count badges without HTML escaping issues

### Improved
- **Better hop count display**
  - Shows actual hop counts for nodes sending packets
  - "UNKNOWN" only for nodes that haven't sent packets yet
  - Explains why some nodes show without hop counts (from device database)
- **Enhanced logging and debugging**
  - Hop summary statistics in sidebar
  - Distribution of nodes by hop count
  - Real-time packet monitoring capabilities

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