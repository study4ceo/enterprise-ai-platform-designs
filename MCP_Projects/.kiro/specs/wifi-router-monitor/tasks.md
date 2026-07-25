# Implementation Plan: WiFi Router Connection Monitor

## Overview

This implementation plan breaks down the WiFi Router Connection Monitor into discrete coding tasks that build incrementally. The application will be developed using Python 3.11+ with FastAPI for the backend, React with TypeScript for the frontend, PostgreSQL for data storage, and WebSocket for real-time updates. The architecture follows a layered approach with protocol adapters, business services, data repositories, and REST/WebSocket APIs.

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Initialize Poetry project with Python 3.11+
  - Configure project structure: `/backend`, `/frontend`, `/docker`
  - Create `pyproject.toml` with core dependencies: FastAPI, SQLAlchemy, pysnmp, netmiko, httpx, passlib, APScheduler, aiosmtplib, mac-vendor-lookup
  - Set up development tooling: Black, Ruff, mypy, pytest
  - Create `.env.example` with configuration template
  - Create Docker Compose file for PostgreSQL development database
  - _Requirements: 10.1, 10.6_

- [x]* 1.1 Set up backend testing framework
  - Configure pytest with pytest-asyncio for async test support
  - Create test directory structure matching source structure
  - Set up test fixtures for database and mock router connections
  - _Requirements: 15.1_

- [x] 2. Implement database models and repositories
  - [x] 2.1 Create SQLAlchemy database models
    - Define `Device` model with MAC address, IP, hostname, vendor, friendly name, notes, trusted flag, timestamps
    - Define `ConnectionEvent` model with timestamp, device reference, router reference, event type, connection duration
    - Define `Router` model with ID, name, protocol, host, port, encrypted credentials, scan settings
    - Define `User` model with username, password hash, timestamps
    - Define `FilterRule` model for allowlist/blocklist MAC addresses
    - Define `Session` model for authentication sessions
    - Add database indexes on MAC addresses, timestamps, and foreign keys
    - _Requirements: 2.5, 5.1, 5.7, 11.2, 14.2_

  - [ ]* 2.2 Write unit tests for database models
    - Test model creation and validation
    - Test relationship mappings
    - Test index effectiveness
    - _Requirements: 15.3_

  - [x] 2.3 Implement repository layer
    - Create `DeviceRepository` with methods: get_by_mac, create, update, search, get_all
    - Create `ConnectionEventRepository` with methods: create, query_by_filters, get_by_date_range, count
    - Create `RouterRepository` with methods: get_all, get_by_id, create, update, delete
    - Create `UserRepository` with methods: get_by_username, create
    - Create `FilterRuleRepository` with methods: get_allowlist, get_blocklist, add_rule, remove_rule
    - Create `SessionRepository` with methods: create, get_by_id, delete, cleanup_expired
    - _Requirements: 2.5, 5.3, 6.6, 8.5, 11.2, 14.2_

  - [ ]* 2.4 Write unit tests for repositories
    - Test CRUD operations for each repository
    - Test query filtering and pagination
    - Test error handling for constraint violations
    - _Requirements: 5.4, 5.5_


- [ ] 3. Implement router protocol adapters
  - [x] 3.1 Create SNMP adapter
    - Implement `SNMPAdapter` class with connection management using pysnmp
    - Implement `get_connected_devices()` method to query SNMP OIDs for device table
    - Implement `test_connection()` method to validate SNMP connectivity
    - Support SNMPv1, v2c, and v3 protocols
    - Handle SNMP timeouts and authentication errors
    - _Requirements: 1.1, 1.5, 2.1, 2.2_

  - [ ]* 3.2 Write unit tests for SNMP adapter
    - Mock SNMP responses and test device extraction
    - Test connection error handling
    - Test timeout scenarios
    - _Requirements: 1.6, 13.1_

  - [x] 3.3 Create SSH adapter
    - Implement `SSHAdapter` class using netmiko
    - Implement device type detection for common routers (Cisco, Ubiquiti, MikroTik)
    - Implement `get_connected_devices()` method to execute router commands and parse output
    - Implement `test_connection()` method to validate SSH connectivity
    - Handle SSH authentication failures and command timeouts
    - _Requirements: 1.2, 1.5, 2.1, 2.2_

  - [ ]* 3.4 Write unit tests for SSH adapter
    - Mock SSH connections and command outputs
    - Test device parsing for different router types
    - Test error handling for authentication failures
    - _Requirements: 1.6, 13.1_

  - [ ] 3.5 Create HTTP API adapter
    - Implement `HTTPAPIAdapter` class using httpx async client
    - Implement `get_connected_devices()` method to query router REST APIs
    - Implement `test_connection()` method to validate API authentication
    - Support common router APIs (Ubiquiti UniFi, TP-Link Omada)
    - Handle API authentication tokens and rate limiting
    - _Requirements: 1.3, 1.5, 2.1, 2.2_

  - [ ]* 3.6 Write unit tests for HTTP API adapter
    - Mock HTTP API responses
    - Test device extraction from API responses
    - Test authentication and rate limit handling
    - _Requirements: 1.6, 13.1_

  - [ ] 3.7 Create ARP scanner adapter
    - Implement `ARPScanner` class for local network scanning
    - Implement `get_connected_devices()` method to scan ARP table
    - Support CIDR notation for network range specification
    - Handle platform-specific ARP table access (Linux, Windows, macOS)
    - _Requirements: 1.4, 2.1, 2.2_

  - [ ]* 3.8 Write unit tests for ARP scanner
    - Mock ARP table data
    - Test network range parsing
    - Test cross-platform compatibility
    - _Requirements: 1.6_


