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
- **Web Framework**: FastAPI (async, high-performance, built-in WebSocket support)
- **Router Communication Libraries**:
  - SNMP: `pysnmp` (pure Python, v1/v2c/v3 support)
  - SSH: `netmiko` (built on Paramiko, optimized for network devices)
  - HTTP/HTTPS: `httpx` (async HTTP client for router APIs)
  - Network scanning: `scapy` (packet manipulation and ARP scanning)
- **MAC Vendor Lookup**: `manuf` (OUI database lookup from Wireshark)
- **Database**: PostgreSQL 15+ (robust time-series support, excellent indexing, JSONB for flexible data)
- **ORM**: SQLAlchemy 2.0+ with async support
- **Authentication**: `passlib` with bcrypt for password hashing, `python-jose` for JWT tokens
- **Task Scheduling**: `APScheduler` for periodic router scanning with async support
- **Notifications**: 
  - Email: `aiosmtplib` (async SMTP client)
  - Webhooks: `httpx` (async HTTP POST)
- **Configuration**: YAML config files via `PyYAML`
- **Logging**: `structlog` for structured logging

**Frontend:**
- **Framework**: Next.js 14+ (App Router) with TypeScript
- **Styling**: Tailwind CSS with custom component library
- **UI Components**: Custom components built with Tailwind, shadcn/ui for base components
- **State Management**: React Context API + TanStack Query (React Query) for server state
- **Real-Time Communication**: Native WebSocket API with automatic reconnection
- **Charts**: Recharts for connection analytics visualization
- **Form Handling**: React Hook Form with Zod validation
- **HTTP Client**: Axios with interceptors for authentication
- **Build Tool**: Built-in Next.js with Turbopack

**Development & Deployment:**
- **Package Management**: 
  - Backend: Poetry for Python dependency management
  - Frontend: npm/pnpm for JavaScript dependencies
- **Code Quality**: 
  - Backend: Black (formatting), Ruff (linting), mypy (type checking)
  - Frontend: ESLint, Prettier, TypeScript strict mode
- **Testing**: 
  - Backend: pytest, pytest-asyncio for async tests, pytest-cov for coverage
  - Frontend: Jest, React Testing Library, Playwright for E2E
- **Containerization**: Docker with multi-stage builds for both backend and frontend
- **Process Management**: Docker Compose for local development and deployment
- **Database Migrations**: Alembic for PostgreSQL schema migrations

**Rationale:**
- **Python + FastAPI**: Excellent ecosystem for network/router monitoring libraries (pysnmp, netmiko, scapy), FastAPI provides async performance and built-in WebSocket support
- **PostgreSQL**: Superior to SQLite for production use with better concurrent connections, advanced indexing, JSONB for flexible credential storage, and proven time-series performance
- **Next.js**: Production-ready React framework with built-in routing, SSR, API routes, and optimization
- **Tailwind CSS**: Rapid UI development with utility-first approach, easy customization, smaller bundle sizes
- **Docker**: Ensures consistent deployment across environments, easy scaling, and portability

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
    mac_address VARCHAR(17) PRIMARY KEY,
    ip_address INET,
    hostname VARCHAR(255),
    vendor VARCHAR(255),
    friendly_name VARCHAR(255),
    notes TEXT,
    trusted BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_devices_friendly_name ON devices(friendly_name);
CREATE INDEX idx_devices_last_seen ON devices(last_seen DESC);
CREATE INDEX idx_devices_vendor ON devices(vendor);
CREATE INDEX idx_devices_trusted ON devices(trusted);
```


**connection_events table (time-series optimized)**
```sql
CREATE TABLE connection_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    mac_address VARCHAR(17) NOT NULL,
    ip_address INET,
    hostname VARCHAR(255),
    router_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('connected', 'disconnected')),
    connection_duration INTEGER,  -- seconds, for disconnection events
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mac_address) REFERENCES devices(mac_address) ON DELETE CASCADE,
    FOREIGN KEY (router_id) REFERENCES routers(id) ON DELETE CASCADE
);

-- Primary index for time-series queries
CREATE INDEX idx_conn_events_timestamp ON connection_events(timestamp DESC);

