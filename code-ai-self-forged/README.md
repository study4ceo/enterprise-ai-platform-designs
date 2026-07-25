# Code-AI-Self-Forged

An autonomous AI agent that thinks, writes, and executes code on its own.

This system enables AI to reason about problems, generate solutions, write code, and run it independently—forging its own path to solve real-world tasks.

## Features

- **Autonomous Reasoning**: Break down complex problems step-by-step
- **Code Generation**: Write Python code to solve problems
- **Safe Execution**: Validate and execute code in isolated subprocess
- **Self-Correction**: Analyze errors and iterate to find solutions
- **Interactive Mode**: Chat with the agent and watch it work
- **Memory**: Maintains conversation context for better decisions
- **🆕 Offline Mode**: Run completely local without API keys (Ollama support)
- **🆕 Multi-Provider**: Switch between cloud (Anthropic) and local (Ollama) models
- **🆕 Heavyweight Option**: Use Claude Opus 4.7 for maximum coding power

## Quick Start

### Choose Your Mode

**☁️ Cloud Mode** - Best quality, requires API key  
**💻 Offline Mode** - Free, no API key, runs local  
**⚡ Heavyweight** - Maximum power, 5x cost  

---

### Cloud Mode (Recommended for Production)

**Local Installation:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run
python main.py
```

**Docker:**
```bash
# 1. Set up API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 2. Build and run
docker-compose up -d

# 3. Attach to interactive session
docker attach code-ai-self-forged
```

---

### Offline Mode - No API Key! 🎉

**Local Installation:**
```bash
# 1. Install Ollama
# Windows: winget install Ollama.Ollama
# Or download: https://ollama.ai/download

# 2. Pull a model (one-time, ~5GB)
ollama pull llama3.1:8b

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure for offline
cp .env.offline.example .env

# 5. Run (no API key needed!)
python main.py
```

**Docker Offline:**
```bash
# 1. Start Ollama + Code-AI-Self-Forged
docker-compose -f docker-compose.offline.yml up -d

# 2. Pull model into Ollama (one-time)
docker exec -it ollama ollama pull llama3.1:8b

# 3. Use it (no API key!)
docker attach code-ai-self-forged-offline
```

---

### Heavyweight Mode (Maximum Coding Power)

For complex, critical problems requiring the highest quality:

```bash
# Use Claude Opus 4.7 (5x more expensive, significantly better)
cp .env.opus.example .env
# Add your ANTHROPIC_API_KEY
python main.py
```

Or set in existing `.env`:
```env
LLM_PROVIDER=anthropic
MODEL_NAME=claude-opus-4.7
```

See [OFFLINE-MODE.md](OFFLINE-MODE.md) and [MODEL-INFO.md](MODEL-INFO.md) for complete guides.

### Usage

**Interactive Mode:**
```bash
python main.py
```

Commands:
- Type your problem or question
- `reset` - Clear conversation
- `exit` or `quit` - Exit

**Command Line Mode:**
```bash
python main.py "Calculate fibonacci numbers up to 100"
```

### Model Options

Choose your model based on needs:

| Mode | Model | Cost | Performance | API Key? |
|------|-------|------|-------------|----------|
| **Balanced** | Claude Sonnet 4.6 | $3-15/M tokens | Excellent | Required |
| **Max Power** | Claude Opus 4.7 | $15-75/M tokens | Best | Required |
| **Offline** | Llama 3.1 8B | Free | Good | No |
| **Offline Pro** | CodeLlama 34B | Free | Very Good | No |

**Switch models:**
```env
# For max coding power
LLM_PROVIDER=anthropic
MODEL_NAME=claude-opus-4.7

# For offline mode
LLM_PROVIDER=ollama
OLLAMA_MODEL=codellama:34b
```

## How It Works

1. **User asks a problem** → Agent reasons about it
2. **Agent writes code** → Validates for safety
3. **Code executes** → Returns output or error
4. **Agent analyzes result** → Iterates if needed

The agent autonomously solves problems in up to 3 iterations, learning from each execution.

## Safety

- AST-based code validation
- Blocks dangerous operations (eval, exec, os.system)
- Subprocess isolation
- Execution timeout (30s default)
- No file access in MVP

## Configuration

### Cloud Mode (Anthropic Claude):
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
MODEL_NAME=claude-sonnet-4.6
MAX_TOKENS=8000
TEMPERATURE=0.7
EXECUTION_TIMEOUT=30
LOG_LEVEL=INFO
```

