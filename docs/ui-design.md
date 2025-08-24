# Meshtastic Server UI Design Document

## Overview
A modern, cyberpunk-themed dashboard UI for the Meshtastic server with real-time network visualization, message monitoring, and command console capabilities. The interface follows a "mission control meets cyberpunk" aesthetic designed for ham radio operators and mesh network enthusiasts.

## Technology Stack

### Core Framework
- **SvelteKit**: High performance, less boilerplate, compiles away for faster loads
- **TypeScript**: Type safety for complex real-time data structures
- **Vite**: Fast build tooling and hot module replacement

### UI Libraries
- **shadcn/ui**: Unstyled, accessible component primitives
- **Tailwind CSS**: Utility-first styling with custom cyberpunk theme
- **Lucide Icons**: Consistent icon set for UI elements

### Visualization
- **D3.js**: Force-directed network graph visualization
- **MapLibre GL JS**: Open-source, high-performance mapping
- **Chart.js**: Telemetry data visualization

### Real-time Communication
- **Native WebSocket API**: Direct connection to FastAPI WebSocket endpoints
- **Svelte Stores**: Reactive state management for real-time updates

## Visual Design Guidelines

### Color Palette
```css
:root {
  /* Backgrounds */
  --bg-primary: #0A0A0A;      /* Near-black */
  --bg-secondary: #0D1117;    /* Dark navy */
  --bg-panel: #161B22;        /* Panel background */
  
  /* Primary Accents */
  --accent-cyan: #00FFFF;     /* Electric cyan - interactive elements */
  --accent-magenta: #FF00FF;  /* Neon magenta - alerts/critical */
  --accent-lime: #39FF14;     /* Lime green - positive status */
  --accent-orange: #FF6600;   /* Orange - warnings */
  
  /* Text */
  --text-primary: #EAEAEA;    /* Off-white body text */
  --text-secondary: #8B949E;  /* Muted text */
  --text-accent: var(--accent-cyan);
  
  /* Borders & Effects */
  --border-color: rgba(0, 255, 255, 0.2);
  --glow-color: rgba(0, 255, 255, 0.5);
}
```

### Typography
- **UI Font**: Inter (sans-serif) - Clean, readable for interface elements
- **Data Font**: Fira Code (monospace) - Terminal feel for logs and data
- **Font Sizes**: 
  - Headers: 24px/20px/16px (h1/h2/h3)
  - Body: 14px
  - Small: 12px
  - Code: 13px

### Visual Effects
- **Glow Effects**: `box-shadow: 0 0 20px var(--glow-color)`
- **Scan Lines**: Subtle animated CSS background overlay
- **Grid Pattern**: Faint background grid for depth
- **Transitions**: 200ms ease for smooth interactions

## Component Architecture

### 1. App Shell (`AppLayout.svelte`)
```
┌──────────────────────────────────────────────────┐
│                    Header Bar                     │
├────────┬─────────────────────────────────────────┤
│        │                                          │
│  Side  │            Main Content Area            │
│  Bar   │                                          │
│        │                                          │
└────────┴─────────────────────────────────────────┘
```

**Features**:
- Collapsible sidebar (width: 250px expanded, 60px collapsed)
- Global stats in header (nodes online, messages/min, connection status)
- Theme switcher (dark/light/auto)
- User preferences persistence

### 2. Dashboard View (`DashboardView.svelte`)
Grid layout with customizable panels:
```
┌─────────────────────────┬──────────────┐
│                         │              │
│    Network Graph        │ Node Stats   │
│      (60% width)        │  (40% width) │
│                         │              │
├─────────────────────────┼──────────────┤
│                         │              │
│    Message Feed         │     Map      │
│      (60% width)        │  (40% width) │
│                         │              │
└─────────────────────────┴──────────────┘
```

### 3. Network Graph Component (`NetworkGraph.svelte`)

**Implementation with D3.js**:
```javascript
// Force-directed layout configuration
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(edges).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide().radius(30));
```

