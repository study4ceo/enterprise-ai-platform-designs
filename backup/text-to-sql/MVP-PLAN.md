# Text-to-SQL Generator - MVP Plan

## Overview
Convert natural language questions to SQL queries using LLM.

## Tech Stack
- **Backend**: Python 3.14+
- **LLM**: Ollama (local) or Anthropic Claude
- **Database**: SQLite (for testing/demo)
- **UI**: Streamlit (simple web interface)

## Core Features (MVP)

### 1. Database Schema Input
- User provides table schema (JSON or SQL DDL)
- Store schema in memory for context

### 2. Natural Language Input
- User types question in plain English
- Example: "Show me all customers who bought more than $1000"

### 3. SQL Generation
- Send question + schema to LLM
- LLM generates SQL query
- Display generated query

### 4. Query Execution (Optional)
- Execute query against demo database
- Show results in table format

## Project Structure

```
text-to-sql/
├── app.py                 # Streamlit UI
├── sql_generator.py       # LLM integration
├── schema_parser.py       # Parse schema input
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── .env.example           # Config template
├── demo_db.sqlite         # Sample database
└── README.md             # Documentation
```

## Implementation Steps

### Step 1: Setup (30 min)
```python
# requirements.txt
streamlit>=1.30.0
anthropic>=0.40.0
openai>=1.12.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
```

### Step 2: LLM Integration (1 hour)
```python
# sql_generator.py
class SQLGenerator:
    def __init__(self, llm_provider="ollama"):
        # Initialize LLM client
        pass
    
    def generate_sql(self, question: str, schema: str) -> str:
        # Send to LLM with schema context
        # Return SQL query
        pass
```

### Step 3: Streamlit UI (1 hour)
```python
# app.py
import streamlit as st

# Schema input (text area)
# Question input (text input)
# Generate button
# Display SQL output
# Execute button (optional)
# Display results table
```

### Step 4: Demo Database (30 min)
- Create SQLite database with sample tables
- Customers, Orders, Products
- Add sample data

## Example Flow

**Input:**
- Schema: `CREATE TABLE customers (id INT, name VARCHAR, total_spent DECIMAL)`
- Question: "Show customers who spent more than $1000"

**LLM Prompt:**
```
Given this database schema:
{schema}

Convert this question to SQL:
{question}

Return only the SQL query, no explanation.
```

**Output:**
```sql
SELECT * FROM customers WHERE total_spent > 1000;
```

## Timeline

- **Setup & Config**: 30 minutes
- **LLM Integration**: 1 hour
- **Streamlit UI**: 1 hour
- **Demo Database**: 30 minutes
- **Testing**: 30 minutes
- **Total**: ~3.5 hours

## Next Steps

1. Create project structure
2. Install dependencies
3. Implement SQL generator
4. Build Streamlit UI
5. Create demo database
6. Test with sample queries

## Enhancements (Future)

- Multiple database support (PostgreSQL, MySQL)
- Query optimization suggestions
- Query history
- Schema visualization
- Multi-table joins
- Complex aggregations
- Export results (CSV, JSON)

## Ready to Start?

Run:
```bash
cd D:\code_ai\code\project-designs\text-to-sql
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
