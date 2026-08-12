# LLM Evaluation Dashboard

A production-ready Next.js dashboard for monitoring and managing LLM evaluation at scale.

## 🚀 Features

### 📊 Dashboard Overview
- Real-time statistics (total jobs, active jobs, costs, success rate)
- Interactive charts for job activity and cost breakdown
- Model performance comparison visualizations
- Recent jobs list with quick navigation

### 💼 Job Management
- Create evaluation jobs with multiple models
- Monitor job progress in real-time
- Filter and search jobs by status
- Detailed job views with task tracking
- Export job results (JSON/CSV/PDF)

### 💬 Analytics Chat
- Natural language queries powered by Gemini AI
- Ask questions about model performance, costs, deployment readiness
- Get insights with contextual data visualization
- Suggested queries for quick insights

### 🎯 Deployment Readiness
- 4-pillar assessment (Performance, Business, Safety, Operational)
- Visual deployment checklist with pass/fail indicators
- Critical issues and warnings highlighting
- Actionable recommendations

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Date Formatting**: date-fns

## 📦 Installation

```bash
# Install dependencies
npm install

# or with yarn
yarn install
```

## 🔧 Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_ANALYTICS_URL=http://localhost:8003/api/v1
```

## 🚀 Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The dashboard will be available at `http://localhost:3001`

## 📁 Project Structure

```
dashboard/
├── app/                      # Next.js App Router pages
│   ├── page.tsx             # Dashboard overview
│   ├── jobs/
│   │   ├── page.tsx         # Jobs list
│   │   └── [id]/page.tsx    # Job details
│   ├── chat/page.tsx        # Analytics chat
│   ├── deployment/page.tsx  # Deployment readiness
│   ├── layout.tsx           # Root layout
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── ui/                  # Base UI components
│   │   ├── Card.tsx
│   │   ├── Button.tsx
│   │   └── Badge.tsx
│   ├── charts/              # Chart components
│   │   ├── JobsChart.tsx
│   │   ├── CostChart.tsx
│   │   └── ModelPerformanceChart.tsx
│   ├── modals/              # Modal dialogs
│   │   └── CreateJobModal.tsx
│   ├── Navigation.tsx       # Top navigation
│   ├── StatsCard.tsx        # Stat display card
│   ├── JobsTable.tsx        # Jobs table
│   ├── TasksTable.tsx       # Tasks table
│   ├── ChatMessage.tsx      # Chat message bubble
│   ├── DeploymentScoreCard.tsx
│   ├── DeploymentChecklist.tsx
│   └── MetricsDisplay.tsx
├── lib/
│   └── api.ts               # API client
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🔌 API Integration

The dashboard connects to two backend services:

### API Gateway (Port 8000)
- User authentication
- Job creation and management
- Task and result retrieval

### Analytics Service (Port 8003)
- Dashboard statistics
- Model comparison analytics
- Cost breakdown
- Deployment readiness assessment
- Natural language chat queries

## 📖 Usage Guide

### Creating an Evaluation Job

1. Navigate to **Jobs** page
2. Click **Create Job** button
3. Fill in job details:
   - Job name
   - Select models to evaluate (Gemini, GPT, Claude)
   - Add prompts (can add multiple)
   - Set priority level
4. Click **Create Job**
5. Monitor progress in real-time

### Monitoring Job Progress

1. Go to **Jobs** page
2. Click on any job to view details
3. See:
   - Overall progress percentage
   - Task completion status
   - Cost breakdown
   - Evaluation metrics
   - Individual task results

### Using Analytics Chat

1. Navigate to **Analytics Chat** page
2. Type your question or use suggested queries:
   - "What's the best performing model?"
   - "Which model is most cost-effective?"
   - "Show deployment readiness"
   - "Show results from the last 5 jobs"
3. Get AI-powered insights with relevant data

### Checking Deployment Readiness

1. Go to **Deployment** page
2. Select a model to assess
3. Review the 4 pillars:
   - **Performance** (25%): BERTScore, latency, throughput
   - **Business** (25%): Cost, ROI, user satisfaction
   - **Safety** (35%): Hallucination, toxicity, bias, PII
   - **Operational** (15%): Monitoring, docs, rollback plan
4. Check deployment status: APPROVED / CONDITIONAL / REJECTED
5. Review critical issues and recommendations

## 🎨 Customization

### Styling

The dashboard uses Tailwind CSS. Customize colors and styles in:
- `tailwind.config.ts` - Theme configuration
- `app/globals.css` - Global styles

### API Endpoints

Update API base URLs in:
- `.env.local` - Local development
- Environment variables in Docker/K8s for production

### Charts

Customize chart appearance in:
- `components/charts/*.tsx`
- Recharts documentation: https://recharts.org

## 🐳 Docker Deployment

The dashboard is included in the main `docker-compose.yml`:

```yaml
dashboard:
  build: ./services/dashboard
  ports:
    - "3001:3001"
  environment:
    - NEXT_PUBLIC_API_URL=http://api-gateway:8000/api/v1
    - NEXT_PUBLIC_ANALYTICS_URL=http://analytics:8003/api/v1
```

Start with Docker:
```bash
docker-compose up dashboard
```

## 🔐 Authentication

The dashboard uses JWT token authentication:

1. User registers/logs in via API Gateway
2. Token stored in localStorage
3. Token included in all API requests
4. Auto-redirect to login if token expires

## 📊 Real-time Updates

- Dashboard stats refresh every 10 seconds
- Job list refreshes every 5 seconds
- Job details refresh every 3 seconds (while running)
- WebSocket support planned for future versions

## 🚨 Error Handling

- Network errors show user-friendly messages
- Failed API calls include retry logic
- Toast notifications for important events
- Graceful degradation for missing data

## 🧪 Testing

```bash
# Run linter
npm run lint

# Type checking
npm run type-check
```

## 📝 License

Part of the LLM Evaluation at Scale system.

## 🤝 Contributing

1. Follow TypeScript and React best practices
2. Use Tailwind CSS for styling
3. Keep components small and focused
4. Add proper TypeScript types
5. Test in both light and dark modes

## 📞 Support

For issues and questions:
- Check the main project README
- Review API documentation at `/docs`
- Check logs in browser console

## 🎯 Future Enhancements

- [ ] WebSocket for true real-time updates
- [ ] Dark mode toggle
- [ ] Advanced filtering and sorting
- [ ] Customizable dashboards
- [ ] User preferences persistence
- [ ] Multi-language support
- [ ] Accessibility improvements
- [ ] Mobile-responsive optimizations
- [ ] Advanced chart interactions
- [ ] Notification system

---

**Dashboard Version**: 1.0.0  
**Last Updated**: Current Session  
**Status**: Production Ready ✅
