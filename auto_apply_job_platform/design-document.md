# AI Auto-Apply Job Platform - Design Document

**Document Date:** June 20, 2026  
**Tech Stack Status:** Latest & Greatest as of this date  
**Project Type:** AI-Powered Job Search Automation SaaS  
**Development Approach:** Test-Driven Development (TDD)  
**Production Status:** Enterprise-Ready, Multi-Tenant Architecture

---

## 📋 Executive Summary

An intelligent job application automation platform that leverages AI to scrape jobs, tailor resumes, and automatically apply to hundreds of positions daily. Targets tech professionals seeking remote work, eliminating 90%+ of manual job search effort.

**Core Problems Solved:**
1. ❌ **"Job searching takes 20+ hours/week"** → ✅ Automated to 30 minutes/week
2. ❌ **"Generic resumes get rejected"** → ✅ AI-tailored for each job
3. ❌ **"Manually tracking 100+ applications is chaos"** → ✅ Unified dashboard
4. ❌ **"Miss great opportunities"** → ✅ Real-time job alerts + auto-apply
5. ❌ **"Cover letters are time-consuming"** → ✅ AI-generated in seconds

---

## 🎯 Target Market

### **Primary Audience:**
- **Tech Professionals:** Software engineers, cloud architects, AI/ML engineers
- **Experience Level:** Mid-senior to senior (3-15 years)
- **Salary Range:** $100K-300K
- **Location:** Remote-first, global
- **Pain Point:** Too busy building to job hunt effectively

### **Market Size:**
- **TAM:** 30M tech professionals globally
- **SAM:** 5M actively job searching
- **SOM:** 100K early adopters (0.3% conversion)
- **Revenue Potential:** $100M+ ARR at scale

### **Competitive Landscape:**
| Competitor | Focus | Weakness | Our Advantage |
|------------|-------|----------|---------------|
| LazyApply | General jobs | No AI tailoring | GPT-5.5 resume customization |
| Sonara | Career coaching | Generic automation | Tech-specific, elite targeting |
| LinkedIn Easy Apply | Single platform | Manual process | Multi-platform automation |
| ZipRecruiter | Job board | No automation | Full application automation |

---

## 🚀 Latest & Greatest Tech Stack (June 2026)

### **Frontend**
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.x | Web framework, SSR |
| React | 19.2.7 | UI library |
| TypeScript | 5.5+ | Type safety |
| Tailwind CSS | 4.x | Styling |
| shadcn/ui | Latest | Component library |
| TanStack Query | 5.x | Data fetching |
| Zustand | 4.x | State management |
| Recharts | 2.x | Analytics charts |

### **Backend**
| Technology | Version | Purpose |
|------------|---------|---------|
| Golang | 1.22+ | API Gateway, job processing |
| Python | 3.12+ | AI services, web scraping |
| Fiber (Go) | 2.52+ | Web framework |
| FastAPI (Python) | 0.111+ | AI service APIs |
| PostgreSQL | 16.x | Main database |
| Redis | 7.x | Queue, caching |
| Asynq | Latest | Background jobs |

### **AI/ML Stack**
| Technology | Version | Purpose |
|------------|---------|---------|
| OpenAI GPT-5.5 | Latest | Resume tailoring, cover letters |
| Claude Opus 4.8 | Latest | Job matching, analysis |
| LangChain | 0.2.x | AI orchestration |
| Sentence Transformers | Latest | Job similarity search |
| pgvector | 0.7+ | Vector similarity |

### **Web Scraping & Automation**
| Technology | Version | Purpose |
|------------|---------|---------|
| Playwright | 1.45+ | Browser automation |
| Cheerio | Latest | HTML parsing |
| Puppeteer | 21.x | Headless Chrome |
| Selenium | 4.x | Fallback automation |

### **Authentication & Security**
| Technology | Version | Purpose |
|------------|---------|---------|
| Clerk | 5.x | User authentication |
| PASETO | v4 | Secure tokens |
| Argon2 | Latest | Password hashing |

### **Infrastructure**
| Technology | Version | Purpose |
|------------|---------|---------|
| Vercel | Latest | Frontend hosting |
| Railway | Latest | Backend hosting |
| Cloudflare | Latest | CDN, DDoS protection |
| Docker | 27.x | Containerization |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               User Dashboard (Next.js 16)                   │
│  Profile Setup | Job Preferences | Application Tracker     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API / GraphQL
                     │