- [x] 4. Implement MAC vendor lookup service
  - [x] 4.1 Create MAC vendor lookup service
    - Integrate `mac-vendor-lookup` library
    - Implement `MACVendorLookup` class with caching layer
    - Implement `get_vendor(mac_address)` method with fallback for unknown vendors
    - Handle OUI database updates and initialization
    - Cache vendor lookups in memory to reduce repeated lookups
    - _Requirements: 2.3_

  - [ ]* 4.2 Write unit tests for MAC vendor lookup
    - Test vendor identification for known MAC prefixes
    - Test cache functionality
    - Test handling of invalid MAC addresses
    - _Requirements: 2.3_

- [ ] 5. Implement device manager service
  - [x] 5.1 Create device manager service
    - Implement `DeviceManagerService` class
    - Implement `get_or_create_device()` method to retrieve or create device profiles
    - Implement `update_device_metadata()` method for friendly names, notes, trust levels
    - Implement `search_devices()` method for multi-field search
    - Implement `is_new_device()` method to check first-time connections
    - Update first_seen and last_seen timestamps automatically
    - Integrate MAC vendor lookup for new devices
    - _Requirements: 2.4, 2.6, 2.7, 6.1, 6.2, 6.3, 6.4, 6.7_

  - [ ]* 5.2 Write unit tests for device manager
    - Test device creation and retrieval logic
    - Test metadata update functionality
    - Test search with various query types
    - Test new device detection logic
    - _Requirements: 2.4, 6.5_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement notification service
  - [ ] 7.1 Create notification configuration models
    - Define `NotificationConfig` dataclass
    - Implement configuration loading from YAML/JSON
    - Support email SMTP settings, webhook URLs, browser push settings
    - _Requirements: 7.7, 10.4_

  - [ ] 7.2 Implement email notification client
    - Create `EmailClient` class using aiosmtplib
    - Implement async `send_notification()` method
    - Format email templates for new device alerts
    - Handle SMTP authentication and connection errors
    - _Requirements: 7.3, 7.6_

  - [ ]* 7.3 Write unit tests for email client
    - Mock SMTP connection
    - Test email formatting and delivery
    - Test error handling for SMTP failures
    - _Requirements: 7.6, 13.7_

  - [ ] 7.4 Implement webhook notification client
    - Create `WebhookClient` class using httpx
    - Implement async `post_notification()` method
    - Format JSON payloads for webhook endpoints
    - Handle webhook timeout and retry logic
    - _Requirements: 7.4_

  - [ ]* 7.5 Write unit tests for webhook client
    - Mock HTTP POST requests
    - Test JSON payload formatting
    - Test retry logic for failed webhooks
    - _Requirements: 7.4, 13.7_


  - [ ] 7.6 Implement notification service with filtering
    - Create `NotificationService` class
    - Implement `should_notify()` method to evaluate filter rules (allowlist, blocklist, trusted)
    - Implement `send_notifications()` method to dispatch to all enabled channels
    - Implement priority levels for blocklisted device alerts
    - Support configuration for notifying on known device reconnections
    - _Requirements: 7.1, 7.8, 8.1, 8.2, 8.3, 8.4, 8.7_

  - [ ]* 7.7 Write integration tests for notification service
    - Test filter rule evaluation logic
    - Test multi-channel notification dispatch
    - Test priority alert handling for blocklisted devices
    - _Requirements: 8.2, 8.4, 8.7_