**Visual Elements**:
- **Nodes**: 
  - Circle size based on node importance (gateway nodes larger)
  - Color indicates battery level (gradient from green to red)
  - Pulsing animation for active communication
  - Border glow for selected/hovered nodes
  
- **Edges**:
  - Line thickness represents signal strength (RSSI)
  - Opacity shows link quality (SNR)
  - Animated particles along edges for message routing
  - Directional arrows for asymmetric links

**Interactivity**:
- Drag nodes to reposition (with physics)
- Click to select and view details
- Double-click to center on node
- Scroll to zoom, drag background to pan
- Right-click context menu for node actions

### 4. Message Monitor (`MessageMonitor.svelte`)

**Layout**:
```
┌─────────────────────────────────────────┐
│ Filters: [Channel ▼] [Type ▼] [Node ▼] │
├─────────────────────────────────────────┤
│ TIME     FROM    TO      TYPE   MESSAGE │
│ 12:34:56 Node1   ALL     TEXT   Hello.. │
│ 12:34:55 Node2   Node3   POS    [GPS]   │
│ 12:34:54 Node3   ALL     TELEM  [Data]  │
│ ...                                      │
└─────────────────────────────────────────┘
```

**Features**:
- Virtual scrolling for 10,000+ messages
- Real-time updates via WebSocket
- Color-coded message types
- Quick filters and search
- Export to CSV/JSON

### 5. Map View (`MapView.svelte`)

**MapLibre GL JS Configuration**:
```javascript
const map = new maplibregl.Map({
  container: 'map',
  style: 'https://tiles.stadiamaps.com/styles/alidade_smooth_dark.json',
  center: [longitude, latitude],
  zoom: 10
});
```

**Node Markers**:
- Custom markers with node icons
- Clustering for dense areas
- Popup on click with node details
- Path lines showing message routes
- Heat map overlay for coverage areas

### 6. Command Console (`CommandConsole.svelte`)

**Terminal-style Interface**:
```
┌─────────────────────────────────────────┐
│ > !ping                                  │
│ Response: pong from !abcd1234 (0.5s)    │
│ > !weather                               │
│ Response: Clear, 72°F, Wind 5mph NW     │
│ > _                                      │
└─────────────────────────────────────────┘
```

**Features**:
- Command history (up/down arrows)
- Auto-complete with Tab
- Syntax highlighting
- Multi-line input support
- Command aliases and macros

### 7. Node Detail Panel (`NodeDetailPanel.svelte`)

**Slide-in Panel Content**:
- **Identity**: Node ID, name, hardware model
- **Status**: Online/offline, last seen, uptime
- **Telemetry**: Live charts for battery, temperature, voltage
- **Position**: GPS coordinates, altitude, speed
- **Network**: SNR, RSSI, hop count, neighbors
- **Messages**: Recent messages from/to this node
- **Actions**: Send message, request telemetry, admin commands

## Real-time Data Flow

### WebSocket Connection Manager
```javascript
class WebSocketManager {
  constructor() {
    this.connections = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectDelay = 30000;
  }

  connect(endpoint, handlers) {
    const ws = new WebSocket(`ws://localhost:8000${endpoint}`);
    
    ws.onopen = () => {
      this.reconnectAttempts = 0;
      handlers.onOpen?.();
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handlers.onMessage?.(data);
      this.updateStore(endpoint, data);
    };
    
    ws.onclose = () => {
      this.scheduleReconnect(endpoint, handlers);
    };
    
    this.connections.set(endpoint, ws);
  }
  
  scheduleReconnect(endpoint, handlers) {
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), this.maxReconnectDelay);
    setTimeout(() => this.connect(endpoint, handlers), delay);
    this.reconnectAttempts++;
  }
}
```

### Store Architecture
```javascript
// nodes.store.js
export const nodes = writable(new Map());
export const selectedNode = writable(null);