┌────────────────────▼────────────────────────────────────────┐
│          API Gateway (Golang + Fiber)                       │
│  Auth | Rate Limiting | Request Routing | Logging          │
└────────┬─────────────┬──────────────┬───────────────────────┘
         │             │              │
         │ gRPC        │ gRPC         │ gRPC
         │             │              │
    ┌────▼────┐   ┌───▼──────┐   ┌──▼────────┐
    │  Job    │   │   AI     │   │  Apply    │
    │ Scraper │   │ Service  │   │  Engine   │
    │(Python) │   │(Python)  │   │(Golang)   │
    └────┬────┘   └───┬──────┘   └──┬────────┘
         │            │              │
         └────────────┼──────────────┘
                      │
         ┌────────────▼─────────────┐
         │   AI Models Layer        │
         │ GPT-5.5 | Claude 4.8    │
         └────────────┬─────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐   ┌───▼──────┐  ┌──▼───────┐
   │   DB    │   │  Vector  │  │  Redis   │
   │Postgres │   │pgvector  │  │  Queue   │
   └────┬────┘   └──────────┘  └──────────┘
        │
   ┌────▼────────────────────────────┐
   │   External Job Platforms        │
   │ LinkedIn | Indeed | AngelList  │
   │ Wellfound | Remote.co | etc.   │
   └─────────────────────────────────┘
```

---

## 📦 Core Features & Implementation

### **1. Multi-Platform Job Scraping**

**Platforms Supported:**
- LinkedIn (API + Scraping)
- Indeed
- AngelList (Wellfound)
- We Work Remotely
- Remote.co
- Stack Overflow Jobs
- GitHub Jobs
- Y Combinator Work at a Startup
- Hacker News Who's Hiring
- Custom job boards

**Tech Stack:**
- Playwright for JavaScript-heavy sites
- Cheerio for static HTML
- Rate limiting (respect robots.txt)
- Rotating proxies (prevent blocking)

**Implementation:**

```python
# job_scraper.py
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict

class JobScraper:
    """Multi-platform job scraper with anti-detection"""
    
    def __init__(self):
        self.platforms = {
            'linkedin': LinkedInScraper(),
            'indeed': IndeedScraper(),
            'angellist': AngelListScraper(),
            'weworkremotely': WeWorkRemotelyScraper()
        }
    
    async def scrape_all_platforms(
        self,
        keywords: List[str],
        location: str = "Remote",
        experience_level: str = "senior"
    ) -> List[Dict]:
        """Scrape jobs from all platforms concurrently"""
        
        tasks = []
        for platform_name, scraper in self.platforms.items():
            task = scraper.scrape(keywords, location, experience_level)
            tasks.append(task)
        
        # Run all scrapers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten and deduplicate
        all_jobs = []
        seen_urls = set()
        
        for platform_jobs in results:
            if isinstance(platform_jobs, Exception):
                continue
            
            for job in platform_jobs:
                if job['apply_url'] not in seen_urls:
                    all_jobs.append(job)
                    seen_urls.add(job['apply_url'])
        
        return all_jobs

