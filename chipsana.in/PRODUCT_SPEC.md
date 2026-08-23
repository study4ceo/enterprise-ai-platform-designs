# Chipsana Product Specification

## Executive Summary

**Product Name:** Chipsana  
**Tagline:** AI Hardware Performance Calculator  
**Target Users:** ML Engineers, Infrastructure Teams, CTOs, Finance Teams  
**Problem:** Difficult to compare AI hardware options and calculate true costs  
**Solution:** Web-based calculator suite for AI infrastructure planning  

## Product Vision

Become the go-to platform for AI infrastructure cost analysis and hardware comparison, helping organizations make data-driven decisions about AI investments.

## Target Audience

### Primary Users
1. **ML Infrastructure Engineers** (40%)
   - Need: Compare GPU options for training/inference
   - Pain: Too many options, unclear trade-offs
   - Goal: Optimize performance per dollar

2. **Engineering Managers / CTOs** (30%)
   - Need: Justify cloud vs on-prem decisions
   - Pain: Complex TCO calculations, board presentations
   - Goal: Make informed budget decisions

3. **Finance / Procurement Teams** (20%)
   - Need: Understand AI infrastructure costs
   - Pain: Technical specs are confusing
   - Goal: Budget planning, vendor negotiations

4. **Researchers / Students** (10%)
   - Need: Learn about AI hardware
   - Pain: Information scattered across sources
   - Goal: Education, experimentation

### User Personas

**Persona 1: "Sarah the ML Engineer"**
- Age: 28-35
- Role: Senior ML Engineer at mid-size tech company
- Experience: 5+ years in ML, familiar with GPUs
- Goal: Convince management to invest in A100 cluster vs using cloud
- Pain: Spreadsheet calculations are time-consuming and error-prone
- Features needed: TCO calculator, GPU comparison, performance estimator

**Persona 2: "David the CTO"**
- Age: 38-45
- Role: CTO at AI startup
- Experience: Technical background, not GPU expert
- Goal: Present AI infrastructure strategy to investors
- Pain: Need simple visualizations and ROI justification
- Features needed: Cost per token, TCO comparison, clear charts

**Persona 3: "Lisa the Finance Director"**
- Age: 35-42
- Role: Finance Director, oversees tech spending
- Experience: Finance expert, limited technical knowledge
- Goal: Understand AI infrastructure budget requests
- Pain: Engineers speak in TFLOPs, she speaks in dollars
- Features needed: Simple cost breakdowns, 3-year projections

## Core Features

### 1. TCO Calculator

**Purpose:** Compare total cost of ownership for GPU clusters (cloud vs on-premise)

**Inputs:**
- Number of GPUs
- GPU type (H100, A100, L4, etc.)
- Time horizon (1-5 years)
- Utilization rate (%)
- Electricity cost ($/kWh)
- Cloud pricing (optional override)

**Calculations:**
- Hardware CapEx
- Electricity costs (with PUE)
- Networking costs
- Facility costs
- Maintenance (% of CapEx)
- Staff costs
- Total 3-year TCO

**Outputs:**
- Side-by-side comparison (cloud vs on-prem)
- Cost breakdown (pie chart)
- ROI analysis
- Breakeven point
- Sensitivity analysis

**UI Components:**
- Form with sliders and inputs
- Real-time calculation updates
- Interactive charts (Recharts)
- Export to PDF/CSV
- Save configuration (requires login)

### 2. Cost Per Token Calculator

**Purpose:** Calculate inference cost per million tokens

**Inputs:**
- Model size (7B, 13B, 70B, 175B, custom)
- GPU type
- Tokens per second (auto-calculated or manual)
- Batch size
- Utilization rate
- Total TCO (from TCO calculator or manual)

**Calculations:**
- Tokens per second per GPU
- Total tokens over lifetime
- Cost per token
- Cost per million tokens
- Comparison with OpenAI/Anthropic pricing

**Outputs:**
- Cost per 1M tokens
- Annual token capacity
- Pricing recommendations
- Competitive analysis

### 3. GPU Comparison Tool

**Purpose:** Side-by-side comparison of GPU accelerators

**Features:**
- Select 2-5 GPUs to compare
- Comparison table with key specs
- Radar charts for visual comparison
- Use case recommendations
- "Best for" tags (training, inference, cost-efficiency)