// messages.store.js  
export const messages = writable([]);
export const messageBuffer = writable([]);

// topology.store.js
export const edges = writable([]);
export const networkStats = derived([nodes, edges], calculateStats);
```

## Performance Optimizations

### 1. Virtual Scrolling
Implement for message lists and node tables:
```javascript
class VirtualScroller {
  constructor(items, itemHeight, containerHeight) {
    this.visibleStart = 0;
    this.visibleEnd = Math.ceil(containerHeight / itemHeight);
  }
  
  getVisibleItems() {
    return this.items.slice(this.visibleStart, this.visibleEnd);
  }
}
```

### 2. DOM Batching
Batch multiple updates in a single frame:
```javascript
let pendingUpdates = [];
let rafId = null;

function scheduleUpdate(update) {
  pendingUpdates.push(update);
  
  if (!rafId) {
    rafId = requestAnimationFrame(() => {
      const fragment = document.createDocumentFragment();
      pendingUpdates.forEach(update => update(fragment));
      container.appendChild(fragment);
      pendingUpdates = [];
      rafId = null;
    });
  }
}
```

### 3. Message Buffering
Buffer incoming messages to prevent UI flooding:
```javascript
const messageBuffer = [];
let flushTimer;

function bufferMessage(message) {
  messageBuffer.push(message);
  
  clearTimeout(flushTimer);
  flushTimer = setTimeout(() => {
    messages.update(m => [...messageBuffer, ...m].slice(0, 10000));
    messageBuffer.length = 0;
  }, 100);
}
```

### 4. Graph Rendering Optimization
- Use Canvas for > 100 nodes (better performance than SVG)
- Implement level-of-detail (LOD) rendering
- Pause physics simulation when idle
- Use WebGL for > 1000 nodes

## Responsive Design

### Breakpoints
```css
/* Mobile: < 640px */
@media (max-width: 639px) {
  /* Stack panels vertically */
  /* Hide sidebar, use hamburger menu */
  /* Simplify network graph */
}

/* Tablet: 640px - 1024px */
@media (min-width: 640px) and (max-width: 1023px) {
  /* 2-column layout */
  /* Collapsible panels */
}

/* Desktop: >= 1024px */
@media (min-width: 1024px) {
  /* Full grid layout */
  /* All features visible */
}
```

## Accessibility

- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Screen Readers**: ARIA labels and live regions for updates
- **Color Contrast**: WCAG AA compliance for all text
- **Focus Indicators**: Clear focus states for keyboard users
- **Reduced Motion**: Respect prefers-reduced-motion setting

## Development Workflow

### File Structure
```
ui/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   ├── network/
│   │   │   ├── messages/
│   │   │   ├── map/
│   │   │   └── console/
│   │   ├── stores/
│   │   ├── utils/
│   │   └── websocket/
│   ├── routes/
│   └── app.html
├── static/
├── package.json
└── svelte.config.js
```

### Build Configuration
```javascript
// vite.config.js
export default {
  optimizeDeps: {
    include: ['d3', 'maplibre-gl']
  },
  build: {
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          'd3': ['d3'],
          'maplibre': ['maplibre-gl']
        }
      }
    }
  }
};
```

## Testing Strategy

- **Unit Tests**: Vitest for component logic
- **Integration Tests**: Playwright for user flows
- **Performance Tests**: Lighthouse CI for metrics
- **Visual Tests**: Percy for UI regression

## Deployment

### Docker Configuration
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["node", "build"]
```

## Future Enhancements

1. **AR View**: Augmented reality node visualization
2. **Voice Commands**: Speech-to-text for console
3. **AI Assistant**: Natural language command interpretation
4. **3D Network View**: Three.js powered 3D visualization
5. **Mobile App**: React Native companion app
6. **Plugin System**: Extensible UI components
7. **Collaborative Features**: Multi-user dashboard sharing
8. **Advanced Analytics**: ML-powered network insights