-- Composite indexes for common query patterns
CREATE INDEX idx_conn_events_mac_timestamp ON connection_events(mac_address, timestamp DESC);
CREATE INDEX idx_conn_events_router_timestamp ON connection_events(router_id, timestamp DESC);
CREATE INDEX idx_conn_events_type_timestamp ON connection_events(event_type, timestamp DESC);

-- For analytics queries
CREATE INDEX idx_conn_events_mac_type ON connection_events(mac_address, event_type);

-- Partition table by month for better performance (PostgreSQL 10+)
-- CREATE TABLE connection_events_y2024m01 PARTITION OF connection_events
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**routers table**
```sql
CREATE TABLE routers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    protocol VARCHAR(20) NOT NULL CHECK (protocol IN ('snmp', 'ssh', 'http_api', 'arp')),
    host VARCHAR(255) NOT NULL,
    port INTEGER,
    credentials JSONB NOT NULL,  -- Encrypted JSON credentials specific to protocol
    model VARCHAR(255),
    firmware_version VARCHAR(100),
    last_scan_timestamp TIMESTAMP WITH TIME ZONE,
    last_scan_status VARCHAR(20) CHECK (last_scan_status IN ('success', 'failed', 'never_scanned')),
    scan_interval INTEGER DEFAULT 30 CHECK (scan_interval BETWEEN 5 AND 300),
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_routers_enabled ON routers(enabled);
CREATE INDEX idx_routers_last_scan ON routers(last_scan_timestamp DESC);
```

**users table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

**filter_rules table**
```sql
CREATE TABLE filter_rules (
    id SERIAL PRIMARY KEY,
    mac_address VARCHAR(17) NOT NULL,
    rule_type VARCHAR(20) NOT NULL CHECK (rule_type IN ('allowlist', 'blocklist')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mac_address, rule_type)
);

CREATE INDEX idx_filter_rules_mac ON filter_rules(mac_address);
CREATE INDEX idx_filter_rules_type ON filter_rules(rule_type);
```

**sessions table**
```sql
CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_expires ON sessions(expires_at);
CREATE INDEX idx_sessions_user ON sessions(user_id);
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



---

## Correctness Properties

**Property-Based Testing is NOT APPLICABLE for this feature.**

### Why No Properties Are Defined

This application is an infrastructure monitoring tool that primarily orchestrates I/O operations and side effects rather than performing algorithmic transformations. Property-based testing (PBT) is inappropriate for the following reasons:

#### 1. Infrastructure-as-Code Pattern (Not Algorithmic Logic)
- **Core operations**: Query routers via SNMP/SSH/HTTP, persist to database, send notifications
- **Testing need**: Verify external integrations work, not algorithmic correctness
- **Analogy**: Similar to Terraform or AWS CDK — infrastructure tools are validated through integration tests, not PBT

#### 2. No Universal Properties Exist
Consider the main workflow:
```python
async def scan_router(self, router_id: str):
    devices = await self.router_adapter.get_devices()  # I/O
    for device in devices:
        await self.db.save(device)  # Side effect
        await self.notify(device)    # Side effect
```

**What would a property test?**
- "For all device lists... what?" — there's no transformation or invariant
- The function performs I/O and side effects, not data transformation
- Success means: router responded, database wrote, notification sent

#### 3. Side-Effect Dominant Operations
- Database writes (connection events, device profiles) — needs DB integration testing
- SMTP email sending — needs mock SMTP server verification
- WebSocket broadcasts — needs connected client verification  
- Router communication — needs protocol-specific integration tests

#### 4. State Management Over Pure Functions
- Tracks device connection state changes over time
- Manages authentication sessions
- Queues events when services unavailable
- **These require state-based testing with specific scenarios, not randomized property generation**

### Alternative Testing Strategy

**Our comprehensive testing approach (detailed in [Testing Strategy](#testing-strategy)):**

| Test Type | Purpose | Example |
|-----------|---------|---------|
| **Unit Tests** (80% coverage) | Business logic with concrete scenarios | Filter rule evaluation, device metadata updates |
| **Integration Tests** (all integrations) | Verify external services work | PostgreSQL operations, SNMP/SSH adapters, email delivery |
| **E2E Tests** (critical paths) | Validate complete workflows | Login → View devices → Configure router → Export data |
| **Performance Tests** | Verify scalability requirements | 500 devices, 10K records, 10 concurrent users |

### Example: Why Integration Tests Are Superior Here

**Testing Device Connection Detection:**

❌ **Property-Based Test Approach (ineffective)**:
```python
@given(st.lists(st.from_type(DeviceConnection)))
def test_scan_detects_new_devices(device_list):
    # What property would we test? This is I/O, not transformation
    result = scan_router(device_list)
    assert ???  # No universal property exists