- [ ] 8. Implement router scanner service
  - [x] 8.1 Create router scanner service
    - Implement `RouterScannerService` class
    - Implement `scan_router()` method to query router and return device list
    - Implement protocol adapter selection based on router configuration
    - Compare current scan with previous scan to detect connections/disconnections
    - Calculate connection duration for disconnection events
    - Handle router connection errors with logging
    - _Requirements: 2.1, 3.1, 3.4, 3.5, 3.6, 3.7, 13.1_

  - [ ]* 8.2 Write unit tests for router scanner
    - Mock protocol adapters
    - Test connection/disconnection detection logic
    - Test connection duration calculation
    - Test error handling for scan failures
    - _Requirements: 3.4, 3.6, 13.3, 13.7_

  - [ ] 8.3 Implement scheduled scanning with APScheduler
    - Integrate APScheduler for periodic router scanning
    - Implement `start_scanning()` method to schedule scans for all enabled routers
    - Implement `stop_scanning()` method to gracefully shut down scanners
    - Support configurable scan intervals per router (5-300 seconds, default 30)
    - Implement independent scanning for multiple routers
    - _Requirements: 3.1, 3.2, 3.3, 14.1, 14.3_

  - [ ]* 8.4 Write integration tests for scheduled scanning
    - Test scan scheduling and execution
    - Test multi-router scanning
    - Test scan interval configuration
    - _Requirements: 3.2, 14.3_

- [ ] 9. Implement connection event handler
  - [ ] 9.1 Create connection event handler
    - Implement `ConnectionEventHandler` class
    - Implement `handle_connection_event()` method to process new connections
    - Implement `handle_disconnection_event()` method to process disconnections
    - Write connection records to database via repository
    - Trigger notification service for new device connections
    - Broadcast events to WebSocket manager for real-time updates
    - _Requirements: 5.1, 5.2, 7.1, 14.7_

  - [ ]* 9.2 Write unit tests for event handler
    - Test connection event processing
    - Test disconnection event processing
    - Test integration with notification service
    - Test event broadcasting
    - _Requirements: 5.1, 5.2, 7.1_


- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement authentication and security
  - [ ] 11.1 Implement password hashing service
    - Create `AuthService` class using passlib with bcrypt
    - Implement `hash_password()` method with work factor of 12
    - Implement `verify_password()` method for authentication
    - _Requirements: 11.3_

  - [ ]* 11.2 Write unit tests for authentication service
    - Test password hashing and verification
    - Test bcrypt work factor
    - Test invalid password handling
    - _Requirements: 11.3, 11.5_

  - [ ] 11.3 Implement session management
    - Create `SessionManager` class
    - Implement `create_session()` method with 30-minute default timeout
    - Implement `validate_session()` method to check session validity
    - Implement `delete_session()` method for logout
    - Implement `cleanup_expired_sessions()` background task
    - Generate secure random session IDs
    - _Requirements: 11.4, 11.2_

  - [ ]* 11.4 Write unit tests for session management
    - Test session creation and validation
    - Test session expiration logic
    - Test expired session cleanup
    - _Requirements: 11.4_

  - [ ] 11.5 Implement authentication middleware
    - Create FastAPI authentication dependency
    - Validate session tokens for protected endpoints
    - Return 401 Unauthorized for invalid sessions
    - Log authentication attempts with timestamp and source IP
    - _Requirements: 11.1, 11.8_

  - [ ]* 11.6 Write integration tests for authentication
    - Test login flow with valid credentials
    - Test login rejection with invalid credentials
    - Test protected endpoint access with valid session
    - Test protected endpoint rejection without session
    - _Requirements: 11.1, 11.5_

