"""Streamlit UI for Text-to-SQL Generator."""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

from sql_generator import SQLGenerator
from config import settings

# Page config
st.set_page_config(
    page_title="Text-to-SQL Generator",
    page_icon="🔍",
    layout="wide"
)

# Initialize
@st.cache_resource
def get_generator():
    return SQLGenerator()

generator = get_generator()

# Title
st.title("🔍 Text-to-SQL Generator")
st.markdown("Convert natural language questions to SQL queries using AI")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info(f"**LLM Provider:** {settings.llm_provider}")
    if settings.llm_provider == "ollama":
        st.info(f"**Model:** {settings.ollama_model}")
    else:
        st.info(f"**Model:** {settings.model_name}")
    
    st.divider()
    
    st.header("📊 Demo Database")
    if Path(settings.db_path).exists():
        st.success("Demo database loaded")
        
        # Show table info
        conn = sqlite3.connect(settings.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        st.write("**Tables:**")
        for table in tables:
            st.write(f"- {table}")
    else:
        st.warning("Demo database not found")
        if st.button("Create Demo Database"):
            from create_demo_db import create_demo_database
            create_demo_database(str(settings.db_path))
            st.rerun()

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input")
    
    # Schema input
    default_schema = """CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    total_spent DECIMAL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price DECIMAL,
    stock INTEGER
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    order_date DATE,
    total_amount DECIMAL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);"""
    
    schema = st.text_area(
        "Database Schema (SQL DDL)",
        value=default_schema,
        height=250,
        help="Provide your database schema in SQL DDL format"
    )
    
    # Question input
    question = st.text_input(
        "Your Question",
        placeholder="e.g., Show me all customers who spent more than $1000",
        help="Ask a question in plain English"
    )
    
    # Generate button
    generate_btn = st.button("🚀 Generate SQL", type="primary", use_container_width=True)

with col2:
    st.header("💻 Output")
    
    if generate_btn and question and schema:
        with st.spinner("Generating SQL query..."):
            try:
                # Generate SQL
                sql_query = generator.generate(question, schema)
                
                # Display SQL
                st.subheader("Generated SQL:")
                st.code(sql_query, language="sql")
                
                # Explain query
                with st.expander("📖 Query Explanation"):
                    with st.spinner("Generating explanation..."):
                        explanation = generator.explain_query(sql_query)
                        st.write(explanation)
                
                # Execute button
                if Path(settings.db_path).exists():
                    st.divider()
                    if st.button("▶️ Execute Query on Demo Database"):
                        with st.spinner("Executing query..."):
                            try:
                                conn = sqlite3.connect(settings.db_path)
                                df = pd.read_sql_query(sql_query, conn)
                                conn.close()
                                
                                st.subheader("📊 Results:")
                                st.dataframe(df, use_container_width=True)
                                st.info(f"Returned {len(df)} row(s)")
                            except Exception as e:
                                st.error(f"Execution error: {str(e)}")
                
            except Exception as e:
                st.error(f"Error generating SQL: {str(e)}")
    
    elif generate_btn:
        st.warning("Please provide both schema and question")

# Footer
st.divider()
st.markdown("""
### 💡 Example Questions:
- Show me all customers from New York
- What are the top 5 best-selling products?
- List customers who spent more than $1000
- Show total revenue by product category
- Find orders placed in January 2024
""")