**Specs Compared:**
- Compute (TFLOPS FP16/FP8/INT8)
- Memory (capacity, bandwidth)
- Power consumption (TDP)
- Cost (MSRP, cloud $/hour)
- Efficiency (GFLOPS/W, GFLOPS/$)
- Interconnect (NVLink, PCIe)
- Launch date, availability

**GPU Database (50+ GPUs):**
- NVIDIA: H100, H200, A100, A10, L4, L40, T4
- AMD: MI300X, MI250X, MI210
- Google: TPU v4, TPU v5e, TPU v5p
- AWS: Trainium2, Inferentia2
- Intel: Gaudi2, Gaudi3 (upcoming)

### 4. Performance Estimator

**Purpose:** Estimate real-world performance for specific models

**Inputs:**
- Model architecture (Transformer, CNN, etc.)
- Model size (parameters)
- Batch size
- Sequence length
- GPU type
- Precision (FP32, FP16, INT8)

**Calculations:**
- FLOPs per forward pass
- Memory requirements
- Roofline analysis (compute vs memory bound)
- Expected MFU
- Tokens/second or samples/second
- Training time estimate

**Outputs:**
- Performance prediction
- Bottleneck identification
- Optimization suggestions
- Roofline chart visualization

### 5. Power & Cooling Calculator

**Purpose:** Datacenter power and cooling planning

**Inputs:**
- Number of racks
- GPUs per rack
- GPU type
- Cooling method (air, liquid)
- Electricity cost

**Calculations:**
- Total power consumption
- PUE (Power Usage Effectiveness)
- Cooling requirements
- Stranded power analysis
- Annual electricity cost
- Carbon footprint (CO2 tons)

**Outputs:**
- Power breakdown
- Cooling comparison (air vs liquid)
- Cost savings with liquid cooling
- Environmental impact

### 6. GPU Database & Search

**Purpose:** Searchable database of AI accelerators

**Features:**
- Search by name, vendor, specs
- Filter by use case, price range, power
- Detailed spec sheets
- Historical pricing data
- Availability tracker
- Community ratings/reviews

## User Flow

### First-time Visitor Journey

1. **Landing Page**
   - Hero: "Calculate AI Infrastructure Costs in Minutes"
   - Feature cards (6 calculators)
   - Sample calculation (H100 cluster)
   - "Try Calculator" CTA

2. **TCO Calculator (no signup required)**
   - Select GPU type
   - Input parameters (sliders, dropdowns)
   - See real-time results
   - View charts and breakdown
   - Export or save (requires signup)

3. **Signup Prompt**
   - "Save this calculation for later"
   - Email + password or Google/GitHub OAuth
   - Free tier: 10 saved calculations

4. **Dashboard (logged in)**
   - Saved calculations
   - Recent activity
   - Quick access to all calculators
   - Upgrade to Pro prompt

### Power User Journey

1. **Dashboard**
2. **Create Project** ("New AI Cluster 2026")
3. **Run multiple calculations:**
   - TCO for different GPU types
   - Cost per token for different models
   - Compare 5 GPU options
4. **Export full report** (PDF with all calculations)
5. **Share with team** (invite collaborators)

## Monetization Strategy

### Free Tier
- All calculators (unlimited usage)
- Up to 10 saved calculations
- Basic GPU database access
- Community support

### Pro Tier ($29/month or $290/year)
- Unlimited saved calculations
- Projects & organization
- Export to PDF/CSV with branding
- Historical data & trends
- Priority support
- API access (1000 calls/month)

### Enterprise Tier ($299/month, custom)
- Everything in Pro
- Team collaboration (unlimited seats)
- White-label embedding
- Custom GPU database entries (private specs)
- Unlimited API access
- Dedicated support
- Custom integrations

### Revenue Projections (Year 1)

**Conservative:**
- Free users: 10,000
- Pro users: 200 ($5,800/month)
- Enterprise: 5 ($1,495/month)
- Total MRR: $7,295
- Annual: ~$87,000

**Optimistic:**
- Free users: 50,000
- Pro users: 1,000 ($29,000/month)
- Enterprise: 20 ($5,980/month)
- Total MRR: $34,980
- Annual: ~$420,000

## Technical Architecture

### Frontend (Next.js 14)
```
chipsana.in/
├── Landing page (SEO optimized)
├── /calculators
│   ├── /tco
│   ├── /cost-per-token
│   ├── /compare
│   ├── /performance
│   └── /power-cooling
├── /database (GPU specs)
├── /dashboard (user dashboard)
├── /pricing
├── /docs (API documentation)
└── /blog (SEO content)
```