- [ ] 12. Implement REST API endpoints
  - [ ] 12.1 Create authentication endpoints
    - Implement `POST /api/auth/login` for user authentication
    - Implement `POST /api/auth/logout` for session termination
    - Implement `GET /api/auth/session` for session validation
    - Return generic error messages for failed authentication
    - _Requirements: 11.1, 11.2, 11.5_

  - [ ] 12.2 Create device endpoints
    - Implement `GET /api/devices` to list all device profiles
    - Implement `GET /api/devices/{mac}` to get device by MAC address
    - Implement `PUT /api/devices/{mac}` to update device metadata
    - Implement `GET /api/devices/search?q={query}` for device search
    - Return 404 for non-existent devices
    - _Requirements: 4.1, 4.2, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ] 12.3 Create connection history endpoints
    - Implement `GET /api/connections` with filtering by date range, device, router, event type
    - Implement pagination with default page size of 50
    - Implement `GET /api/connections/export` for CSV/JSON export
    - Support query parameters for filtering export data
    - _Requirements: 5.3, 5.4, 5.5, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_


  - [ ] 12.4 Create router endpoints
    - Implement `GET /api/routers` to list configured routers
    - Implement `POST /api/routers` to add new router
    - Implement `GET /api/routers/{id}` to get router details
    - Implement `PUT /api/routers/{id}` to update router configuration
    - Implement `DELETE /api/routers/{id}` to remove router
    - Implement `POST /api/routers/{id}/test` to test router connection
    - Implement `GET /api/routers/{id}/status` to get router connection status
    - Encrypt router credentials before storing in database
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 14.1, 14.2, 14.6_

  - [ ] 12.5 Create filter rules endpoints
    - Implement `GET /api/filters/allowlist` to get allowlist
    - Implement `POST /api/filters/allowlist` to add to allowlist
    - Implement `DELETE /api/filters/allowlist/{mac}` to remove from allowlist
    - Implement `GET /api/filters/blocklist` to get blocklist
    - Implement `POST /api/filters/blocklist` to add to blocklist
    - Implement `DELETE /api/filters/blocklist/{mac}` to remove from blocklist
    - Implement `POST /api/filters/import` for bulk CSV import
    - _Requirements: 8.1, 8.3, 8.5, 8.6_

  - [ ] 12.6 Create analytics endpoints
    - Implement `GET /api/analytics/connections-24h` for 24-hour connection chart data
    - Implement `GET /api/analytics/connections-7d` for 7-day connection chart data
    - Implement `GET /api/analytics/top-devices` for top 10 frequent devices
    - Implement `GET /api/analytics/peak-times` for peak connection times
    - Implement `GET /api/analytics/unique-devices-30d` for unique device count
    - Implement `GET /api/analytics/avg-duration` for average connection duration per device
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ] 12.7 Create configuration endpoints
    - Implement `GET /api/config` to get application configuration
    - Implement `PUT /api/config` to update configuration
    - Implement `POST /api/config/reload` to reload configuration from file
    - Validate configuration values before applying
    - _Requirements: 10.1, 10.7, 10.8_

  - [ ]* 12.8 Write integration tests for REST API
    - Test all endpoints with valid and invalid inputs
    - Test authentication requirements for protected endpoints
    - Test error responses and status codes
    - Test pagination and filtering
    - _Requirements: 4.1, 4.2, 5.3, 5.4, 5.5, 11.1_

- [ ] 13. Implement WebSocket manager for real-time updates
  - [ ] 13.1 Create WebSocket manager
    - Implement `WebSocketManager` class
    - Implement `connect()` method to accept new WebSocket connections
    - Implement `disconnect()` method to remove connections
    - Implement `broadcast_connection_event()` method to send events to all clients
    - Implement `broadcast_device_update()` method for device metadata changes
    - Maintain dictionary of active WebSocket connections by session ID
    - Handle WebSocket connection errors and automatic cleanup
    - _Requirements: 4.3, 4.4, 4.5_

  - [ ]* 13.2 Write integration tests for WebSocket
    - Test WebSocket connection establishment
    - Test event broadcasting to multiple clients
    - Test connection cleanup on disconnect
    - _Requirements: 4.3, 4.4_

  - [ ] 13.3 Implement WebSocket endpoint
    - Create `WS /ws` endpoint in FastAPI
    - Validate authentication token before accepting WebSocket connection
    - Send initial state (active connections, router status) upon connection
    - Implement heartbeat/ping mechanism to detect disconnected clients
    - _Requirements: 4.5, 11.1_


- [ ] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Implement configuration management
  - [ ] 15.1 Create configuration loader
    - Implement `ConfigLoader` class supporting YAML and JSON formats
    - Define configuration schema with validation using Pydantic
    - Load router connection parameters, scan intervals, notification settings, retention period, web server settings
    - Provide default values for all configuration options
    - Implement configuration validation with descriptive error messages
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.8_

  - [ ]* 15.2 Write unit tests for configuration loader
    - Test configuration loading from YAML and JSON
    - Test validation for invalid configuration values
    - Test default value application
    - _Requirements: 10.8_

  - [ ] 15.3 Implement configuration hot reload
    - Implement file watcher for configuration file changes
    - Reload configuration without application restart
    - Update router scanner intervals dynamically
    - Update notification settings dynamically
    - Log configuration reload events
    - _Requirements: 10.7_

  - [ ]* 15.4 Write integration tests for hot reload
    - Test configuration changes are applied without restart
    - Test scanner interval updates
    - Test notification setting updates
    - _Requirements: 10.7_