### Offline Mode (No API Key):
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
MAX_TOKENS=8000
TEMPERATURE=0.7
EXECUTION_TIMEOUT=30
LOG_LEVEL=INFO
```

See [MODEL-INFO.md](MODEL-INFO.md) for model recommendations.

## Project Structure

```
code-ai-self-forged/
├── main.py                      # Entry point, CLI interface
├── reasoning_agent.py           # AI reasoning and orchestration
├── code_executor.py             # Safe code execution engine
├── code_validator.py            # AST-based safety checks
├── config.py                    # Configuration management
├── logger.py                    # Structured logging
├── requirements.txt             # Dependencies
├── .env.example                 # Cloud mode config template
├── .env.offline.example         # Offline mode config template
├── Dockerfile                   # Container image
├── docker-compose.yml           # Cloud deployment
├── docker-compose.offline.yml   # Offline deployment
├── test_*.py                    # Test suites
├── run_all_tests.py            # Master test runner
├── DEPLOYMENT.md               # Deployment guide
├── OFFLINE-MODE.md             # Offline setup guide
├── MODEL-INFO.md               # Model recommendations
├── REAL-WORLD-PROBLEMS.md      # Problem examples
└── workspace/                  # Temporary execution space
```

## Example Session

```
You: Calculate the sum of squares from 1 to 10

Agent: I'll write code to solve this...

✓ Solved in 1 iteration(s)

Output:
385
```

## Test Suites

The project includes comprehensive test suites with **production-ready real-world problems**:

### Run All Tests
```bash
python run_all_tests.py
```

### Individual Test Suites

**1. Time Series Analysis** (`test_time_series.py`)
- Moving averages (7-day, 30-day)
- Anomaly detection with statistical analysis
- Seasonal pattern detection
- Combined time series analysis

**2. Data Analysis** (`test_data_analysis.py`)
- Log parsing and error detection
- Sales data aggregation
- CSV data transformation and cleaning

**3. Data Validation** (`test_validation.py`)
- Email address validation
- Credit card validation (Luhn algorithm)
- Password strength checking
- Phone number validation

**4. Financial Calculations** (`test_financial.py`)
- Financial report generation
- Compound interest calculations
- Portfolio rebalancing
- Loan amortization schedules

**5. Algorithms & Optimization** (`test_algorithms.py`)
- Meeting room scheduling
- Task priority optimization
- Inventory reorder calculations

**6. Business Logic** (`test_business_logic.py`)
- Shipping cost calculations
- Complex discount rules
- Employee leave balance tracking

### Run Individual Suites
```bash
python test_time_series.py
python test_data_analysis.py
python test_validation.py
python test_financial.py
python test_algorithms.py
python test_business_logic.py
```

Each test demonstrates the agent's ability to:
- ✅ Understand complex requirements
- ✅ Write production-quality code
- ✅ Execute and validate results
- ✅ Self-correct when errors occur
- ✅ Provide actionable insights

See [REAL-WORLD-PROBLEMS.md](REAL-WORLD-PROBLEMS.md) for detailed problem descriptions (25+ scenarios).

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide (local, Docker, AWS, GCP, Azure, Kubernetes)
- **[OFFLINE-MODE.md](OFFLINE-MODE.md)** - Run without API keys using local LLMs
- **[MODEL-INFO.md](MODEL-INFO.md)** - Model comparison, pricing, selection guide
- **[REAL-WORLD-PROBLEMS.md](REAL-WORLD-PROBLEMS.md)** - 25+ production-ready test problems

## Deployment Modes Comparison

| Feature | Cloud Mode | Offline Mode |
|---------|------------|--------------|
| **API Key Required** | ✅ Yes | ❌ No |
| **Cost** | $3-15 per 1M tokens | Free (after hardware) |
| **Quality** | Excellent (Claude 4.6) | Good (Llama 3.1) |
| **Speed** | Very Fast | Medium (GPU) / Slow (CPU) |
| **Privacy** | Data sent to cloud | Data stays local |
| **Internet Required** | Yes | No (after model download) |
| **Hardware Needed** | None | 8GB+ RAM |
| **Best For** | Production, quality | Development, privacy |

Choose based on your needs! See [OFFLINE-MODE.md](OFFLINE-MODE.md) for offline setup.

## Roadmap

- [x] MVP: Basic reasoning + Python execution
- [x] Production test suites (25+ real-world problems across 6 categories)
- [x] Docker deployment with docker-compose
- [x] Multi-cloud deployment guides (AWS, GCP, Azure)
- [x] Offline mode with Ollama (no API key needed)
- [x] Multi-provider support (Anthropic + Ollama)
- [x] Heavyweight option (Claude Opus 4.7)
- [ ] Docker-based code execution sandbox (enhanced security)
- [ ] Multi-language support (JavaScript, Go)
- [ ] File system operations
- [ ] Web API integration
- [ ] REST API interface
- [ ] Web UI

## License

MIT
