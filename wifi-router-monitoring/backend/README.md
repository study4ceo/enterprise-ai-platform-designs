# WiFi Router Connection Monitor - Backend

FastAPI backend for monitoring WiFi router connections and device tracking.

## Technology Stack

- **Python**: 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 18.4
- **ORM**: SQLAlchemy 2.0+ (async)
- **Router Protocols**: SNMP (pysnmp), SSH (netmiko), HTTP APIs (httpx), ARP scanning (scapy)
- **Authentication**: bcrypt + JWT
- **Task Scheduling**: APScheduler
- **Real-time**: WebSocket

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── database.py              # Database connection and session
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── connection_event.py
│   │   ├── router.py
│   │   ├── user.py
│   │   ├── filter_rule.py
│   │   └── session.py
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   ├── device_repository.py
│   │   ├── connection_repository.py
│   │   ├── router_repository.py
│   │   ├── user_repository.py
│   │   ├── filter_repository.py
│   │   └── session_repository.py
│   ├── adapters/                # Router protocol adapters
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── snmp_adapter.py
│   │   ├── ssh_adapter.py
│   │   ├── http_adapter.py
│   │   └── arp_scanner.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── mac_lookup.py
│   │   ├── device_manager.py
│   │   ├── notification_service.py
│   │   ├── router_scanner.py
│   │   ├── connection_event_handler.py
│   │   ├── auth_service.py
│   │   ├── session_manager.py
│   │   ├── analytics_service.py
│   │   └── data_retention.py
│   ├── api/                     # REST API endpoints
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Auth middleware
│   │   ├── auth.py
│   │   ├── devices.py
│   │   ├── connections.py
│   │   ├── routers.py
│   │   ├── filters.py
│   │   ├── analytics.py
│   │   └── config.py
│   ├── websocket/               # WebSocket handlers
│   │   ├── __init__.py
│   │   └── manager.py
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── logging.py
│       └── encryption.py
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── alembic/                     # Database migrations
│   ├── versions/
│   └── env.py
├── config/                      # Configuration files
│   └── config.example.yml
├── logs/                        # Application logs
├── pyproject.toml               # Poetry dependencies
├── alembic.ini                  # Alembic configuration
├── .env.example                 # Environment variables template
└── README.md
```

## Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)
- PostgreSQL 18.4
- Docker and Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   cd D:\code_ai\code\project-designs\wifi-router-monitoring\backend
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   pip install poetry
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start PostgreSQL** (using Docker Compose)
   ```bash
   cd ../docker
   docker-compose up -d db
   ```

6. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

7. **Create default admin user**
   ```bash
   poetry run python -m app.scripts.create_admin
   ```

### Development

**Start the development server:**
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Run tests:**
```bash
poetry run pytest tests/ -v --cov=app
```

**Format code:**
```bash
poetry run black .
```

**Lint code:**
```bash
poetry run ruff check .
```

**Type check:**
```bash
poetry run mypy app
```

## Configuration

Configuration can be set via:
1. Environment variables (`.env` file)
2. YAML configuration file (`config/config.yml`)

See `.env.example` for all available options.

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_device_manager.py

# Run integration tests only
poetry run pytest tests/integration/
```

## Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

## Deployment

### Using Docker

```bash
cd ../docker
docker-compose up -d
```

### Manual Deployment

1. Set `APP_ENV=production` in `.env`
2. Set a strong `SECRET_KEY`
3. Configure PostgreSQL connection
4. Run migrations: `poetry run alembic upgrade head`
5. Start with: `poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`

## License

MIT