- [ ] 16. Implement data retention and cleanup
  - [ ] 16.1 Create data retention service
    - Implement `DataRetentionService` class
    - Implement `cleanup_old_connections()` method to delete connection records older than retention period
    - Default retention period to 90 days
    - Schedule cleanup task to run daily
    - Log cleanup operations with record counts
    - _Requirements: 5.7_

  - [ ]* 16.2 Write unit tests for data retention
    - Test connection record deletion based on age
    - Test retention period configuration
    - _Requirements: 5.7_

- [ ] 17. Implement error handling and resilience
  - [ ] 17.1 Implement router reconnection logic
    - Add retry mechanism to router scanner for connection failures
    - Attempt reconnection every 60 seconds after router connection loss
    - Track router connection state (connected, disconnected, error)
    - Log reconnection attempts and results
    - _Requirements: 13.1, 13.2, 13.3_

  - [ ] 17.2 Implement connection event queue
    - Create in-memory queue for connection events when database is unavailable
    - Limit queue to 1000 events maximum
    - Persist queued events when database becomes available
    - Discard oldest events if queue capacity exceeded
    - Log warnings for queue overflow
    - _Requirements: 13.4, 13.5, 13.6_

  - [ ]* 17.3 Write integration tests for error handling
    - Test router reconnection after failure
    - Test event queueing during database unavailability
    - Test queue overflow handling
    - _Requirements: 13.1, 13.3, 13.4, 13.5, 13.6_

  - [ ] 17.4 Implement comprehensive logging
    - Configure structured logging with timestamps, log levels, and context
    - Log all errors with error type and context information
    - Log authentication attempts with timestamp and source IP
    - Log router scan failures and reconnection attempts
    - Write logs to persistent log file with rotation
    - _Requirements: 11.8, 13.7_


- [ ] 18. Implement HTTPS support
  - [ ] 18.1 Add HTTPS configuration
    - Support SSL certificate and key file configuration
    - Configure FastAPI to use SSL/TLS when HTTPS is enabled
    - Reject HTTP connections when HTTPS is enabled
    - Provide clear documentation for certificate generation (self-signed or Let's Encrypt)
    - _Requirements: 11.6, 11.7_

  - [ ]* 18.2 Write integration tests for HTTPS
    - Test HTTPS endpoint access
    - Test HTTP rejection when HTTPS is enabled
    - _Requirements: 11.6, 11.7_

- [ ] 19. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Set up frontend React application
  - [ ] 20.1 Initialize React project with TypeScript
    - Create React app using Vite with TypeScript template
    - Install dependencies: Material-UI, React Router, React Query, Recharts
    - Configure TypeScript with strict mode
    - Set up project structure: `/components`, `/pages`, `/services`, `/hooks`, `/types`
    - Configure Vite for development and production builds
    - _Requirements: 4.1_

  - [ ] 20.2 Create API client service
    - Implement `ApiClient` class for REST API communication
    - Configure base URL and authentication token headers
    - Implement methods for all REST endpoints
    - Handle HTTP errors and authentication failures
    - _Requirements: 4.1, 11.1_

  - [ ] 20.3 Implement WebSocket client
    - Create `WebSocketClient` class for real-time updates
    - Implement connection management with automatic reconnection
    - Implement event listeners for connection events and device updates
    - Handle connection errors and disconnection
    - _Requirements: 4.3, 4.4, 4.5_

- [ ] 21. Implement frontend authentication
  - [ ] 21.1 Create login page
    - Build login form with username and password fields
    - Implement form validation
    - Call authentication API on submit
    - Store session token in local storage or secure cookie
    - Redirect to dashboard on successful login
    - Display error message for failed authentication
    - _Requirements: 11.1, 11.5_

  - [ ] 21.2 Implement authentication context
    - Create React Context for authentication state
    - Provide login, logout, and session validation methods
    - Implement protected route wrapper for authenticated pages
    - Redirect to login page when session expires
    - _Requirements: 11.1, 11.4_

- [ ] 22. Implement active connections dashboard
  - [ ] 22.1 Create active connections view
    - Build table component displaying currently active devices
    - Show MAC address, IP address, hostname, vendor, connection time
    - Display friendly names when available
    - Implement real-time updates via WebSocket
    - Display total count of active connections
    - Show router connection status indicators
    - Display last scan timestamp
    - Update within 2 seconds of connection/disconnection events
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 4.7, 4.8, 6.5, 14.4, 14.6_

  - [ ]* 22.2 Write frontend component tests
    - Test active connections table rendering
    - Test WebSocket update handling
    - Test connection status indicators
    - _Requirements: 4.1, 4.2, 4.3, 4.4_


- [ ] 23. Implement connection history view
  - [ ] 23.1 Create connection history page
    - Build table component showing connection records
    - Display timestamp, device information, event type, connection duration
    - Implement date range filtering with date pickers
    - Implement device filtering dropdown
    - Implement event type filtering (connected/disconnected)
    - Implement router filtering for multi-router setups
    - Implement pagination with page size of 50
    - Show connection duration for disconnection events
    - _Requirements: 5.3, 5.4, 5.5, 5.6, 14.5_

  - [ ]* 23.2 Write frontend component tests for history view
    - Test connection history rendering
    - Test filtering functionality
    - Test pagination controls
    - _Requirements: 5.3, 5.4, 5.5_

- [ ] 24. Implement device management view
  - [ ] 24.1 Create device management page
    - Build table component listing all device profiles
    - Display MAC address, IP, hostname, vendor, friendly name, notes, trust status
    - Implement device search with query input
    - Implement edit functionality for friendly names and notes
    - Implement trust/untrust toggle button
    - Show first seen and last seen timestamps
    - Display friendly names in place of MAC addresses where available
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ]* 24.2 Write frontend component tests for device management
    - Test device list rendering
    - Test search functionality
    - Test metadata editing
    - Test trust status toggle
    - _Requirements: 6.1, 6.2, 6.3, 6.7_

