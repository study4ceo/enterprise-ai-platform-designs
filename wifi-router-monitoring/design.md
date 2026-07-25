# Technical Design Document: WiFi Router Connection Monitor

## Overview

The WiFi Router Connection Monitor is a standalone Python application designed to provide real-time visibility into device connections on WiFi networks. The system continuously monitors routers using multiple protocols (SNMP, SSH, HTTP API, ARP), detects new device connections, maintains historical records, and displays information through a responsive web dashboard with real-time updates via WebSockets.

### Core Capabilities

- **Multi-Protocol Router Communication**: Support for SNMP, SSH, router HTTP/HTTPS APIs, and ARP table scanning
- **Automatic Device Discovery**: Detect and identify devices with MAC address, IP, hostname, and vendor lookup via OUI database
- **Real-Time Monitoring**: Continuous scanning with configurable intervals (5-300 seconds, default 30s)
- **Live Dashboard**: WebSocket-powered real-time updates displaying active connections and device information
- **Historical Tracking**: Time-series database for connection events with 90-day default retention
- **Device Management**: User-assigned friendly names, notes, trust levels, and device profiling
- **Multi-Channel Notifications**: Browser push, email, and webhook notifications for new device connections
- **Device Filtering**: Allowlist/blocklist support with high-priority alerts for blocklisted devices
- **Analytics & Reporting**: Connection patterns, frequency analysis, duration tracking, and bandwidth monitoring
- **Security**: Username/password authentication with bcrypt hashing, HTTPS support, session management
- **Multi-Router Support**: Monitor multiple routers simultaneously from a single dashboard
- **Export Capabilities**: CSV and JSON export of connection history with filtering

### Technology Stack

**Backend:**
- **Language**: Python 3.11+
- **Web Framework**: FastAPI (async, high-performance, WebSocket support)
- **Router Communication Libraries**:
  - SNMP: `pysnmp` (pure Python, v1/v2c/v3 support)
  - SSH: `netmiko` (built on Paramiko, network device focused)
  - HTTP/HTTPS: `httpx` (async HTTP client)
- **MAC Vendor Lookup**: `mac-vendor-lookup` (local OUI database from IEEE)
- **Database**: SQLite with optimizations for time-series data (indexes on timestamps, MAC addresses)
- **Authentication**: `passlib` with bcrypt for password hashing
- **Task Scheduling**: `APScheduler` for periodic router scanning
- **Notifications**: 
  - Email: `aiosmtplib` (async SMTP)
  - Webhooks: `httpx` (async HTTP POST)
- **Configuration**: YAML config files via `PyYAML`

**Frontend:**
- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI (MUI) for responsive components
- **State Management**: React Context API + React Query for server state
- **Real-Time Communication**: Native WebSocket API
- **Charts**: Recharts for connection analytics visualization
- **Build Tool**: Vite for fast development and optimized production builds

**Development & Deployment:**
- **Package Management**: Poetry for Python dependency management
- **Code Quality**: Black (formatting), Ruff (linting), mypy (type checking)
- **Testing**: pytest, pytest-asyncio for async tests
- **Containerization**: Docker with multi-stage builds
- **Process Management**: systemd service or Docker Compose

---

## Architecture

### High-Level Architecture

The application follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Dashboard (React)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ Active   │  │ History  │  │ Device   │  │ Analytics  │ │
│  │ Devices  │  │ View     │  │ Mgmt     │  │ Dashboard  │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
           │                        ▲
           │ HTTP/REST              │ WebSocket
           ▼                        │
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Application Server                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ REST API     │  │ WebSocket    │  │ Authentication   │ │
│  │ Endpoints    │  │ Manager      │  │ Middleware       │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Router       │  │ Device       │  │ Connection       │ │
│  │ Scanner      │  │ Manager      │  │ Event Handler    │ │
│  │ Service      │  │ Service      │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Notification │  │ Analytics    │  │ Export           │ │
│  │ Service      │  │ Service      │  │ Service          │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Access Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Device       │  │ Connection   │  │ Configuration    │ │
│  │ Repository   │  │ Repository   │  │ Repository       │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Persistence Layer                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SQLite Database                          │  │
│  │  - devices table (device profiles)                    │  │
│  │  - connection_events table (time-series history)      │  │
│  │  - routers table (router configurations)              │  │
│  │  - users table (authentication)                       │  │
│  │  - filter_rules table (allowlists/blocklists)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                        │
           ▼                        ▼
