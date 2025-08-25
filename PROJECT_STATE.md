# Meshtastic Dashboard Project State

## 🚀 Quick Start After Crash
```bash
cd /Volumes/External/code/meshtastic/server
streamlit run dashboard.py
# Access at: http://localhost:8501
```

## 📁 Key Files
- **Main Dashboard**: `/dashboard.py` - Streamlit UI application
- **Message Store**: `/app/device/message_store.py` - In-memory and DB storage
- **Database**: `/app/database/db.py` - SQLite persistence layer
- **Service**: `/app/device/service.py` - Message handling and routing
- **Connection**: `/app/device/connection.py` - Meshtastic device interface

## ✅ Completed Features (As of 2025-08-24)
1. **Signal Strength Bars** - Visual RSSI/SNR indicators with color coding
2. **Database Persistence** - SQLite storage for messages and nodes
3. **Node Details Modal** - Comprehensive node analytics view
4. **Network Graph** - Radial/radar topology visualization with zoom/pan
5. **Dark/Light Theme** - Toggle between themes with CSS styling
6. **Hop Tracking** - Comprehensive hop count analysis and logging
7. **View Details Button** - Fixed positioning inside node cards
8. **Network Graph Fixes** - TypeError fixes and null handling

## 🔧 Current Work: UI/UX Improvements
**Problem**: Message spam from telemetry/position updates, 84+ nodes cluttering the list

**Solution in Progress**: 
- Smart message filtering (Chat/Activity/System views)
- Time-based node filtering (Last 15 min/hour/24h)
- Message grouping and collapsing
- Session control buttons

See `UI_IMPROVEMENT_PLAN.md` for full details.

## 🐛 Known Issues
1. Nodes showing "-1 hops" = No routing info received yet (normal behavior)
2. GitHub security warnings about dependencies (non-critical)

## 📊 Database Schema
- **nodes** table: id, name, position, telemetry, hops, timestamps
- **messages** table: type, from, to, text, channel, timestamps
- **node_history** table: Time-series data for node metrics

## 🎨 UI Structure
```
┌─────────────────────────────────────┐
│         Header & Controls           │
├───────────┬─────────────────────────┤
│  Sidebar  │     Main Content        │
│           │  ┌──────┬──────┐        │
│  Filters  │  │ Msgs │Nodes │        │
│  Stats    │  └──────┴──────┘        │
│  Controls │                          │
└───────────┴─────────────────────────┘
```

## 🔄 Git Status
- **Repository**: github.com:jvandenbos/meshmonitor.git
- **Branch**: main
- **Last Commit**: "Add zoom/pan controls to network topology radar view"

## 📝 Next Steps (After UI Improvements)
1. IRC-style commands for node interaction
2. Message export functionality
3. Advanced analytics dashboard
4. Multi-device support
5. Web-based configuration

## 🛠️ Development Notes
- Using Streamlit for rapid UI development
- SQLite for local persistence (no external DB needed)
- Deque for efficient in-memory message storage
- NetworkX + Plotly for graph visualization
- Real-time updates via Meshtastic Python API

## 💡 Recovery Instructions
If crashed mid-implementation:
1. Check `git status` for uncommitted changes
2. Review `UI_IMPROVEMENT_PLAN.md` for current task
3. Check `dashboard.py` lines 1000-1200 for message display code
4. Check `message_store.py` for data storage methods
5. Continue from last completed step in plan

## 🔑 Key Design Decisions
- **Separation of Concerns**: UI filtering vs data capture
- **Progressive Disclosure**: Collapse repetitive updates
- **Persona-Driven Design**: Casual chat users vs technical monitors
- **Session vs Persistent**: Clear memory without losing DB data