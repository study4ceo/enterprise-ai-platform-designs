# WiFi Router Connection Monitor

A standalone application that monitors WiFi routers for new device connections and displays real-time connection information on a dashboard. Perfect for network administrators who need visibility into network activity, security monitoring, and device management.

## Features

- **Multi-Protocol Support**: Connect to routers via SNMP, SSH, HTTP API, or ARP scanning
- **Real-Time Dashboard**: WebSocket-powered live updates with sub-2-second latency
- **Device Management**: Assign friendly names, notes, and trust levels to devices
- **Smart Notifications**: Browser push, email, and webhook alerts with filtering
- **Connection Analytics**: Charts, reports, and usage pattern analysis
- **Multi-Router Support**: Monitor multiple routers from a single dashboard
- **Secure**: bcrypt password hashing, HTTPS support, session management
- **Data Export**: CSV and JSON export for external analysis

## Technology Stack

### Backend
- **Python 3.11+** with **FastAPI**
- **PostgreSQL 18.4** for data storage
- **WebSocket** for real-time updates
- Router protocols: SNMP, SSH, HTTP API, ARP scanning

### Frontend
- **Next.js 16.2.11** with TypeScript
- **Tailwind CSS** for styling
- **React Query** for state management
- **Recharts** for analytics visualization

### Deployment
- **Docker** and **Docker Compose**
- Production-ready with health checks and logging

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OR: Python 3.11+, Node.js 18+, PostgreSQL 18.4

### Option 1: Docker (Recommended)

```bash
# Clone the repository
cd D:\code_ai\code\project-designs\wifi-router-monitoring

# Start all services
cd docker
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install poetry
poetry install
cp .env.example .env
# Edit .env with your database credentials
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with backend URL
npm run dev
```

## Project Structure

```
wifi-router-monitoring/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── repositories/   # Data access layer
│   │   ├── adapters/       # Router protocol adapters
│   │   ├── services/       # Business logic
│   │   ├── api/            # REST endpoints
│   │   └── websocket/      # WebSocket handlers
│   ├── tests/              # Test suite
│   ├── alembic/            # Database migrations
│   └── config/             # Configuration files
├── frontend/               # Next.js React frontend
│   ├── app/                # Next.js pages (App Router)
│   ├── components/         # React components
│   ├── services/           # API clients
│   └── types/              # TypeScript types
├── docker/                 # Docker configuration
│   └── docker-compose.yml
├── design.md               # Technical design document
├── requirements.md         # Requirements specification
└── tasks.md                # Implementation task list
```

## Configuration

### Router Setup

Edit `backend/config/config.yml` to add your routers:

**SNMP Example:**
```yaml
routers:
  - id: main-router
    name: Main Router
    protocol: snmp
    host: 192.168.1.1
    port: 161
    credentials:
      community: public
      version: "2c"
    scan_interval_seconds: 30
    enabled: true
```

**SSH Example:**
```yaml
  - id: office-router
    name: Office Router
    protocol: ssh
    host: 192.168.2.1
    port: 22
    credentials:
      username: admin
      password: secure-password
      device_type: cisco_ios
    scan_interval_seconds: 60
    enabled: true
```

### Notification Setup

Configure notifications in `backend/.env`:

```env
# Email notifications
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
EMAIL_RECIPIENTS=admin@example.com

# Webhook notifications
WEBHOOK_NOTIFICATIONS_ENABLED=true
WEBHOOK_URLS=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Usage

### Default Credentials

- **Username**: `admin`
- **Password**: `admin` (change immediately after first login)

### Adding a Router

1. Navigate to **Routers** page
2. Click **Add Router**
3. Select protocol (SNMP/SSH/HTTP API/ARP)
4. Enter connection details
5. Click **Test Connection**
6. Click **Save**

### Managing Devices

1. Navigate to **Devices** page
2. Click on any device to edit
3. Add friendly name, notes, or mark as trusted
4. Trusted devices won't trigger notifications

### Setting Up Alerts

1. Navigate to **Settings** → **Notifications**
2. Enable desired notification channels
3. Configure SMTP or webhook settings
4. Navigate to **Filters**
5. Add devices to allowlist (no alerts) or blocklist (high-priority alerts)

### Viewing Analytics

1. Navigate to **Analytics** page
2. View connection charts (24h, 7d)
3. See top devices and peak times
4. Analyze connection patterns

### Exporting Data

1. Navigate to **Connection History**
2. Apply filters (date range, device, router)
3. Click **Export**
4. Select format (CSV or JSON)

## Development

### Backend Development

```bash
cd backend
poetry run pytest                    # Run tests
poetry run black .                   # Format code
poetry run ruff check .              # Lint code
poetry run mypy app                  # Type check
poetry run alembic revision --autogenerate -m "description"  # Create migration
```

### Frontend Development

```bash
cd frontend
npm run dev              # Start dev server
npm run build            # Production build
npm run lint             # Lint code
npm run test             # Run tests
```

## Supported Routers

### SNMP
- Cisco IOS/IOS-XE
- Juniper Junos
- MikroTik RouterOS
- Any router with SNMP support

### SSH
- Cisco IOS/IOS-XE/IOS-XR
- Juniper Junos
- Arista EOS
- Ubiquiti EdgeRouter
- MikroTik RouterOS

### HTTP API
- Ubiquiti UniFi Controller
- TP-Link Omada Controller
- Meraki Dashboard API (with API key)

### ARP Scanner
- Works on any local network
- No router credentials required

## Troubleshooting

### Router Connection Fails

1. Verify router IP and port
2. Check firewall rules
3. For SNMP: Verify community string and SNMP version
4. For SSH: Verify username, password, and device type
5. Use **Test Connection** button for diagnostics

### Notifications Not Received

1. Check notification settings in **Settings** page
2. Verify SMTP credentials (test with [SMTP tools](https://www.smtper.net/))
3. For webhooks, verify URL with `curl` test
4. Check device isn't in allowlist
5. Check logs: `docker-compose logs backend`

### Dashboard Not Updating

1. Check WebSocket connection (browser dev tools → Network → WS)
2. Verify backend is running: `http://localhost:8000/health`
3. Check backend logs for scan errors
4. Verify router scan is enabled

### Database Migration Issues

```bash
# Reset database (development only)
cd backend
poetry run alembic downgrade base
poetry run alembic upgrade head
```

## Security Considerations

- Change default admin password immediately
- Use strong `SECRET_KEY` in production
- Enable HTTPS for production deployments
- Secure PostgreSQL with strong passwords
- Restrict PostgreSQL network access
- Keep router credentials encrypted in database
- Use environment variables for sensitive data

## Performance Tuning

- **Scan Interval**: Increase for large networks (60-120 seconds)
- **Database**: Enable PostgreSQL connection pooling
- **WebSocket**: Limit concurrent connections (default 50)
- **Retention**: Reduce history retention for faster queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest` and `npm test`
5. Submit a pull request

## License

MIT License

## Support

- **Documentation**: See `design.md` for technical details
- **Issues**: Submit issues with logs and error messages
- **Logs**: `docker-compose logs backend` or `backend/logs/app.log`

## Roadmap

- [ ] Mobile app (iOS/Android)
- [ ] Machine learning for anomaly detection
- [ ] Bandwidth monitoring per device
- [ ] Integration with network management tools
- [ ] Support for additional router protocols
- [ ] Advanced reporting and dashboards