```

✅ **Integration Test Approach (effective)**:
```python
async def test_snmp_adapter_detects_real_device():
    """WHEN router has connected device THEN SNMP adapter extracts it"""
    adapter = SNMPAdapter(host="192.168.1.1", community="public")
    devices = await adapter.get_connected_devices()
    
    assert len(devices) > 0
    assert all(device.mac_address for device in devices)
    assert all(device.ip_address for device in devices)
```

The integration test verifies:
- SNMP communication works
- OID queries return data  
- MAC/IP extraction succeeds
- Actual router protocol behavior

This catches real bugs that property tests cannot: network timeouts, wrong OIDs, parsing errors, authentication failures.

### Conclusion

For infrastructure monitoring applications that orchestrate I/O and side effects, **integration tests, example-based unit tests, and E2E tests provide superior coverage** compared to property-based testing. The testing strategy section below details our comprehensive approach for ensuring correctness.

---

## Error Handling

### Router Communication Errors

**Connection Failures**
- **Scenario**: Router unreachable via configured protocol
- **Handling**:
  1. Log error with timestamp, router ID, and error details
  2. Update `routers.last_scan_status` to 'failed'
  3. Display warning indicator in Dashboard
  4. Retry on next scan interval (controlled by APScheduler)
  5. After 5 consecutive failures, send admin notification

**Authentication Failures**
- **Scenario**: Invalid credentials for SNMP, SSH, or HTTP API
- **Handling**:
  1. Log authentication failure with router ID
  2. Mark router as 'failed' with descriptive error message
  3. Display error in Dashboard with "Test Connection" action button
  4. Do not retry automatically (requires user intervention)

**Timeout Errors**
- **Scenario**: Router query exceeds timeout threshold (default 30s)
- **Handling**:
  1. Cancel pending operation
  2. Log timeout error
  3. Treat as temporary failure and retry on next interval
  4. If timeouts persist, suggest increasing scan interval

**Protocol-Specific Errors**
- **SNMP**: OID not found, version mismatch
- **SSH**: Command execution failure, prompt detection issues
- **HTTP API**: Invalid JSON response, endpoint not found
- **Handling**: Log specific error, attempt fallback protocol if configured

### Database Errors

**Connection Failure**
- **Scenario**: PostgreSQL database unreachable
- **Handling**:
  1. Queue connection events in memory (max 1000 events in `ConnectionEventHandler`)
  2. Continue router scanning and store results in memory
  3. Display warning banner in Dashboard
  4. Attempt database reconnection every 60 seconds
  5. When reconnected, flush queued events to database
  6. If queue exceeds 1000 events, discard oldest events (FIFO) and log warning

**Query Timeout**
- **Scenario**: Long-running query exceeds timeout
- **Handling**:
  1. Cancel query using PostgreSQL statement timeout
  2. Return error to API client with 504 Gateway Timeout
  3. Log slow query for optimization analysis
  4. Suggest pagination or narrower filters to user

**Constraint Violations**
- **Scenario**: Duplicate MAC address, foreign key violation
- **Handling**:
  1. Catch SQLAlchemy exceptions
  2. Return 409 Conflict with descriptive error message
  3. For duplicate devices, fetch existing record instead

**Migration Failures**
- **Scenario**: Alembic migration fails during deployment
- **Handling**:
  1. Rollback migration automatically
  2. Log detailed error with migration version
  3. Prevent application startup
  4. Require manual intervention

### WebSocket Errors

**Connection Drops**
- **Scenario**: Client WebSocket connection lost
- **Handling**:
  1. Remove from `active_connections` in `WebSocketManager`
  2. Client implements exponential backoff reconnection (1s, 2s, 4s, max 30s)
  3. On reconnect, send full state update to client

**Broadcast Failures**
- **Scenario**: Message send fails to specific client
- **Handling**:
  1. Log error with session ID
  2. Remove dead connection from active connections
  3. Continue broadcasting to other clients

**Invalid Messages**
- **Scenario**: Client sends malformed WebSocket message
- **Handling**:
  1. Validate message schema
  2. Send error response to client
  3. Do not disconnect (allow retry)

### Notification Errors

**Email Delivery Failure**
- **Scenario**: SMTP server unreachable or email rejected
- **Handling**:
  1. Log error with device MAC and error details
  2. Retry up to 3 times with exponential backoff
  3. If all retries fail, log final failure and continue
  4. Do not block connection event processing

**Webhook Failure**
- **Scenario**: Webhook endpoint returns non-2xx status or timeout
- **Handling**:
  1. Log error with webhook URL, device MAC, and HTTP status
  2. Retry once after 5 seconds
  3. If retry fails, log and continue (do not block)

**Browser Push Failure**
- **Scenario**: Browser not connected or push subscription expired
- **Handling**:
  1. Fail silently (expected when dashboard not open)
  2. Log debug message only
  3. No retries needed

### Configuration Errors

**Invalid Configuration File**
- **Scenario**: YAML syntax error or invalid values
- **Handling**:
  1. Log validation errors with line numbers
  2. Use default values for invalid fields
  3. Send warning notification to admin
  4. Application continues with defaults

**Missing Required Configuration**
- **Scenario**: Required field (e.g., database connection string) missing
- **Handling**:
  1. Log critical error
  2. Refuse application startup
  3. Provide clear error message with expected format

**Configuration Reload Failure**
- **Scenario**: Runtime configuration reload encounters errors
- **Handling**:
  1. Keep current configuration
  2. Log error and notify user via API response
  3. Do not apply partial updates

### Resource Exhaustion

**Memory Limit Exceeded**
- **Scenario**: Connection event queue or device cache grows too large
- **Handling**:
  1. Implement LRU eviction for in-memory caches
  2. Log warning when approaching memory limits
  3. Discard oldest queued events if limit exceeded
  4. Consider persisting to disk if memory pressure continues

**Too Many Concurrent Connections**
- **Scenario**: More than 10 dashboard users connected simultaneously
- **Handling**:
  1. Accept connection but log warning
  2. If exceeds 50 connections, reject new WebSocket connections with 503 error
  3. Suggest horizontal scaling in logs

**Database Connection Pool Exhaustion**
- **Scenario**: All database connections in use
- **Handling**:
  1. Queue requests with timeout (5 seconds)
  2. Return 503 Service Unavailable if timeout exceeded
  3. Log error and suggest increasing pool size

### Security Errors

**Authentication Failures**
- **Scenario**: Invalid username/password or expired session
- **Handling**:
  1. Return 401 Unauthorized with generic message
  2. Log attempt with username, timestamp, and source IP
  3. Implement rate limiting (5 attempts per minute per IP)
  4. Lock account after 10 failed attempts in 1 hour

**HTTPS Certificate Errors**
- **Scenario**: Invalid or expired SSL certificate
- **Handling**:
  1. Refuse to start application if HTTPS enabled with invalid cert
  2. Log detailed error message
  3. Provide instructions for generating valid certificate

**CSRF Token Validation Failure**
- **Scenario**: Missing or invalid CSRF token
- **Handling**:
  1. Return 403 Forbidden
  2. Log warning with session ID
  3. Client should refresh token and retry

### Error Logging Strategy

**Log Levels:**
- **DEBUG**: Scan results, device lookups, WebSocket messages
- **INFO**: Successful connections, configuration changes, new device detection
- **WARNING**: Temporary failures, queue near capacity, slow queries
- **ERROR**: Connection failures, database errors, notification failures
- **CRITICAL**: Application startup failures, database unavailable

**Log Format (Structured JSON):**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "component": "RouterScanner",
  "router_id": "router-1",
  "message": "SNMP connection failed",
  "error": "Timeout waiting for response",
  "context": {
    "host": "192.168.1.1",
    "protocol": "snmp"
  }
}
```