┌──────────────────┐      ┌────────────────────────┐
│  Router          │      │  External Services     │
│  (SNMP/SSH/API)  │      │  - Email SMTP          │
│                  │      │  - Webhook Endpoints   │
└──────────────────┘      └────────────────────────┘
```

### Component Responsibilities

**1. Router Scanner Service**
- Manages periodic scanning of all configured routers
- Implements router-specific protocol adapters (SNMP, SSH, HTTP API, ARP)
- Handles connection pooling and retry logic
- Detects new connections and disconnections by comparing scan results
- Publishes connection events to the event handler

**2. Device Manager Service**
- Maintains device profiles in the database
- Performs MAC vendor lookup via OUI database
- Updates device metadata (friendly names, notes, trust levels)
- Tracks first seen and last seen timestamps

**3. Connection Event Handler**
- Processes connection and disconnection events
- Writes connection records to time-series database
- Triggers notifications based on filter rules
- Broadcasts real-time updates to WebSocket clients

**4. Notification Service**
- Evaluates filter rules (allowlists, blocklists, trusted devices)
- Sends browser push notifications
- Sends email alerts via SMTP
- Posts webhook notifications to external systems

**5. Analytics Service**
- Aggregates connection data for dashboard charts
- Calculates connection frequencies, durations, and patterns
- Provides peak time analysis and device statistics

**6. WebSocket Manager**
- Maintains active WebSocket connections from dashboard clients
- Broadcasts device connection updates in real-time
- Handles client connection lifecycle and heartbeats

**7. Authentication Middleware**
- Validates session tokens for protected endpoints
- Enforces HTTPS when enabled
- Logs authentication attempts

---

## Components and Interfaces

### Core Components

#### 1. Router Protocol Adapters

**SNMP Adapter**
```python
class SNMPAdapter:
    def __init__(self, host: str, port: int, community: str, version: str):
        """Initialize SNMP connection parameters"""
        
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """Query router via SNMP for device table"""
        # OIDs: ipNetToMediaPhysAddress, ipNetToMediaNetAddress
        
    async def test_connection(self) -> ConnectionTestResult:
        """Validate SNMP connectivity and credentials"""
```

**SSH Adapter**
```python
class SSHAdapter:
    def __init__(self, host: str, port: int, username: str, password: str, 
                 device_type: str):
        """Initialize SSH connection via netmiko"""
        
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """Execute router commands to extract device table"""
        # Commands vary by router manufacturer (Cisco, Ubiquiti, etc.)
        
    async def test_connection(self) -> ConnectionTestResult:
        """Validate SSH connectivity"""
```

**HTTP API Adapter**
```python
class HTTPAPIAdapter:
    def __init__(self, base_url: str, auth_token: str):
        """Initialize HTTP API client"""
        
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """Query router API for connected devices"""
        
    async def test_connection(self) -> ConnectionTestResult:
        """Validate API connectivity and authentication"""
```

**ARP Scanner**
```python
class ARPScanner:
    def __init__(self, network_cidr: str):
        """Initialize ARP scanner for local network"""
        
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """Scan local network ARP table"""
```


#### 2. Router Scanner Service

```python
class RouterScannerService:
    def __init__(self, router_repository: RouterRepository, 
                 device_manager: DeviceManagerService,
                 event_handler: ConnectionEventHandler):
        """Initialize scanner with dependencies"""
        
    async def start_scanning(self):
        """Start periodic scanning for all configured routers"""
        
    async def stop_scanning(self):
        """Stop all scanning tasks"""
        
    async def scan_router(self, router_id: str) -> ScanResult:
        """Perform single scan of specified router"""
        # 1. Get router configuration
        # 2. Select appropriate protocol adapter
        # 3. Query router for connected devices
        # 4. Compare with previous scan results
        # 5. Generate connection/disconnection events
        
    async def handle_scan_error(self, router_id: str, error: Exception):
        """Handle scan failures with retry logic"""