- [ ] 25. Implement filter rules management
  - [ ] 25.1 Create filter rules page
    - Build allowlist management section with table of allowed devices
    - Build blocklist management section with table of blocked devices
    - Implement add/remove functionality for both lists
    - Implement bulk CSV import with file upload
    - Provide CSV template download
    - Display device information for filtered MAC addresses
    - _Requirements: 8.1, 8.3, 8.5, 8.6_

  - [ ]* 25.2 Write frontend component tests for filter rules
    - Test allowlist/blocklist display
    - Test add/remove operations
    - Test CSV import functionality
    - _Requirements: 8.5, 8.6_

- [ ] 26. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 27. Implement analytics dashboard
  - [ ] 27.1 Create analytics page
    - Build chart component for 24-hour connection count using Recharts
    - Build chart component for 7-day connection count using Recharts
    - Display top 10 most frequently connected devices table
    - Display average connection duration per device
    - Display peak connection times chart
    - Display unique devices count for past 30 days
    - Fetch analytics data from REST API endpoints
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 27.2 Write frontend component tests for analytics
    - Test chart rendering with mock data
    - Test analytics data fetching
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 28. Implement router management view
  - [ ] 28.1 Create router management page
    - Build table component listing configured routers
    - Display router name, protocol, host, status, last scan time
    - Implement add router form with protocol selection
    - Implement edit router functionality
    - Implement delete router with confirmation
    - Implement test connection button showing results
    - Display connection status indicators for each router
    - _Requirements: 1.5, 1.6, 14.1, 14.2, 14.6_

  - [ ]* 28.2 Write frontend component tests for router management
    - Test router list rendering
    - Test add/edit/delete operations
    - Test connection test functionality
    - _Requirements: 1.5, 1.6_


- [ ] 29. Implement configuration settings view
  - [ ] 29.1 Create configuration settings page
    - Build form for notification settings (browser, email, webhook)
    - Build form for SMTP configuration (host, port, username, password, recipients)
    - Build form for webhook URL configuration
    - Build form for scan interval configuration
    - Build form for connection history retention period
    - Build toggle for notifying on known device reconnections
    - Implement save configuration functionality
    - Implement reload configuration from file functionality
    - Display current configuration values
    - _Requirements: 7.7, 7.8, 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 29.2 Write frontend component tests for settings
    - Test settings form rendering
    - Test configuration save functionality
    - _Requirements: 7.7, 10.1_

- [ ] 30. Implement data export functionality
  - [ ] 30.1 Create export feature in connection history
    - Add export button to connection history page
    - Implement format selection (CSV or JSON)
    - Apply current filters to export data
    - Download exported file to user's browser
    - Display loading indicator during export generation
    - Show error message if export fails or times out
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

  - [ ]* 30.2 Write frontend component tests for export
    - Test export button functionality
    - Test format selection
    - Test filter application to exports
    - _Requirements: 12.2, 12.3, 12.5, 12.6_