**Log Rotation:**
- Rotate logs daily
- Keep 30 days of logs
- Compress rotated logs
- Max log file size: 100MB

---

## Testing Strategy

### Overview

The WiFi Router Connection Monitor requires comprehensive testing across multiple layers to ensure reliability, correctness, and performance. Testing will NOT use property-based testing (PBT) because:

1. **Infrastructure-Driven**: The application heavily relies on external systems (routers, databases, SMTP servers) where behavior doesn't vary meaningfully with input structure
2. **State-Heavy**: Testing focuses on state transitions and side effects (database writes, notifications) rather than pure functions
3. **Integration-Critical**: Most bugs occur at integration boundaries, not in algorithmic logic

**Instead, the testing strategy focuses on:**
- **Unit Tests**: For business logic, data transformations, and pure functions
- **Integration Tests**: For database operations, router communication, and external services
- **E2E Tests**: For critical user workflows through the dashboard
- **Mock-Based Tests**: For isolating components during unit testing

### Unit Testing

**Target Components:**
- Device Manager Service (device profile operations)
- Notification Service (filter rule evaluation)
- Analytics Service (aggregation calculations)
- Data validation and serialization
- Utility functions (MAC address formatting, OUI lookup)

**Framework**: pytest with pytest-asyncio for async tests