### Backend (FastAPI)
```
api.chipsana.in/
├── /api/v1
│   ├── /calculators
│   │   ├── /tco
│   │   ├── /cost-per-token
│   │   ├── /performance
│   │   └── /power-cooling
│   ├── /gpus (database)
│   ├── /users (auth)
│   ├── /projects
│   └── /exports
└── /docs (Swagger UI)
```

### Database Schema (PostgreSQL)

```sql
-- GPU Specifications
CREATE TABLE gpus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    vendor VARCHAR(50) NOT NULL,
    release_date DATE,
    architecture VARCHAR(50),
    
    -- Compute
    fp32_tflops DECIMAL(10,2),
    fp16_tflops DECIMAL(10,2),
    fp8_tflops DECIMAL(10,2),
    int8_tops DECIMAL(10,2),
    
    -- Memory
    memory_gb INTEGER,
    memory_bandwidth_gbs DECIMAL(10,2),
    memory_type VARCHAR(20),
    
    -- Power & Physical
    tdp_watts INTEGER,
    die_size_mm2 DECIMAL(10,2),
    transistors_billions DECIMAL(10,2),
    process_node VARCHAR(20),
    
    -- Economics
    msrp_usd DECIMAL(10,2),
    cloud_cost_per_hour DECIMAL(10,4),
    
    -- Interconnect
    nvlink_bandwidth_gbs DECIMAL(10,2),
    pcie_gen VARCHAR(10),
    
    -- Metadata
    availability VARCHAR(20), -- available, limited, pre-order, discontinued
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User accounts
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    plan VARCHAR(20) DEFAULT 'free', -- free, pro, enterprise
    created_at TIMESTAMP DEFAULT NOW()
);

-- Saved calculations
CREATE TABLE calculations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- tco, cost_per_token, etc.
    name VARCHAR(200),
    inputs JSONB NOT NULL, -- All calculator inputs
    outputs JSONB NOT NULL, -- All calculated results
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Projects (Pro/Enterprise)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Project calculations
CREATE TABLE project_calculations (
    project_id INTEGER REFERENCES projects(id),
    calculation_id INTEGER REFERENCES calculations(id),
    PRIMARY KEY (project_id, calculation_id)
);
```

## MVP Scope (4 weeks)

### Week 1: Foundation
- [x] Project setup (Next.js + FastAPI)
- [x] Database schema
- [ ] Seed GPU database (top 20 GPUs)
- [ ] Basic UI components (shadcn/ui)
- [ ] Landing page

### Week 2: Core Calculators
- [ ] TCO Calculator (frontend + backend)
- [ ] Cost Per Token Calculator
- [ ] Basic charts (Recharts)

### Week 3: Comparison & Database
- [ ] GPU Comparison Tool
- [ ] GPU Database page
- [ ] Search & filter

### Week 4: Polish & Launch
- [ ] User authentication (Clerk or NextAuth)
- [ ] Saved calculations
- [ ] Export to CSV
- [ ] SEO optimization
- [ ] Deploy to production

## Post-MVP Roadmap

### Phase 2 (Month 2-3)
- Performance Estimator
- Power & Cooling Calculator
- Projects feature (Pro tier)
- API access
- Blog with SEO content

### Phase 3 (Month 4-6)
- Advanced charts & visualizations
- Historical pricing data
- GPU availability tracker
- Community reviews
- Mobile responsive improvements

### Phase 4 (Month 7-12)
- Team collaboration features
- White-label embedding
- Integration with cloud providers (AWS, GCP, Azure)
- Custom API endpoints for Enterprise
- Mobile app (React Native)

## Success Metrics

### North Star Metric
**Monthly Active Users (MAU)** - Users who run at least one calculation

### Key Metrics

**Acquisition:**
- Website visitors
- Signup conversion rate (target: 5%)
- Organic search traffic

**Engagement:**
- Calculations per user (target: 3+)
- Time on site (target: 5+ minutes)
- Return visitors (target: 30%)

**Revenue:**
- Free to Pro conversion (target: 2%)
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)

**Retention:**
- Day 7 retention (target: 40%)
- Day 30 retention (target: 20%)
- Churn rate (target: <5% monthly)

## Marketing & Growth Strategy

### Content Marketing (Primary)
1. **Blog Posts (SEO)**
   - "H100 vs A100: Complete Comparison"
   - "True Cost of Training GPT-4 Scale Models"
   - "Cloud vs On-Premise: ROI Calculator"
   - Target: 50,000 monthly organic visitors (Year 1)