- [ ] 31. Implement browser notifications
  - [ ] 31.1 Implement browser push notifications
    - Request notification permission from user
    - Implement notification display when new device events received via WebSocket
    - Show MAC address, IP, hostname, vendor in notification
    - Implement notification click handler to navigate to dashboard
    - Respect notification enable/disable setting from configuration
    - _Requirements: 7.2, 7.5_

  - [ ]* 31.2 Write frontend component tests for notifications
    - Test notification permission request
    - Test notification display on WebSocket events
    - _Requirements: 7.2, 7.5_

- [ ] 32. Implement responsive UI styling
  - [ ] 32.1 Style all components with Material-UI
    - Apply Material-UI theme for consistent styling
    - Implement responsive layouts for mobile, tablet, desktop
    - Add loading spinners and skeleton screens for async operations
    - Style tables, forms, buttons, and cards
    - Implement dark/light theme toggle
    - Ensure accessibility compliance (ARIA labels, keyboard navigation)
    - _Requirements: 4.1, 15.2_

- [ ] 33. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 34. Implement Docker containerization
  - [ ] 34.1 Create Dockerfile for backend
    - Create multi-stage Dockerfile for Python backend
    - Use Python 3.11+ base image
    - Install dependencies via Poetry
    - Copy application code
    - Expose FastAPI port (default 8000)
    - Configure healthcheck endpoint
    - _Requirements: 10.6_

  - [ ] 34.2 Create Dockerfile for frontend
    - Create multi-stage Dockerfile for React frontend
    - Use Node.js for build stage
    - Build production-optimized bundle with Vite
    - Use nginx for serving static files
    - Configure nginx for SPA routing
    - Expose port 80
    - _Requirements: 4.1_


  - [ ] 34.3 Create Docker Compose configuration
    - Create `docker-compose.yml` for full application stack
    - Define services: backend, frontend, PostgreSQL database
    - Configure networking between services
    - Configure volume mounts for database persistence and configuration files
    - Set environment variables for service configuration
    - Configure health checks for all services
    - _Requirements: 10.6_

- [ ] 35. Implement database migrations
  - [ ] 35.1 Set up Alembic for database migrations
    - Initialize Alembic in the backend project
    - Create initial migration for all database tables
    - Implement migration scripts for schema changes
    - Document migration process in README
    - _Requirements: 2.5, 15.3_

  - [ ] 35.2 Create database initialization script
    - Create script to initialize database with default admin user
    - Create sample router configurations for testing
    - Document database setup process
    - _Requirements: 11.2_

- [ ] 36. Implement performance optimizations
  - [ ] 36.1 Add database query optimizations
    - Verify indexes on MAC addresses and timestamps
    - Implement query result caching for analytics endpoints
    - Use database connection pooling
    - Optimize connection history queries with proper pagination
    - _Requirements: 15.1, 15.3, 15.4, 15.5_

  - [ ] 36.2 Implement frontend performance optimizations
    - Implement React Query caching for API responses
    - Use React.memo for expensive component renders
    - Implement virtualized scrolling for large device lists
    - Lazy load analytics charts
    - Optimize WebSocket message handling to prevent re-renders
    - _Requirements: 15.2, 15.7_

  - [ ]* 36.3 Write performance tests
    - Test API response times with large datasets
    - Test dashboard render times with 500 active connections
    - Test WebSocket update latency
    - _Requirements: 15.1, 15.2, 15.4, 15.6_

- [ ] 37. Create deployment documentation
  - [ ] 37.1 Write installation and setup guide
    - Document system requirements
    - Document Docker installation steps
    - Document configuration file setup
    - Document router configuration examples for SNMP, SSH, HTTP API
    - Document initial user creation
    - Document HTTPS certificate setup
    - _Requirements: 1.1, 1.2, 1.3, 11.6_

  - [ ] 37.2 Write user guide
    - Document dashboard navigation
    - Document device management workflows
    - Document filter rules configuration
    - Document notification setup
    - Document analytics interpretation
    - Document data export procedures
    - _Requirements: 4.1, 6.1, 7.7, 8.5, 9.1, 12.1_

  - [ ] 37.3 Write operational guide
    - Document log file locations and rotation
    - Document backup procedures for database
    - Document upgrade procedures
    - Document troubleshooting common issues
    - Document performance tuning recommendations
    - _Requirements: 13.7, 15.6_

