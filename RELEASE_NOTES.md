# Release Notes

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