**Example Test Cases:**

```python
# tests/unit/test_device_manager.py
import pytest
from datetime import datetime
from services.device_manager import DeviceManagerService

@pytest.mark.asyncio
async def test_is_new_device_returns_true_for_unseen_mac():
    """WHEN checking a MAC address not in database THEN is_new_device returns True"""
    device_manager = DeviceManagerService(mock_device_repo, mock_mac_lookup)
    assert device_manager.is_new_device("AA:BB:CC:DD:EE:FF") is True

@pytest.mark.asyncio
async def test_get_or_create_device_creates_profile_for_new_device():
    """WHEN calling get_or_create_device with new MAC THEN device profile is created"""
    device_manager = DeviceManagerService(mock_device_repo, mock_mac_lookup)
    device = await device_manager.get_or_create_device(
        mac="AA:BB:CC:DD:EE:FF",
        ip="192.168.1.100",
        hostname="phone"
    )
    assert device.mac_address == "AA:BB:CC:DD:EE:FF"
    assert device.vendor is not None  # OUI lookup performed

@pytest.mark.asyncio
async def test_update_device_metadata_updates_friendly_name():
    """WHEN updating device metadata THEN changes persist"""
    device_manager = DeviceManagerService(mock_device_repo, mock_mac_lookup)
    await device_manager.update_device_metadata(
        mac="AA:BB:CC:DD:EE:FF",
        friendly_name="John's Phone"
    )
    device = await device_manager.get_device("AA:BB:CC:DD:EE:FF")
    assert device.friendly_name == "John's Phone"

# tests/unit/test_notification_service.py
@pytest.mark.asyncio
async def test_should_notify_returns_false_for_trusted_device():
    """WHEN device is marked trusted THEN should_notify returns False"""
    notification_service = NotificationService(mock_filter_repo, mock_email, mock_webhook, config)
    device = Device(mac_address="AA:BB:CC:DD:EE:FF", trusted=True, ...)
    decision = await notification_service.should_notify(device, is_new=False)
    assert decision.should_notify is False

@pytest.mark.asyncio
async def test_should_notify_returns_high_priority_for_blocklisted_device():
    """WHEN device is blocklisted THEN should_notify returns high priority"""
    notification_service = NotificationService(mock_filter_repo, mock_email, mock_webhook, config)
    # Setup: Add device to blocklist
    await mock_filter_repo.add_blocklist("AA:BB:CC:DD:EE:FF")
    device = Device(mac_address="AA:BB:CC:DD:EE:FF", ...)
    decision = await notification_service.should_notify(device, is_new=True)
    assert decision.should_notify is True
    assert decision.priority == "high"

# tests/unit/test_analytics_service.py
@pytest.mark.asyncio
async def test_calculate_avg_duration_returns_correct_average():
    """WHEN calculating average connection duration THEN correct value returned"""
    analytics_service = AnalyticsService(mock_connection_repo)
    # Setup: Create connection events with known durations
    await mock_connection_repo.add_event(
        mac="AA:BB:CC:DD:EE:FF",
        event_type="disconnected",
        connection_duration=3600  # 1 hour
    )
    await mock_connection_repo.add_event(
        mac="AA:BB:CC:DD:EE:FF",
        event_type="disconnected",
        connection_duration=7200  # 2 hours
    )
    avg = await analytics_service.get_avg_duration("AA:BB:CC:DD:EE:FF")
    assert avg == 5400  # 1.5 hours in seconds
```

**Coverage Goal**: 80% code coverage for service layer