class LinkedInScraper:
    """LinkedIn job scraper with anti-detection"""
    
    async def scrape(self, keywords: List[str], location: str, level: str) -> List[Dict]:
        async with async_playwright() as p:
            # Launch browser with stealth mode
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # Add stealth scripts
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)
            
            jobs = []
            
            for keyword in keywords:
                # Build search URL
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}&f_E={level}&f_WT=2"
                
                await page.goto(search_url, wait_until='networkidle')
                
                # Wait for job cards
                await page.wait_for_selector('.job-card-container')
                
                # Extract job listings
                job_cards = await page.query_selector_all('.job-card-container')
                
                for card in job_cards:
                    try:
                        title = await card.query_selector('.job-card-list__title')
                        company = await card.query_selector('.job-card-container__company-name')
                        location_el = await card.query_selector('.job-card-container__metadata-item')
                        link = await card.query_selector('a')
                        
                        job = {
                            'title': await title.inner_text() if title else None,
                            'company': await company.inner_text() if company else None,
                            'location': await location_el.inner_text() if location_el else None,
                            'apply_url': await link.get_attribute('href') if link else None,
                            'platform': 'linkedin',
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting job: {e}")
                        continue
                
                # Random delay to avoid detection
                await asyncio.sleep(random.uniform(2, 5))
            
            await browser.close()
            return jobs
```

---


### **2. AI-Powered Resume Tailoring**

**Features:**
- Analyze job description → Extract keywords
- Match user's experience to job requirements
- Rewrite resume bullets to emphasize relevant skills
- Maintain truthfulness (no fake experience)
- Generate ATS-optimized PDFs

**Implementation:**

```python
# resume_tailor.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import logfire

class ResumeTailor:
    """AI-powered resume tailoring for each job"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5.5", temperature=0.3)
        logfire.configure()
    
    async def tailor_resume(
        self,
        base_resume: Dict,
        job_description: str,
        job_title: str,
        company: str
    ) -> Dict:
        """Tailor resume for specific job"""
        
        with logfire.span("resume_tailoring", job_title=job_title, company=company):
            # Extract job requirements
            requirements = await self.extract_requirements(job_description)
            
            # Match user skills to requirements
            skill_matches = self.match_skills(base_resume['skills'], requirements)
            
            # Rewrite experience bullets
            tailored_experience = await self.rewrite_experience(
                base_resume['experience'],
                requirements,
                skill_matches
            )
            
            # Optimize summary
            tailored_summary = await self.optimize_summary(
                base_resume['summary'],
                job_title,
                requirements
            )
            
            return {
                **base_resume,
                'summary': tailored_summary,
                'experience': tailored_experience,
                'skills': self.reorder_skills(base_resume['skills'], skill_matches),
                'tailored_for': {
                    'job_title': job_title,
                    'company': company,
                    'match_score': skill_matches['overall_score']
                }
            }
    
    async def extract_requirements(self, job_description: str) -> Dict:
        """Extract key requirements from job description"""
        
        prompt = ChatPromptTemplate.from_template("""
        Analyze this job description and extract:
        1. Required technical skills
        2. Preferred technologies
        3. Experience level
        4. Key responsibilities
        5. Nice-to-have skills
        
        Job Description:
        {job_description}
        
        Return as JSON with arrays for each category.
        """)
        
        chain = prompt | self.llm
        result = await chain.ainvoke({"job_description": job_description})
        
        return json.loads(result.content)
    
    async def rewrite_experience(
        self,
        experience: List[Dict],
        requirements: Dict,
        skill_matches: Dict
    ) -> List[Dict]:
        """Rewrite experience bullets to emphasize relevant skills"""
        
        tailored_experience = []
        
        for job in experience:
            prompt = ChatPromptTemplate.from_template("""
            Rewrite these job responsibilities to emphasize skills relevant to:
            Required Skills: {required_skills}
            Preferred Tech: {preferred_tech}
            
            Original responsibilities:
            {original_bullets}
            
            Rules:
            1. Keep all facts accurate (no fabrication)
            2. Emphasize relevant technologies
            3. Quantify achievements where possible
            4. Use strong action verbs
            5. Make it ATS-friendly
            
            Return rewritten bullets as JSON array.
            """)
            
            chain = prompt | self.llm
            result = await chain.ainvoke({
                "required_skills": ", ".join(requirements['required_skills']),
                "preferred_tech": ", ".join(requirements['preferred_technologies']),
                "original_bullets": "\n".join(job['responsibilities'])
            })
            
            tailored_job = {
                **job,
                'responsibilities': json.loads(result.content)
            }
            
            tailored_experience.append(tailored_job)
        
        return tailored_experience
```

---

### **3. Intelligent Job Matching**

**Matching Algorithm:**
- Vector similarity (job description vs user profile)
- Keyword matching (required skills)
- Salary range filtering
- Experience level matching
- Location preferences
- Company culture fit

**Implementation:**

```python
# job_matcher.py
from sentence_transformers import SentenceTransformer
import numpy as np

class JobMatcher:
    """Intelligent job matching using embeddings"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def match_jobs(
        self,
        user_profile: Dict,
        jobs: List[Dict],
        min_score: float = 0.7
    ) -> List[Dict]:
        """Match jobs to user profile"""
        
        # Generate user profile embedding
        user_text = self.create_profile_text(user_profile)
        user_embedding = self.model.encode(user_text)
        
        # Score each job
        matched_jobs = []
        
        for job in jobs:
            # Calculate similarity score
            job_text = f"{job['title']} {job['description']} {job['requirements']}"
            job_embedding = self.model.encode(job_text)
            
            similarity = np.dot(user_embedding, job_embedding) / (
                np.linalg.norm(user_embedding) * np.linalg.norm(job_embedding)
            )
            
            # Additional scoring factors
            keyword_score = self.keyword_match(user_profile, job)
            salary_score = self.salary_match(user_profile, job)
            level_score = self.experience_match(user_profile, job)
            
            # Weighted final score
            final_score = (
                similarity * 0.5 +
                keyword_score * 0.3 +
                salary_score * 0.1 +
                level_score * 0.1
            )
            
            if final_score >= min_score:
                matched_jobs.append({
                    **job,
                    'match_score': final_score,
                    'match_details': {
                        'similarity': similarity,
                        'keywords': keyword_score,
                        'salary': salary_score,
                        'level': level_score
                    }
                })
        
        # Sort by score descending
        matched_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matched_jobs