2. **Guides & Resources**
   - "GPU Buyer's Guide 2026"
   - "AI Infrastructure Planning Checklist"
   - "TCO Calculator Spreadsheet Templates"

### Community & Social
1. **Twitter/X (@chipsana_in)**
   - Daily GPU news & comparisons
   - Industry insights
   - User success stories

2. **LinkedIn**
   - Technical articles
   - Case studies
   - Target enterprise audience

3. **Reddit/HackerNews**
   - Share calculators on r/MachineLearning
   - Engage in infrastructure discussions
   - Post launch on HackerNews

### Partnerships
1. **GPU Vendors**
   - Official specs partnership
   - Featured tools

2. **Cloud Providers**
   - AWS, GCP, Azure integration
   - Co-marketing opportunities

3. **ML Frameworks**
   - Integration with cost tracking
   - Reference from documentation

## Competitive Analysis

### Competitors

1. **MLPerf Benchmarks**
   - Strength: Official, standardized benchmarks
   - Weakness: Complex, not user-friendly, no cost analysis
   - Differentiation: We add cost & TCO analysis

2. **Cloud Provider Calculators**
   - AWS, GCP, Azure pricing calculators
   - Strength: Official pricing
   - Weakness: Cloud-only, no on-prem comparison
   - Differentiation: Cloud vs on-prem, multi-vendor

3. **GPU Databases**
   - TechPowerUp GPU Database
   - Strength: Comprehensive specs
   - Weakness: Gaming focus, no AI-specific metrics
   - Differentiation: AI-focused, performance calculators

4. **Spreadsheet Templates**
   - DIY Excel/Google Sheets
   - Strength: Customizable
   - Weakness: Time-consuming, error-prone
   - Differentiation: Automated, validated formulas

### Competitive Advantages

1. **AI-Specific Focus** - Not gaming or general compute
2. **Cost + Performance** - Combined analysis, not separate
3. **Free & Accessible** - No enterprise sales required
4. **Real Formulas** - Based on actual research (SemiAnalysis style)
5. **Regular Updates** - GPU database updated weekly
6. **Community Driven** - User reviews and real-world data

## Risk Analysis

### Risks & Mitigation

**Risk 1: Inaccurate Calculations**
- Mitigation: Cite sources, allow user overrides, community verification
- Severity: High
- Probability: Medium

**Risk 2: GPU Vendor Pushback**
- Mitigation: Use public specifications only, neutral analysis
- Severity: Medium
- Probability: Low

**Risk 3: Low Adoption**
- Mitigation: Strong SEO, free tier, community building
- Severity: High
- Probability: Medium

**Risk 4: Competitors Copy**
- Mitigation: Move fast, build community, continuous innovation
- Severity: Medium
- Probability: High

**Risk 5: Data Becomes Outdated**
- Mitigation: Automated scraping, community contributions, API integrations
- Severity: Medium
- Probability: High

## Launch Plan

### Pre-Launch (2 weeks before)
- [ ] Finish MVP features
- [ ] Test with 10 beta users
- [ ] Prepare launch materials (video, screenshots)
- [ ] Write launch blog post
- [ ] Create social media assets
- [ ] Set up analytics (Google Analytics, Mixpanel)

### Launch Day
- [ ] Post on HackerNews (Show HN: Chipsana)
- [ ] Post on Reddit (r/MachineLearning, r/LocalLLaMA)
- [ ] Tweet launch announcement
- [ ] Email to beta users
- [ ] LinkedIn post
- [ ] ProductHunt submission

### Post-Launch (First Week)
- [ ] Monitor feedback & bugs
- [ ] Respond to comments
- [ ] Ship quick fixes
- [ ] Reach out to press (TechCrunch, VentureBeat)
- [ ] Guest post on ML blogs

### First Month
- [ ] Iterate based on user feedback
- [ ] Add most-requested features
- [ ] Publish 4 SEO blog posts
- [ ] Reach 1,000 MAU

## Conclusion

Chipsana addresses a real need in the AI infrastructure market: making hardware decisions easier and more transparent. With a focused MVP and clear growth strategy, we can build a valuable tool for the ML community and create a sustainable business.

**Next Steps:**
1. ✅ Create project structure
2. ⏳ Build MVP (4 weeks)
3. ⏳ Beta test with 10 users
4. ⏳ Launch publicly
5. ⏳ Iterate and grow

---

*Document Version: 1.0*
*Last Updated: August 22, 2026*
*Author: Chipsana Product Team*