- [ ] 38. Final integration and end-to-end testing
  - [ ]* 38.1 Write end-to-end tests
    - Test complete user workflow: login, view devices, configure router, receive notifications
    - Test multi-router monitoring scenario
    - Test data export workflow
    - Test error recovery scenarios
    - _Requirements: 14.1, 14.3_

  - [ ] 38.2 Perform manual testing and bug fixes
    - Test all features manually across different browsers
    - Test with real router connections (SNMP, SSH, HTTP API)
    - Verify notification delivery (email, webhook, browser)
    - Test performance with large datasets
    - Fix any bugs identified during testing
    - _Requirements: 1.1, 1.2, 1.3, 7.3, 7.4, 15.1_


- [ ] 39. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks that can be skipped for faster MVP delivery
- Each task references specific requirements from the requirements document for traceability
- The implementation follows an incremental approach: database → protocol adapters → business services → API → frontend
- Checkpoints ensure validation at logical breaks in the implementation
- Property-based testing is not applicable for this infrastructure/integration application
- Unit tests validate individual components while integration tests validate cross-component workflows
- The task list assumes all design and requirements documents are available during implementation
- Router credential encryption should use industry-standard encryption (e.g., AES-256)
- Database connection pooling improves performance under high load
- WebSocket heartbeat prevents stale connections
- Configuration hot reload eliminates downtime for setting changes
- Multi-router support enables enterprise deployments
- HTTPS support is critical for production deployments
- Docker containerization simplifies deployment across different environments

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1"] },
    { "id": 1, "tasks": ["2.2", "2.3"] },
    { "id": 2, "tasks": ["2.4", "3.1", "3.3", "3.5", "3.7", "4.1"] },
    { "id": 3, "tasks": ["3.2", "3.4", "3.6", "3.8", "4.2", "5.1"] },
    { "id": 4, "tasks": ["5.2", "7.1"] },
    { "id": 5, "tasks": ["7.2", "7.4"] },
    { "id": 6, "tasks": ["7.3", "7.5", "7.6"] },
    { "id": 7, "tasks": ["7.7", "8.1"] },
    { "id": 8, "tasks": ["8.2", "8.3"] },
    { "id": 9, "tasks": ["8.4", "9.1"] },
    { "id": 10, "tasks": ["9.2", "11.1"] },
    { "id": 11, "tasks": ["11.2", "11.3"] },
    { "id": 12, "tasks": ["11.4", "11.5"] },
    { "id": 13, "tasks": ["11.6", "12.1"] },
    { "id": 14, "tasks": ["12.2", "12.3", "12.4", "12.5", "12.6", "12.7"] },
    { "id": 15, "tasks": ["12.8", "13.1"] },
    { "id": 16, "tasks": ["13.2", "13.3"] },
    { "id": 17, "tasks": ["15.1"] },
    { "id": 18, "tasks": ["15.2", "15.3"] },
    { "id": 19, "tasks": ["15.4", "16.1"] },
    { "id": 20, "tasks": ["16.2", "17.1", "17.2"] },
    { "id": 21, "tasks": ["17.3", "17.4", "18.1"] },
    { "id": 22, "tasks": ["18.2", "20.1"] },
    { "id": 23, "tasks": ["20.2", "20.3"] },
    { "id": 24, "tasks": ["21.1", "21.2"] },
    { "id": 25, "tasks": ["22.1"] },
    { "id": 26, "tasks": ["22.2", "23.1"] },
    { "id": 27, "tasks": ["23.2", "24.1"] },
    { "id": 28, "tasks": ["24.2", "25.1"] },
    { "id": 29, "tasks": ["25.2", "27.1"] },
    { "id": 30, "tasks": ["27.2", "28.1"] },
    { "id": 31, "tasks": ["28.2", "29.1"] },
    { "id": 32, "tasks": ["29.2", "30.1"] },
    { "id": 33, "tasks": ["30.2", "31.1"] },
    { "id": 34, "tasks": ["31.2", "32.1"] },
    { "id": 35, "tasks": ["34.1", "34.2"] },
    { "id": 36, "tasks": ["34.3", "35.1"] },
    { "id": 37, "tasks": ["35.2", "36.1", "36.2"] },
    { "id": 38, "tasks": ["36.3", "37.1", "37.2", "37.3"] },
    { "id": 39, "tasks": ["38.1", "38.2"] }
  ]
}
```
