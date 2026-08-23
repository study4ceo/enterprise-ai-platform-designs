# Chipsana - AI Hardware Performance Calculator

**Tagline:** Make informed decisions about AI infrastructure investments

## Overview

Chipsana is a comprehensive web application for analyzing and comparing AI hardware performance, costs, and infrastructure requirements. Built for ML engineers, infrastructure teams, and technical decision-makers.

## Features

### 1. TCO Calculator
- Compare cloud vs on-premise costs
- 3-5 year projections
- Hardware, electricity, networking, staff costs
- Breakeven analysis

### 2. Cost Per Token Calculator
- Inference cost estimation
- Different model sizes (7B, 70B, 175B+)
- Utilization impact
- Batch size optimization

### 3. GPU Comparison Tool
- Side-by-side comparison of GPUs
- Performance metrics (TFLOPS, bandwidth, memory)
- Cost efficiency analysis
- Use case recommendations

### 4. Performance Estimator
- Roofline model visualization
- MFU (Model FLOPs Utilization) calculator
- Bandwidth requirements
- Bottleneck identification

### 5. Power & Cooling Calculator
- PUE calculations
- Air vs liquid cooling comparison
- Stranded power analysis
- Carbon footprint estimation

### 6. GPU Database
- Comprehensive specs for 50+ accelerators
- NVIDIA (H100, A100, L4, etc.)
- AMD (MI300X, MI250X)
- Google TPU (v4, v5)
- AWS Trainium, Inferentia

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts / Chart.js
- **Forms:** React Hook Form + Zod

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL + Prisma ORM
- **Caching:** Redis
- **API Docs:** Swagger/OpenAPI

### Deployment
- **Frontend:** Vercel
- **Backend:** Railway / Render
- **Database:** Supabase / Neon
- **CDN:** Cloudflare

## Project Structure

```
chipsana.in/
├── frontend/                 # Next.js application
│   ├── app/                 # App router pages
│   │   ├── page.tsx        # Landing page
│   │   ├── calculators/    # Calculator pages
│   │   ├── compare/        # GPU comparison
│   │   └── api/            # API routes (if needed)
│   ├── components/         # React components
│   │   ├── ui/            # shadcn components
│   │   ├── calculators/   # Calculator UI components
│   │   └── charts/        # Chart components
│   ├── lib/               # Utilities, types
│   └── public/            # Static assets
│
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── main.py       # FastAPI app
│   │   ├── routers/      # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── calculators/  # Calculation logic
│   │   └── database/     # DB connection
│   └── requirements.txt
│
├── database/              # Database scripts
│   ├── schema.sql        # Database schema
│   └── seed.sql          # GPU data seeding
│
└── docs/                 # Documentation
    ├── api.md           # API documentation
    └── calculations.md  # Calculation formulas
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- pnpm (recommended) or npm

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/chipsana.git
cd chipsana.in
```

2. Install frontend dependencies
```bash
cd frontend
pnpm install
```

3. Install backend dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/chipsana
REDIS_URL=redis://localhost:6379
```

5. Run database migrations
```bash
cd backend
alembic upgrade head
python seed_database.py  # Seed GPU data
```

6. Start development servers
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
pnpm dev
```

Visit http://localhost:3000

## Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel
```

### Backend (Railway)
```bash
cd backend
railway up
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - See LICENSE file

## Contact

- Website: https://chipsana.in
- Email: hello@chipsana.in
- Twitter: @chipsana_in

## Roadmap

- [x] TCO Calculator
- [x] Cost Per Token Calculator
- [x] GPU Comparison Tool
- [ ] Performance Estimator
- [ ] Power & Cooling Calculator
- [ ] User accounts & saved calculations
- [ ] API for programmatic access
- [ ] Mobile app (React Native)
- [ ] Integration with cloud providers (AWS, GCP, Azure)

## Acknowledgments

- Inspired by SemiAnalysis research
- GPU data from official vendor specifications
- Community feedback and contributions
