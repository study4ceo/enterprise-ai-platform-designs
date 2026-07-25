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

## Quick Start

### Installation

```bash
# Clone or navigate to project
cd code-ai-self-forged

# Install dependencies (Python 3.14+)
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Docker Deployment (Recommended)

```bash
# 1. Set up environment
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# 2. Build and run
docker-compose up -d

# 3. Attach to interactive session
docker attach code-ai-self-forged

# Or run one-shot
docker-compose run --rm code-ai-self-forged python main.py "your problem"
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment options (local, Docker, AWS, GCP, Azure, Kubernetes).

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

Edit `.env` to customize:

```env
ANTHROPIC_API_KEY=your_key_here
MODEL_NAME=claude-sonnet-4-20250514
MAX_TOKENS=8000
TEMPERATURE=0.7
EXECUTION_TIMEOUT=30
LOG_LEVEL=INFO
```

## Project Structure

```
code-ai-self-forged/
├── main.py              # Entry point, CLI interface
├── reasoning_agent.py   # AI reasoning and orchestration
├── code_executor.py     # Safe code execution engine
├── code_validator.py    # AST-based safety checks
├── config.py            # Configuration management
├── logger.py            # Structured logging
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── workspace/           # Temporary execution space
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

## Roadmap

- [x] MVP: Basic reasoning + Python execution
- [x] Production test suites (25+ real-world problems across 6 categories)
- [x] Docker deployment with docker-compose
- [x] Multi-cloud deployment guides (AWS, GCP, Azure)
- [ ] Docker-based code execution sandbox (enhanced security)
- [ ] Multi-language support (JavaScript, Go)
- [ ] File system operations
- [ ] Web API integration
- [ ] REST API interface
- [ ] Web UI

## License

MIT
