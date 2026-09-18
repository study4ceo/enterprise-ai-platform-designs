"""SQL query generation using LLM."""

from typing import Optional
from config import settings


class SQLGenerator:
    """Generate SQL queries from natural language."""

    SYSTEM_PROMPT = """You are an expert SQL query generator.

Given a database schema and a natural language question, generate a valid SQL query.

Rules:
- Return ONLY the SQL query, no explanation
- Use proper SQL syntax
- Include appropriate WHERE, JOIN, GROUP BY, ORDER BY clauses as needed
- For aggregations, use proper GROUP BY
- Use table and column names exactly as provided in schema
- Return a single SQL statement only

Example:
Schema: CREATE TABLE users (id INT, name VARCHAR, age INT);
Question: Show all users older than 25
SQL: SELECT * FROM users WHERE age > 25;
"""

    def __init__(self):
        """Initialize SQL generator."""
        if settings.llm_provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.model_name
        elif settings.llm_provider == "groq":
            from openai import OpenAI
            self.client = OpenAI(
                base_url=settings.groq_base_url,
                api_key=settings.groq_api_key
            )
            self.model = settings.groq_model
        elif settings.llm_provider == "ollama":
            from openai import OpenAI
            self.client = OpenAI(
                base_url=settings.ollama_base_url,
                api_key="not-needed"
            )
            self.model = settings.ollama_model
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
        
        self.provider = settings.llm_provider

    def generate(self, question: str, schema: str) -> str:
        """Generate SQL query from question and schema.
        
        Args:
            question: Natural language question
            schema: Database schema (SQL DDL or description)
            
        Returns:
            Generated SQL query
        """
        prompt = f"""Database Schema:
{schema}

Question: {question}

Generate the SQL query:"""

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            sql = response.content[0].text.strip()
        else:  # ollama
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            sql = response.choices[0].message.content.strip()

        # Clean up markdown code blocks if present
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].split("```")[0].strip()

        return sql

    def explain_query(self, sql: str) -> str:
        """Generate natural language explanation of SQL query.
        
        Args:
            sql: SQL query
            
        Returns:
            Explanation in plain English
        """
        prompt = f"""Explain this SQL query in simple English:

{sql}

Provide a brief, clear explanation of what this query does."""

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        else:  # ollama
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            return response.choices[0].message.content.strip()