```

---

### **4. Automated Application Submission**

**Features:**
- Detect application system (Greenhouse, Lever, Workday, etc.)
- Auto-fill forms with user data
- Upload tailored resume
- Submit cover letter
- Handle CAPTCHAs (when possible)
- Track submission status

**Implementation:**

```go
// application_engine.go
package main

import (
    "context"
    "fmt"
    "github.com/playwright-community/playwright-go"
)

type ApplicationEngine struct {
    browser playwright.Browser
}

func NewApplicationEngine() (*ApplicationEngine, error) {
    pw, err := playwright.Run()
    if err != nil {
        return nil, err
    }
    
    browser, err := pw.Chromium.Launch(playwright.BrowserTypeLaunchOptions{
        Headless: playwright.Bool(true),
    })
    
    return &ApplicationEngine{browser: browser}, nil
}

func (ae *ApplicationEngine) ApplyToJob(
    ctx context.Context,
    job Job,
    tailoredResume Resume,
    coverLetter string,
) (ApplicationResult, error) {
    // Detect application system
    systemType := ae.DetectApplicationSystem(job.ApplyURL)
    
    switch systemType {
    case "greenhouse":
        return ae.ApplyGreenhouse(ctx, job, tailoredResume, coverLetter)
    case "lever":
        return ae.ApplyLever(ctx, job, tailoredResume, coverLetter)
    case "workday":
        return ae.ApplyWorkday(ctx, job, tailoredResume, coverLetter)
    default:
        return ae.ApplyGeneric(ctx, job, tailoredResume, coverLetter)
    }
}

func (ae *ApplicationEngine) ApplyGreenhouse(
    ctx context.Context,
    job Job,
    resume Resume,
    coverLetter string,
) (ApplicationResult, error) {
    page, err := ae.browser.NewPage()
    if err != nil {
        return ApplicationResult{}, err
    }
    defer page.Close()
    
    // Navigate to application page
    if _, err := page.Goto(job.ApplyURL); err != nil {
        return ApplicationResult{}, err
    }
    
    // Fill first name
    if err := page.Locator("input[name='first_name']").Fill(resume.FirstName); err != nil {
        return ApplicationResult{}, err
    }
    
    // Fill last name
    if err := page.Locator("input[name='last_name']").Fill(resume.LastName); err != nil {
        return ApplicationResult{}, err
    }
    
    // Fill email
    if err := page.Locator("input[name='email']").Fill(resume.Email); err != nil {
        return ApplicationResult{}, err
    }
    
    // Fill phone
    if err := page.Locator("input[name='phone']").Fill(resume.Phone); err != nil {
        return ApplicationResult{}, err
    }
    
    // Upload resume
    resumePath := fmt.Sprintf("/tmp/resumes/%s.pdf", resume.ID)
    if err := page.Locator("input[type='file']").SetInputFiles(resumePath); err != nil {
        return ApplicationResult{}, err
    }
    
    // Fill cover letter
    if coverLetter != "" {
        if err := page.Locator("textarea[name='cover_letter']").Fill(coverLetter); err != nil {
            // Cover letter might be optional
            fmt.Println("Warning: Could not fill cover letter")
        }
    }
    
    // Submit application
    if err := page.Locator("button[type='submit']").Click(); err != nil {
        return ApplicationResult{}, err
    }
    
    // Wait for confirmation
    if err := page.WaitForSelector(".confirmation-message", playwright.PageWaitForSelectorOptions{
        Timeout: playwright.Float(10000),
    }); err != nil {
        return ApplicationResult{}, err
    }
    
    return ApplicationResult{
        Status:      "submitted",
        JobID:       job.ID,
        SubmittedAt: time.Now(),
        Message:     "Application submitted successfully via Greenhouse",
    }, nil
}
```

---

### **5. Application Tracking Dashboard**

**Features:**
- View all applications in one place
- Filter by status (submitted, interviewing, rejected, offer)
- Track response rates
- Analytics (applications per week, response rate, etc.)
- Interview scheduler integration
- Notes & follow-ups

**Implementation:**

```typescript
// ApplicationDashboard.tsx
'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface Application {
  id: string;
  job_title: string;
  company: string;
  status: 'submitted' | 'viewed' | 'interviewing' | 'rejected' | 'offer';
  applied_at: string;
  match_score: number;
  salary_range: string;
}

