# Setup Guide

## Prerequisites

Install on D: drive:
- Go 1.23+
- Python 3.14+
- Node.js 20+
- PostgreSQL 18+
- Redis 7+

## Database Setup

```sql
-- PostgreSQL
CREATE DATABASE creative_hub;

-- Create tables (run in psql)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE brand_kits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    colors TEXT[],
    fonts TEXT[],
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    type VARCHAR(50),
    content TEXT,
    url TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Go Backend

```bash
cd backend-go
cp .env.example .env
# Edit .env with your credentials

go mod download
go run cmd/server/main.go
```

Access: http://localhost:8080/health

## Python Workers

```bash
cd ai-workers
pip install -r requirements.txt
cp .env.example .env
# Add GROQ_API_KEY to .env

python worker.py
```

## Next.js Frontend

```bash
cd frontend
npm install
cp .env.example .env.local

npm run dev
```

Access: http://localhost:3000

## Testing

**Text Generation:**
```bash
curl -X POST http://localhost:8080/api/generate/text \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a tweet about AI",
    "type": "social",
    "tone": "professional",
    "variants": 3
  }'
```

**Check Job Status:**
```bash
curl http://localhost:8080/api/jobs/{job_id}
```

## Troubleshooting

**Redis not connecting:**
- Start Redis: `redis-server`
- Check port: `redis-cli ping`

**PostgreSQL issues:**
- Check connection: `psql -U postgres`
- Verify database: `\l`

**Go compilation errors:**
- Run: `go mod tidy`
- Update deps: `go get -u ./...`

**Python worker not starting:**
- Check Redis: Connection should show in logs
- Verify API key in .env

**Frontend build fails:**
- Clear cache: `rm -rf .next node_modules`
- Reinstall: `npm install`