```

#### 3. Device Manager Service

```python
class DeviceManagerService:
    def __init__(self, device_repository: DeviceRepository, 
                 mac_lookup: MACVendorLookup):
        """Initialize device manager"""
        
    async def get_or_create_device(self, mac: str, ip: str, 
                                   hostname: str) -> Device:
        """Get existing device or create new device profile"""
        
    async def update_device_metadata(self, mac: str, 
                                    friendly_name: str = None,
                                    notes: str = None,
                                    trusted: bool = None) -> Device:
        """Update user-assigned device metadata"""
        
    async def search_devices(self, query: str) -> List[Device]:
        """Search devices by MAC, IP, hostname, or friendly name"""
        
    def is_new_device(self, mac: str) -> bool:
        """Check if device has been seen before"""
```

#### 4. Connection Event Handler

```python
class ConnectionEventHandler:
    def __init__(self, connection_repository: ConnectionRepository,
                 notification_service: NotificationService,
                 websocket_manager: WebSocketManager):
        """Initialize event handler"""
        
    async def handle_connection_event(self, event: ConnectionEvent):
        """Process connection or disconnection event"""
        # 1. Write to connection history
        # 2. Check notification filters
        # 3. Trigger notifications if applicable
        # 4. Broadcast to WebSocket clients
        
    async def handle_disconnection_event(self, event: DisconnectionEvent):
        """Process device disconnection"""
```


#### 5. Notification Service

```python
class NotificationService:
    def __init__(self, filter_repository: FilterRuleRepository,
                 email_client: EmailClient,
                 webhook_client: WebhookClient,
                 config: NotificationConfig):
        """Initialize notification service"""
        
    async def should_notify(self, device: Device, 
                           is_new: bool) -> NotificationDecision:
        """Evaluate filter rules to determine if notification needed"""
        # Check allowlist, blocklist, trusted status
        
    async def send_notifications(self, device: Device, 
                                event_type: str, priority: str):
        """Send notifications via enabled channels"""
        # Browser push, email, webhook
        
    async def send_browser_notification(self, device: Device):
        """Send browser push notification"""
        
    async def send_email_notification(self, device: Device):
        """Send email alert via SMTP"""
        
    async def send_webhook_notification(self, device: Device, 
                                       webhook_url: str):
        """POST notification to webhook endpoint"""
