# 🚀 Quick Start Guide

Get the LLM Evaluation System running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- API Keys (at least one):
  - **Groq API key** (Recommended! Free tier available) 🆓
  - Google Gemini API key (optional)
  - OpenAI API key (optional)
  - Anthropic API key (optional)

💡 **Tip**: Get a free Groq API key at https://console.groq.com/keys for 10-20x faster, 95% cheaper evaluations!

## Step 1: Clone & Configure

```bash
# Navigate to project
cd evaluate_LLMs_at_scale

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Recommended (Free!):
GROQ_API_KEY=your_groq_key_here

# Optional (for multi-model comparison):
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

💡 **Get a free Groq API key**: Visit https://console.groq.com/keys (no credit card required!)

## Step 2: Start All Services

```bash
# Start everything with Docker Compose
make up

# Or manually:
docker-compose up -d

# Wait 30 seconds for initialization
```

## Step 3: Access the Dashboard

Open your browser and navigate to:
```
http://localhost:3001
```

## Step 4: Register & Login

1. Click **Register** (or use the API)
2. Create account with email/password
3. Login to get your auth token
4. Dashboard will load automatically

## Step 5: Create Your First Evaluation Job

### Via Dashboard UI:
1. Click **Create Job** button
2. Fill in:
   - Job name: "My First Evaluation"
   - Models: Check "Llama 3.1 70B (Groq)" ⚡ (Recommended!)
   - Prompts: Add "What is artificial intelligence?"
   - Priority: Medium
3. Click **Create Job**
4. Watch blazing fast results! ⚡

💡 **Why Groq?** 10-20x faster and 95% cheaper than GPT-4!

### Via API (cURL):
```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'

# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }' | jq -r '.access_token')

# Create evaluation job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "My First Evaluation",
    "models": ["gemini-pro"],
    "prompts": [
      "What is artificial intelligence?",
      "Explain machine learning in simple terms"
    ],
    "metrics": ["bleu"]
  }'
```

## Step 6: Monitor Progress

### Dashboard
1. Go to **Jobs** page
2. Click on your job
3. See:
   - Progress bar
   - Task completion status
   - Real-time cost tracking
   - Evaluation metrics

### API
```bash
# Get job status
curl http://localhost:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer $TOKEN"

# Get job results
curl http://localhost:8000/api/v1/jobs/{job_id}/results \
  -H "Authorization: Bearer $TOKEN"
```

## Step 7: Try Analytics Chat

1. Go to **Analytics Chat** page
2. Ask questions like:
   - "What's the best performing model?"
   - "Show me cost breakdown"
   - "Which model is most cost-effective?"
3. Get AI-powered insights!

## 🎉 You're Done!

Your LLM evaluation system is now running!

## 📊 What's Available

### Services Running
- ✅ Dashboard: http://localhost:3001
- ✅ API Gateway: http://localhost:8000
- ✅ Analytics API: http://localhost:8003
- ✅ API Docs: http://localhost:8000/docs
- ✅ RabbitMQ UI: http://localhost:15672 (admin/admin)
- ✅ MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
- ✅ Grafana: http://localhost:3000 (admin/admin)

### Key Features
- ✅ Multi-model evaluation (Gemini, GPT, Claude)
- ✅ Real-time progress tracking
- ✅ Cost tracking per model
- ✅ Response caching (saves money)
- ✅ Evaluation metrics (BLEU, etc.)
- ✅ Natural language analytics
- ✅ Deployment readiness assessment

## 🔧 Common Commands

```bash
# View logs
make logs

# Stop all services
make down

# Restart services
make restart

# View specific service logs
docker-compose logs -f api-gateway
docker-compose logs -f worker-gemini

# Scale workers
docker-compose up -d --scale worker-gemini=5

# Clean everything (CAUTION: Deletes data)
make clean
```

## 🐛 Troubleshooting

### Services not starting?
```bash
# Check Docker is running
docker ps

# Check logs for errors
make logs

# Restart services
make restart
```

### Database connection errors?
```bash
# Wait for PostgreSQL to initialize (takes ~30 seconds)
docker-compose logs postgres

# Restart dependent services
docker-compose restart api-gateway orchestrator
```

### Worker not processing tasks?
```bash
# Check worker logs
docker-compose logs worker-gemini

# Verify RabbitMQ has messages
# Open http://localhost:15672
# Check "llm_tasks" queue

# Check API key is set
docker-compose exec worker-gemini env | grep GEMINI_API_KEY
```

### Dashboard not loading?
```bash
# Check dashboard logs
docker-compose logs dashboard

# Verify it's running
docker-compose ps dashboard

# Check API Gateway is accessible
curl http://localhost:8000/health
```

## 📚 Next Steps

### 1. Explore the Dashboard
- Create multiple jobs
- Compare different models
- Check deployment readiness
- Use analytics chat

### 2. Try Different Prompts
- Question answering
- Text summarization
- Code generation
- Creative writing

### 3. Compare Models
Create jobs with multiple models:
```json
{
  "models": ["gemini-pro", "gpt-4", "gpt-3.5-turbo", "claude-sonnet"],
  "prompts": ["Your prompt here"]
}
```

### 4. Monitor Costs
- Check cost per model in dashboard
- View cost breakdown in Analytics
- Set up alerts for cost thresholds

### 5. Assess Deployment Readiness
- Go to Deployment page
- Review 4-pillar assessment
- Check critical issues
- Get recommendations

## 🎓 Learn More

- [Full Architecture](./ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Dashboard Guide](./services/dashboard/README.md)
- [Design Decisions](./DESIGN.md)
- [Implementation Status](./FINAL_STATUS.md)

## 💡 Tips

### Performance
- Enable response caching (on by default)
- Scale workers based on load
- Use priority queues for urgent jobs

### Cost Optimization
- Start with GPT-3.5 or Gemini (cheaper)
- Use caching to avoid duplicate API calls
- Monitor cost per job in dashboard

### Best Practices
- Use descriptive job names
- Add multiple prompts per job
- Set appropriate priorities
- Monitor metrics regularly

## 🆘 Need Help?

1. Check logs: `make logs`
2. Review documentation in this repo
3. Inspect API docs: http://localhost:8000/docs
4. Check RabbitMQ queue status
5. Verify database connections

## 🎯 Common Use Cases

### Use Case 1: Model Selection
```
Goal: Choose the best model for your use case
Steps:
1. Create job with all models
2. Use same prompts across models
3. Compare metrics in dashboard
4. Check cost vs performance tradeoff
5. Review deployment readiness
```

### Use Case 2: Prompt Engineering
```
Goal: Optimize prompts for best results
Steps:
1. Create multiple jobs with prompt variations
2. Use same model across jobs
3. Compare metrics to find best prompt
4. Iterate and improve
```

### Use Case 3: Cost Analysis
```
Goal: Minimize costs while maintaining quality
Steps:
1. Run evaluations on all models
2. Go to Analytics → Cost Breakdown
3. Compare cost per task
4. Check quality metrics
5. Choose cost-effective option
```

### Use Case 4: Production Readiness
```
Goal: Validate model is ready for deployment
Steps:
1. Run comprehensive evaluation
2. Go to Deployment page
3. Review 4-pillar assessment
4. Address critical issues
5. Get APPROVED status
6. Deploy confidently
```

---

**Quick Start Version**: 1.0  
**Last Updated**: Current Session  
**Estimated Time**: 5 minutes  
**Difficulty**: Easy ✅
