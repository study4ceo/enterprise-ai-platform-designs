# Text-to-SQL Generator

Convert natural language questions to SQL queries using AI.

## Features

- 🔍 Natural language to SQL conversion
- 🤖 Works with Ollama (local) or Claude (cloud)
- 📊 Interactive web interface with Streamlit
- 💾 Demo SQLite database included
- ▶️ Execute queries and see results
- 📖 Query explanations in plain English

## Quick Start

### 1. Install Dependencies

```bash
cd D:\code_ai\code\project-designs\text-to-sql
pip install -r requirements.txt
```

### 2. Configure

```bash
# For Ollama (local, no API key)
cp .env.example .env
# Default config uses Ollama

# For Claude (cloud)
# Edit .env and set:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your_key_here
```

### 3. Create Demo Database

```bash
python create_demo_db.py
```

### 4. Run Application

```bash
streamlit run app.py
```

Open browser at: http://localhost:8501

## Usage

1. **Enter Schema**: Provide your database schema (SQL DDL format)
2. **Ask Question**: Type your question in plain English
3. **Generate**: Click "Generate SQL" to get the query
4. **Execute**: (Optional) Run query on demo database to see results
5. **Explain**: View explanation of what the query does

## Example Questions

- "Show me all customers from New York"
- "What are the top 5 best-selling products?"
- "List customers who spent more than $1000"
- "Show total revenue by product category"
- "Find orders placed in January 2024"

## Demo Database

Includes 3 tables:
- **customers**: Customer information
- **products**: Product catalog
- **orders**: Order history

## Configuration

Edit `.env`:

```env
# LLM Provider
LLM_PROVIDER=ollama  # or anthropic

# Ollama (local)
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434

# Anthropic (cloud)
ANTHROPIC_API_KEY=your_key
MODEL_NAME=claude-sonnet-4.6

# Generation
MAX_TOKENS=2000
TEMPERATURE=0.0
```

## Project Structure

```
text-to-sql/
├── app.py                 # Streamlit UI
├── sql_generator.py       # LLM integration
├── create_demo_db.py      # Demo database setup
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── .env.example           # Config template
├── demo_db.sqlite         # Demo database (created)
└── README.md             # This file
```

## Requirements

- Python 3.14+
- Ollama (for local mode) or Anthropic API key
- 8GB+ RAM (for Ollama)

## License

MIT