export const ApplicationDashboard = () => {
  const { data: applications, isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: fetchApplications,
  });
  
  const [filter, setFilter] = useState<string>('all');
  
  // Calculate statistics
  const stats = applications ? {
    total: applications.length,
    submitted: applications.filter(a => a.status === 'submitted').length,
    interviewing: applications.filter(a => a.status === 'interviewing').length,
    offers: applications.filter(a => a.status === 'offer').length,
    responseRate: (applications.filter(a => a.status !== 'submitted').length / applications.length * 100).toFixed(1),
  } : null;
  
  const filteredApplications = applications?.filter(app => {
    if (filter === 'all') return true;
    return app.status === filter;
  });
  
  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Total</h3>
          <p className="text-3xl font-bold">{stats?.total}</p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Submitted</h3>
          <p className="text-3xl font-bold text-blue-600">{stats?.submitted}</p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Interviewing</h3>
          <p className="text-3xl font-bold text-yellow-600">{stats?.interviewing}</p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Offers</h3>
          <p className="text-3xl font-bold text-green-600">{stats?.offers}</p>
        </Card>
        
        <Card className="p-4">
          <h3 className="text-sm font-medium text-gray-500">Response Rate</h3>
          <p className="text-3xl font-bold">{stats?.responseRate}%</p>
        </Card>
      </div>
      
      {/* Filter Tabs */}
      <div className="flex gap-2">
        {['all', 'submitted', 'interviewing', 'rejected', 'offer'].map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg ${
              filter === status ? 'bg-blue-500 text-white' : 'bg-gray-100'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>
      
      {/* Applications Table */}
      <Card className="p-6">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Job Title</th>
              <th className="text-left p-2">Company</th>
              <th className="text-left p-2">Status</th>
              <th className="text-left p-2">Match Score</th>
              <th className="text-left p-2">Salary</th>
              <th className="text-left p-2">Applied</th>
              <th className="text-left p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredApplications?.map(app => (
              <tr key={app.id} className="border-b hover:bg-gray-50">
                <td className="p-2 font-medium">{app.job_title}</td>
                <td className="p-2">{app.company}</td>
                <td className="p-2">
                  <Badge variant={getStatusVariant(app.status)}>
                    {app.status}
                  </Badge>
                </td>
                <td className="p-2">
                  <div className="flex items-center gap-2">
                    <Progress value={app.match_score * 100} className="w-20" />
                    <span>{(app.match_score * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="p-2">{app.salary_range}</td>
                <td className="p-2">{formatDate(app.applied_at)}</td>
                <td className="p-2">
                  <button className="text-blue-500 hover:underline">
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      
      {/* Analytics Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Applications Over Time</h3>
          <ApplicationsChart data={applications} />
        </Card>
        
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Response Rate by Company</h3>
          <ResponseRateChart data={applications} />
        </Card>
      </div>
    </div>
  );
};
```

---


## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    subscription_plan VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    credits_remaining INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User profiles (resume data)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Basic info
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    
    -- Resume data
    summary TEXT,
    skills JSONB,
    experience JSONB,
    education JSONB,
    certifications JSONB,
    
    -- Base resume file
    resume_file_url VARCHAR(500),
    
    -- Job preferences
    desired_titles TEXT[],
    desired_salary_min INT,
    desired_salary_max INT,
    desired_locations TEXT[],
    remote_only BOOLEAN DEFAULT TRUE,
    
    -- Search embeddings
    profile_embedding vector(384),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Jobs scraped from various platforms
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Job details
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    salary_min INT,
    salary_max INT,
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    
    -- Application details
    apply_url VARCHAR(1000) NOT NULL,
    platform VARCHAR(100), -- linkedin, indeed, etc.
    application_system VARCHAR(100), -- greenhouse, lever, etc.
    
    -- Metadata
    posted_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_remote BOOLEAN DEFAULT FALSE,
    experience_level VARCHAR(50), -- junior, mid, senior, staff, principal
    employment_type VARCHAR(50), -- full-time, part-time, contract
    
    -- Search optimization
    job_embedding vector(384),
    keywords TEXT[],
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(apply_url)
);

-- Applications submitted
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id),
    
    -- Application details
    status VARCHAR(50) DEFAULT 'submitted', -- submitted, viewed, interviewing, rejected, offer
    tailored_resume_url VARCHAR(500),
    cover_letter TEXT,
    
    -- Matching
    match_score FLOAT,
    match_details JSONB,
    
    -- Timeline
    submitted_at TIMESTAMP DEFAULT NOW(),
    viewed_at TIMESTAMP,
    responded_at TIMESTAMP,
    interview_scheduled_at TIMESTAMP,
    
    -- Communication
    notes TEXT,
    follow_up_date DATE,
    
    -- Tracking
    application_source VARCHAR(100), -- auto, manual
    submission_method VARCHAR(100), -- playwright, api, email
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tailored resumes (cached)
CREATE TABLE tailored_resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id),
    
    -- Resume content
    resume_data JSONB NOT NULL,
    pdf_url VARCHAR(500),
    
    -- Tailoring details
    tailored_for_title VARCHAR(500),
    tailored_for_company VARCHAR(255),
    keywords_emphasized TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cover letters (cached)
CREATE TABLE cover_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id),
    
    content TEXT NOT NULL,
    template_used VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Job alerts & notifications
CREATE TABLE job_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Alert criteria
    keywords TEXT[],
    locations TEXT[],
    salary_min INT,
    remote_only BOOLEAN DEFAULT TRUE,
    experience_levels TEXT[],
    platforms TEXT[],
    
    -- Notification settings
    notification_method VARCHAR(50), -- email, sms, push
    frequency VARCHAR(50), -- instant, daily, weekly
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subscription plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    price_monthly INT NOT NULL,
    price_yearly INT NOT NULL,
    
    -- Limits
    applications_per_month INT,
    job_alerts INT,
    resume_tailoring BOOLEAN DEFAULT FALSE,
    cover_letter_generation BOOLEAN DEFAULT FALSE,
    priority_support BOOLEAN DEFAULT FALSE,
    
    -- Features
    features JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics & metrics
CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Application metrics
    total_applications INT DEFAULT 0,
    applications_this_week INT DEFAULT 0,
    applications_this_month INT DEFAULT 0,
    
    -- Response metrics
    responses_received INT DEFAULT 0,
    interviews_scheduled INT DEFAULT 0,
    offers_received INT DEFAULT 0,
    
    -- Performance
    average_match_score FLOAT,
    response_rate FLOAT,
    
    -- Last updated
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_jobs_platform ON jobs(platform);
CREATE INDEX idx_jobs_active ON jobs(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_jobs_posted ON jobs(posted_at DESC);
CREATE INDEX idx_jobs_embedding ON jobs USING ivfflat (job_embedding vector_cosine_ops);

CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_submitted ON applications(submitted_at DESC);

CREATE INDEX idx_user_profiles_embedding ON user_profiles USING ivfflat (profile_embedding vector_cosine_ops);
```

---

## 💰 Pricing Model

### **Tiered Subscription Plans:**

| Feature | Free | Pro | Elite | Enterprise |
|---------|------|-----|-------|------------|
| **Price** | $0 | $29/mo | $79/mo | $199/mo |
| **Applications/Month** | 10 | 100 | Unlimited | Unlimited |
| **Job Platforms** | 3 | All (10+) | All (10+) | All (10+) |
| **Resume Tailoring** | ❌ | ✅ | ✅ | ✅ |
| **Cover Letters** | ❌ | ✅ | ✅ | ✅ |
| **Job Alerts** | 1 | 5 | Unlimited | Unlimited |
| **Interview Prep** | ❌ | ❌ | ✅ | ✅ |
| **Priority Support** | ❌ | ❌ | ✅ | ✅ |
| **Team Accounts** | ❌ | ❌ | ❌ | ✅ |
| **Custom Integrations** | ❌ | ❌ | ❌ | ✅ |

### **Add-ons:**
- **Extra Applications:** $10 per 50 applications
- **Resume Review:** $49 one-time (human expert)
- **Interview Coaching:** $99 per session

---

## 📊 Revenue Projections

### **Conservative Scenario:**

| Month | Free Users | Pro Users | Elite Users | Enterprise | MRR |
|-------|------------|-----------|-------------|------------|-----|
| 1 | 100 | 5 | 1 | 0 | $224 |
| 3 | 500 | 30 | 5 | 1 | $1,464 |
| 6 | 2,000 | 150 | 20 | 5 | $7,530 |
| 12 | 10,000 | 500 | 100 | 20 | $36,480 |

**Year 1 ARR:** ~$437K

### **Optimistic Scenario:**

| Month | Free Users | Pro Users | Elite Users | Enterprise | MRR |
|-------|------------|-----------|-------------|------------|-----|
| 1 | 500 | 20 | 5 | 0 | $975 |
| 3 | 2,000 | 100 | 20 | 3 | $5,177 |
| 6 | 10,000 | 500 | 100 | 15 | $27,385 |
| 12 | 50,000 | 2,000 | 500 | 50 | $117,450 |

**Year 1 ARR:** ~$1.4M

---

## 🔐 Security & Compliance

### **Data Protection:**
- **Encryption at rest:** AES-256 for all user data
- **Encryption in transit:** TLS 1.3 for all connections
- **Resume storage:** Encrypted S3 buckets
- **PII handling:** GDPR & CCPA compliant

### **Authentication:**
- PASETO v4 tokens (not JWT)
- Clerk for user authentication
- MFA support (TOTP)
- Session management

### **Rate Limiting:**
- API: 100 requests/minute per user
- Scraping: Respect robots.txt
- Job applications: Max 50/day (prevent abuse)

### **Privacy:**
- Users control data sharing
- Resume data never sold
- Option to delete all data (GDPR right to erasure)
- Transparent data usage policy

---

## 🚀 MVP Feature Set (4-Week Build)

### **Week 1: Core Infrastructure**
- [ ] User authentication (Clerk)
- [ ] Database setup (PostgreSQL + pgvector)
- [ ] Basic UI (Next.js 16)
- [ ] API gateway (Golang + Fiber)

### **Week 2: Job Scraping**
- [ ] LinkedIn scraper
- [ ] Indeed scraper
- [ ] Job storage & deduplication
- [ ] Basic job search

### **Week 3: Resume Tailoring**
- [ ] User profile setup
- [ ] GPT-5.5 integration
- [ ] Resume tailoring logic
- [ ] PDF generation

### **Week 4: Auto-Apply**
- [ ] Greenhouse integration
- [ ] Lever integration
- [ ] Application tracking
- [ ] Dashboard UI

**MVP Launch:** 200+ jobs/day, 2 platforms, basic automation

---

## 📈 Growth Strategy

### **Month 1-3: Beta Launch**
- Launch on Product Hunt
- Share on Reddit (r/cscareerquestions, r/jobs)
- Post on Hacker News
- LinkedIn outreach
- **Goal:** 1,000 users, $5K MRR

### **Month 4-6: Content Marketing**
- Blog: "How I applied to 1,000 jobs in 1 month"
- YouTube tutorials
- Twitter thread about automation
- SEO optimization
- **Goal:** 5,000 users, $25K MRR

### **Month 7-12: Scale**
- Paid ads (Google, LinkedIn)
- Influencer partnerships
- Referral program (give $10, get $10)
- Enterprise sales
- **Goal:** 20,000 users, $100K MRR

---

## 🎯 Success Metrics

### **User Engagement:**
- Daily Active Users (DAU)
- Applications per user per week
- Average session duration
- Feature adoption rate

### **Business Metrics:**
- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Lifetime Value (LTV)
- Churn rate
- **Target:** LTV:CAC ratio > 3:1

### **Product Metrics:**
- Job match accuracy (>80%)
- Application success rate (>20% response rate)
- Resume tailoring quality (user feedback >4/5)
- Platform uptime (>99.9%)

---

## 🛠️ Tech Stack Summary

**Frontend:** Next.js 16 + React 19.2.7 + TypeScript + Tailwind  
**Backend:** Golang (API) + Python (AI/Scraping)  
**Database:** PostgreSQL 16 + pgvector + Redis  
**AI:** GPT-5.5 + Claude Opus 4.8 + LangChain  
**Automation:** Playwright + Puppeteer  
**Auth:** Clerk + PASETO  
**Hosting:** Vercel (frontend) + Railway (backend)  
**Payments:** Stripe

---

## 🚧 Future Features (Post-MVP)

### **Phase 2 (Month 4-6):**
- [ ] Interview prep AI coach
- [ ] Salary negotiation assistant
- [ ] Company research automation
- [ ] Email follow-up automation
- [ ] Chrome extension

### **Phase 3 (Month 7-12):**
- [ ] Mobile app (React Native)
- [ ] Team accounts (for bootcamps)
- [ ] White-label for recruiters
- [ ] API for third-party integrations
- [ ] International expansion

---

## 📚 Your Advantage Building This

### **Why YOU Can Build This 3x Faster:**

1. ✅ **Golang Expert** → Backend done in days, not weeks
2. ✅ **AI/ML Expert** → Resume tailoring is your specialty
3. ✅ **Cloud Architect** → Scalable from day 1
4. ✅ **Security Expert** → Compliant & secure from start
5. ✅ **Have Design Docs** → Architecture already mapped

**Normal Dev:** 12 weeks to MVP  
**You:** 4 weeks to MVP (3x faster!)

---

## 💡 Competitive Advantages

### **vs LazyApply:**
- ✅ Better AI (GPT-5.5 vs generic)
- ✅ Tech-focused (they're general)
- ✅ More platforms (10+ vs 5)
- ✅ Elite targeting ($150K+ jobs)

### **vs Sonara:**
- ✅ Faster automation (100+ apps/day vs 50)
- ✅ Better resume tailoring
- ✅ Lower price ($29 vs $79)
- ✅ More transparent (no black box)

### **vs Manual Job Search:**
- ✅ 20x faster (20 hours → 1 hour/week)
- ✅ Better targeting (AI matching)
- ✅ No application fatigue
- ✅ Analytics & insights

---

## 🎯 Your Next Steps

### **This Week (20 hours):**
1. **Day 1-2:** Setup infrastructure (8h)
2. **Day 3-4:** Build job scraper (8h)
3. **Day 5:** Test scraping LinkedIn (4h)

### **Week 2 (20 hours):**
1. **Day 1-2:** Resume tailoring with GPT-5.5 (8h)
2. **Day 3-4:** Auto-apply engine (8h)
3. **Day 5:** Dashboard UI (4h)

### **Week 3 (20 hours):**
1. **Day 1-2:** User authentication (8h)
2. **Day 3-4:** Stripe integration (8h)
3. **Day 5:** Testing & bug fixes (4h)

### **Week 4 (20 hours):**
1. **Day 1-2:** Polish UI (8h)
2. **Day 3:** Deploy to production (4h)
3. **Day 4:** Launch on Product Hunt (4h)
4. **Day 5:** Marketing push (4h)

**Total: 80 hours = 4 weeks @ 20 hours/week**

---

## 💰 Revenue Potential Summary

**Month 3:** $5K MRR  
**Month 6:** $25K MRR  
**Month 12:** $100K MRR  
**Year 2:** $500K+ MRR

**Exit Opportunity:** $10M-50M valuation (10-50x MRR)

---

**Status:** ✅ Complete Design Document  
**Version:** 1.0  
**Date:** June 20, 2026  
**Next:** Build MVP in 4 weeks! 🚀