**Test Configuration:**
- Use pytest fixtures for mock dependencies
- Use `pytest-mock` for mocking external calls
- Use `freezegun` for time-dependent tests
- Use `pytest-cov` for coverage reporting

### Integration Testing

**Target Areas:**
- Database operations (SQLAlchemy with PostgreSQL)
- Router protocol adapters (SNMP, SSH, HTTP API, ARP)
- Email notification delivery
- Webhook HTTP POST requests
- WebSocket message broadcasting

**Framework**: pytest with test containers for PostgreSQL

**Example Test Cases:**

```python
# tests/integration/test_database.py
import pytest
from testcontainers.postgres import PostgresContainer
from repositories.device_repository import DeviceRepository

@pytest.fixture(scope="module")
def postgres():
    """Start PostgreSQL container for integration tests"""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.mark.asyncio
async def test_device_repository_create_and_retrieve(postgres):
    """WHEN creating device in database THEN it can be retrieved"""
    repo = DeviceRepository(postgres.get_connection_url())
    await repo.create_device(
        mac="AA:BB:CC:DD:EE:FF",
        ip="192.168.1.100",
        hostname="test-device"
    )
    device = await repo.get_device("AA:BB:CC:DD:EE:FF")
    assert device.mac_address == "AA:BB:CC:DD:EE:FF"
    assert device.ip_address == "192.168.1.100"

@pytest.mark.asyncio
async def test_connection_events_query_by_date_range(postgres):
    """WHEN querying connection events by date range THEN correct events returned"""
    repo = ConnectionRepository(postgres.get_connection_url())
    # Create events with different timestamps
    await repo.create_event(mac="AA:BB:CC:DD:EE:FF", timestamp=datetime(2024, 1, 1, 10, 0))
    await repo.create_event(mac="AA:BB:CC:DD:EE:FF", timestamp=datetime(2024, 1, 2, 10, 0))
    await repo.create_event(mac="AA:BB:CC:DD:EE:FF", timestamp=datetime(2024, 1, 3, 10, 0))
    
    events = await repo.query_events(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2, 23, 59)
    )
    assert len(events) == 2

# tests/integration/test_router_adapters.py
@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("TEST_ROUTER_HOST"), reason="No test router configured")
async def test_snmp_adapter_retrieves_devices():
    """WHEN querying router via SNMP THEN devices are returned"""
    adapter = SNMPAdapter(
        host=os.getenv("TEST_ROUTER_HOST"),
        port=161,
        community="public",
        version="2c"
    )
    devices = await adapter.get_connected_devices()
    assert isinstance(devices, list)
    for device in devices:
        assert device.mac_address is not None
        assert device.ip_address is not None

# tests/integration/test_notifications.py
@pytest.mark.asyncio
async def test_email_notification_sends_successfully(smtp_mock_server):
    """WHEN sending email notification THEN email is delivered"""
    email_client = EmailClient(
        smtp_host="localhost",
        smtp_port=smtp_mock_server.port
    )
    device = Device(mac_address="AA:BB:CC:DD:EE:FF", ip_address="192.168.1.100", ...)
    await email_client.send_notification(device)
    
    # Verify email received by mock server
    messages = smtp_mock_server.get_messages()
    assert len(messages) == 1
    assert "AA:BB:CC:DD:EE:FF" in messages[0].body

@pytest.mark.asyncio
async def test_webhook_notification_posts_to_endpoint(httpx_mock):
    """WHEN sending webhook notification THEN HTTP POST is made"""
    httpx_mock.add_response(status_code=200)
    webhook_client = WebhookClient()
    device = Device(mac_address="AA:BB:CC:DD:EE:FF", ...)
    
    await webhook_client.send_notification(device, "https://example.com/webhook")
    
    request = httpx_mock.get_request()
    assert request.method == "POST"
    assert "AA:BB:CC:DD:EE:FF" in request.content.decode()
```

**Coverage Goal**: All database queries, external service integrations

**Test Environment:**
- Use Docker test containers for PostgreSQL
- Mock SMTP server for email tests (aiosmtpd)
- Mock HTTP server for webhook tests (pytest-httpx)
- Optional: Real test router for protocol adapter testing (CI skip if unavailable)

### End-to-End Testing