```

#### 6. WebSocket Manager

```python
class WebSocketManager:
    def __init__(self):
        """Initialize WebSocket connection manager"""
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept new WebSocket connection"""
        
    async def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        
    async def broadcast_connection_event(self, event: ConnectionEvent):
        """Send event to all connected clients"""
        
    async def broadcast_device_update(self, device: Device):
        """Send device update to all connected clients"""
        
    async def send_personal_message(self, message: dict, session_id: str):
        """Send message to specific client"""
```

### REST API Endpoints

**Authentication Endpoints**
```
POST   /api/auth/login          - Authenticate user
POST   /api/auth/logout         - Terminate session
GET    /api/auth/session        - Validate current session
```

**Device Endpoints**
```
GET    /api/devices             - List all device profiles
GET    /api/devices/{mac}       - Get device by MAC address
PUT    /api/devices/{mac}       - Update device metadata
GET    /api/devices/search      - Search devices (query param)
```


**Connection History Endpoints**
```
GET    /api/connections         - Query connection history
                                  Query params: start_date, end_date, 
                                  device_mac, router_id, event_type,
                                  page, page_size
GET    /api/connections/export  - Export connection data (CSV/JSON)
                                  Query params: format, filters
```

**Router Endpoints**
```
GET    /api/routers             - List configured routers
POST   /api/routers             - Add new router
GET    /api/routers/{id}        - Get router details
PUT    /api/routers/{id}        - Update router configuration
DELETE /api/routers/{id}        - Remove router
POST   /api/routers/{id}/test   - Test router connection
GET    /api/routers/{id}/status - Get router connection status
```

**Filter Rules Endpoints**
```
GET    /api/filters/allowlist   - Get allowlist
POST   /api/filters/allowlist   - Add to allowlist
DELETE /api/filters/allowlist/{mac} - Remove from allowlist
GET    /api/filters/blocklist   - Get blocklist
POST   /api/filters/blocklist   - Add to blocklist
DELETE /api/filters/blocklist/{mac} - Remove from blocklist
POST   /api/filters/import      - Bulk import MAC addresses (CSV)
```

**Analytics Endpoints**
```
GET    /api/analytics/connections-24h    - Connection count over 24 hours
GET    /api/analytics/connections-7d     - Connection count over 7 days
GET    /api/analytics/top-devices        - Top 10 most frequent devices
GET    /api/analytics/peak-times         - Peak connection times
GET    /api/analytics/unique-devices-30d - Unique devices in 30 days
GET    /api/analytics/avg-duration       - Average connection duration per device
```

**Configuration Endpoints**
```
GET    /api/config              - Get application configuration
PUT    /api/config              - Update configuration
POST   /api/config/reload       - Reload configuration from file
```

**WebSocket Endpoint**
```
WS     /ws                      - WebSocket for real-time updates
```

---

## Data Models

### Database Schema

**devices table**
```sql
CREATE TABLE devices (
    mac_address TEXT PRIMARY KEY,
    ip_address TEXT,
    hostname TEXT,
    vendor TEXT,
    friendly_name TEXT,
    notes TEXT,
    trusted BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_devices_friendly_name ON devices(friendly_name);
CREATE INDEX idx_devices_last_seen ON devices(last_seen);
```


**connection_events table (time-series optimized)**
```sql
CREATE TABLE connection_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    mac_address TEXT NOT NULL,
    ip_address TEXT,
    hostname TEXT,
    router_id TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- 'connected' or 'disconnected'
    connection_duration INTEGER,  -- seconds, for disconnection events
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mac_address) REFERENCES devices(mac_address),
    FOREIGN KEY (router_id) REFERENCES routers(id)
);

CREATE INDEX idx_conn_events_timestamp ON connection_events(timestamp DESC);
CREATE INDEX idx_conn_events_mac ON connection_events(mac_address);
CREATE INDEX idx_conn_events_router ON connection_events(router_id);
CREATE INDEX idx_conn_events_type ON connection_events(event_type);
```

**routers table**
```sql
CREATE TABLE routers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    protocol TEXT NOT NULL,  -- 'snmp', 'ssh', 'http_api', 'arp'
    host TEXT NOT NULL,
    port INTEGER,
    credentials TEXT NOT NULL,  -- JSON encrypted credentials
    model TEXT,
    firmware_version TEXT,
    last_scan_timestamp TIMESTAMP,
    last_scan_status TEXT,  -- 'success', 'failed', 'never_scanned'
    scan_interval INTEGER DEFAULT 30,  -- seconds
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**users table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_username ON users(username);
```

**filter_rules table**
```sql
CREATE TABLE filter_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address TEXT NOT NULL,
    rule_type TEXT NOT NULL,  -- 'allowlist' or 'blocklist'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mac_address, rule_type)
);

CREATE INDEX idx_filter_rules_mac ON filter_rules(mac_address);
CREATE INDEX idx_filter_rules_type ON filter_rules(rule_type);
```

**sessions table**
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_sessions_expires ON sessions(expires_at);
```


### Domain Models (Python)

**Device**
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Device:
    mac_address: str
    ip_address: Optional[str]
    hostname: Optional[str]
    vendor: Optional[str]
    friendly_name: Optional[str]
    notes: Optional[str]
    trusted: bool
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime
```

**ConnectionEvent**
```python
from enum import Enum

class EventType(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

@dataclass
class ConnectionEvent:
    id: Optional[int]
    timestamp: datetime
    mac_address: str
    ip_address: Optional[str]
    hostname: Optional[str]
    router_id: str
    event_type: EventType
    connection_duration: Optional[int]  # seconds
```

**DeviceConnection** (scan result)
```python
@dataclass
class DeviceConnection:
    mac_address: str
    ip_address: str
    hostname: Optional[str]
    timestamp: datetime
```

**Router**
```python
class RouterProtocol(str, Enum):
    SNMP = "snmp"
    SSH = "ssh"
    HTTP_API = "http_api"
    ARP = "arp"

@dataclass
class Router:
    id: str
    name: str
    protocol: RouterProtocol
    host: str
    port: Optional[int]
    credentials: dict  # Varies by protocol
    model: Optional[str]
    firmware_version: Optional[str]
    last_scan_timestamp: Optional[datetime]
    last_scan_status: str
    scan_interval: int
    enabled: bool
```

**NotificationConfig**
```python
@dataclass
class NotificationConfig:
    browser_enabled: bool
    email_enabled: bool
    webhook_enabled: bool
    smtp_host: Optional[str]
    smtp_port: Optional[int]
    smtp_username: Optional[str]
    smtp_password: Optional[str]
    email_recipients: List[str]
    webhook_urls: List[str]
    notify_on_known_device: bool
```