**Target Workflows:**
1. User login flow
2. View active devices on dashboard
3. Add new router configuration
4. Update device friendly name
5. Export connection history
6. Configure notification settings

**Framework**: Playwright for browser automation

**Example Test Cases:**

```python
# tests/e2e/test_dashboard.py
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_user_can_login_and_view_dashboard():
    """WHEN user logs in with valid credentials THEN dashboard is displayed"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to login page
        await page.goto("http://localhost:3000/login")
        
        # Fill credentials
        await page.fill('input[name="username"]', "admin")
        await page.fill('input[name="password"]', "password123")
        await page.click('button[type="submit"]')
        
        # Verify redirect to dashboard
        await page.wait_for_url("http://localhost:3000/dashboard")
        assert "Active Devices" in await page.content()

@pytest.mark.asyncio
async def test_real_time_device_appears_on_dashboard():
    """WHEN new device connects THEN it appears on dashboard via WebSocket"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Login and navigate to dashboard
        await login(page)
        
        # Simulate device connection event (trigger backend)
        await trigger_device_connection("AA:BB:CC:DD:EE:FF", "192.168.1.100")
        
        # Verify device appears within 2 seconds
        await page.wait_for_selector(f'[data-mac="AA:BB:CC:DD:EE:FF"]', timeout=2000)
        device_element = await page.query_selector(f'[data-mac="AA:BB:CC:DD:EE:FF"]')
        assert device_element is not None

@pytest.mark.asyncio
async def test_user_can_update_device_friendly_name():
    """WHEN user updates device friendly name THEN change is saved"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await login(page)
        
        # Click on device to open details
        await page.click('[data-mac="AA:BB:CC:DD:EE:FF"]')
        
        # Update friendly name
        await page.fill('input[name="friendlyName"]', "John's Laptop")
        await page.click('button:has-text("Save")')
        
        # Verify update
        await page.wait_for_selector('text="Saved successfully"')
        await page.reload()
        assert "John's Laptop" in await page.content()
```

**Coverage Goal**: All critical user workflows

**Test Environment:**
- Full stack running (backend + frontend + database)
- Docker Compose for orchestration
- Seed data for consistent test state

### Performance Testing

**Target Metrics:**
- **Scan Performance**: 500 devices scanned in < 5 seconds
- **Database Queries**: Connection history queries (10K records) < 2 seconds
- **WebSocket Broadcast**: Updates delivered to 10 clients < 100ms
- **Memory Usage**: < 512MB with 500 active connections
- **API Response Time**: 95th percentile < 200ms

**Tools**: locust for load testing, memory_profiler for memory analysis

**Example Load Test:**

```python
# tests/performance/test_load.py
from locust import HttpUser, task, between

class DashboardUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tasks"""
        self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "password123"
        })
    
    @task(3)
    def view_active_devices(self):
        """Simulate viewing active devices"""
        self.client.get("/api/devices")
    
    @task(2)
    def view_connection_history(self):
        """Simulate viewing connection history"""
        self.client.get("/api/connections?page=1&page_size=50")
    
    @task(1)
    def view_analytics(self):
        """Simulate viewing analytics"""
        self.client.get("/api/analytics/connections-24h")

# Run with: locust -f tests/performance/test_load.py --users 50 --spawn-rate 5
```

### Testing Best Practices

**1. Test Data Management:**
- Use factories (factory_boy) for creating test objects
- Use database migrations in tests (same as production)
- Reset database state between tests

**2. Async Testing:**
- Always use `@pytest.mark.asyncio` for async tests
- Use `pytest-asyncio` event loop fixture
- Properly await all async calls

**3. Mocking Strategy:**
- Mock external services (routers, SMTP, webhooks)
- Use real database for integration tests (test containers)
- Mock time-dependent code with `freezegun`

**4. Test Organization:**
```
tests/
├── unit/
│   ├── test_device_manager.py
│   ├── test_notification_service.py
│   └── test_analytics_service.py
├── integration/
│   ├── test_database.py
│   ├── test_router_adapters.py
│   └── test_notifications.py
├── e2e/
│   ├── test_dashboard.py
│   └── test_workflows.py
├── performance/
│   └── test_load.py
└── conftest.py  # Shared fixtures
```

**5. CI/CD Integration:**
- Run unit tests on every commit (fast feedback)
- Run integration tests on pull requests
- Run E2E tests on staging deployment
- Run performance tests weekly

**6. Test Coverage Requirements:**
- Unit tests: 80% coverage minimum
- Integration tests: All repository methods
- E2E tests: All critical user workflows (login, view devices, add router, export data)

**7. Flaky Test Prevention:**
- Use explicit waits in E2E tests (not sleep)
- Isolate test data (unique IDs per test)
- Cleanup resources in teardown
- Use retry decorators only for inherently flaky external services

### Manual Testing Checklist

**Pre-Release Validation:**
- [ ] Test with real router (SNMP, SSH, HTTP API)
- [ ] Verify WebSocket reconnection after network interruption
- [ ] Test with 100+ devices over 24 hours (stability)
- [ ] Verify email notifications delivered
- [ ] Test CSV/JSON export with large datasets
- [ ] Verify HTTPS with valid certificate
- [ ] Test across browsers (Chrome, Firefox, Safari)
- [ ] Verify mobile responsiveness
- [ ] Test database migration from previous version
- [ ] Verify log rotation and disk usage

---

## Implementation Notes

### Development Workflow

**1. Backend Development:**
```bash
# Setup Poetry environment
poetry install

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
poetry run pytest tests/ -v --cov=app

# Lint and format
poetry run ruff check .
poetry run black .
poetry run mypy .
```

**2. Frontend Development:**
```bash
# Install dependencies
pnpm install

# Start development server (with backend proxy)
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Lint and format
pnpm lint
pnpm format
```

**3. Docker Development:**
```bash
# Start full stack
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up -d --build

# Run database migrations in container
docker-compose exec backend alembic upgrade head

# Access database shell
docker-compose exec db psql -U postgres -d wifi_monitor
```

### Deployment Considerations

**Environment Variables:**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/wifi_monitor
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Docker Compose Production:**
```yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: wifi_monitor
      POSTGRES_USER: wifi_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    restart: unless-stopped

  backend:
    build: ./backend
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://wifi_user:${DB_PASSWORD}@db:5432/wifi_monitor
    restart: unless-stopped
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    restart: unless-stopped
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

**Security Hardening:**
- Run containers as non-root user
- Use secrets management (Docker secrets, HashiCorp Vault)
- Enable HTTPS with Let's Encrypt certificates
- Implement rate limiting on API endpoints
- Regular security updates for base images

### Monitoring and Observability

**Metrics to Track:**
- Router scan success/failure rate
- Average scan duration per router
- Database query performance
- WebSocket connection count
- Memory and CPU usage
- API endpoint latency (p50, p95, p99)
- Error rate by component

**Logging:**
- Structured JSON logs with `structlog`
- Log aggregation to centralized system (e.g., ELK stack)
- Alert on critical errors (database down, all routers failing)

**Health Checks:**
```python
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "database": await check_database(),
        "routers": await check_router_connections()
    }
```

### Scalability Considerations

**Horizontal Scaling:**
- Backend: Multiple FastAPI instances behind load balancer (nginx, HAProxy)
- Frontend: Stateless Next.js instances
- Database: PostgreSQL read replicas for analytics queries
- WebSocket: Sticky sessions or Redis pub/sub for multi-instance coordination

**Vertical Scaling:**
- Increase database connection pool size
- Increase APScheduler thread pool for more concurrent scans
- Optimize PostgreSQL (shared_buffers, work_mem, effective_cache_size)

**Data Retention:**
- Implement automatic cleanup of old connection events (>90 days)
- Archive to cold storage if needed
- Use PostgreSQL table partitioning by month for better performance

---

## Conclusion

This technical design provides a comprehensive architecture for the WiFi Router Connection Monitor application using Python + FastAPI for the backend and Next.js + Tailwind CSS for the frontend. The design emphasizes:

- **Reliability**: Robust error handling, retry logic, and graceful degradation
- **Real-Time Performance**: WebSocket-based live updates with sub-second latency
- **Scalability**: PostgreSQL with optimized indexing, connection pooling, horizontal scaling
- **Security**: bcrypt password hashing, HTTPS support, session management, rate limiting
- **Maintainability**: Clear separation of concerns, dependency injection, comprehensive testing
- **Observability**: Structured logging, health checks, performance metrics

The implementation will follow industry best practices for modern web applications, with comprehensive testing coverage, Docker-based deployment, and production-ready configuration management.
