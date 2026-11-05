# ETL Pipeline Project Structure

```
etl-pipeline/
│
├── data/
│   ├── raw/              # Input CSV files go here
│   └── processed/        # Archive processed files here
│
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── extract.py        # Extract module - read CSV files
│   ├── transform.py      # Transform module - clean and standardize data
│   ├── validate.py       # Validate module - data quality checks
│   ├── load.py           # Load module - write to DuckDB
│   └── pipeline.py       # Main orchestration
│
├── logs/                 # Log files
│
├── tests/
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_transform.py
│   ├── test_validate.py
│   └── test_load.py
│
├── orders.duckdb         # DuckDB database file
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
├── README.md             # Project documentation
└── main.py               # Entry point
```

## Module Responsibilities

### 1. `config.py`
- Load configuration from environment variables or config file
- Define paths, column mappings, validation rules
- Database connection settings

### 2. `extract.py`
- Read CSV files from `./data/raw`
- Handle variable column names
- Select only required columns
- Return pandas DataFrame

### 3. `transform.py`
- Standardize column names
- Convert data types
- Handle missing values
- Apply business logic transformations

### 4. `validate.py`
- Check required columns exist
- Validate data types
- Check for nulls in critical fields
- Verify business rules (e.g., amount >= 0)
- **Raise exceptions on validation failure**

### 5. `load.py`
- Connect to DuckDB
- Create table if not exists
- Implement idempotent inserts (upsert logic using order_id as key)
- Archive processed files

### 6. `pipeline.py`
- Orchestrate ETL flow
- Error handling and logging
- Coordinate module execution

## Key Design Principles

✅ **Idempotency**: Using MERGE/UPSERT based on `order_id` primary key  
✅ **Fail Loudly**: Validation errors raise exceptions, stopping execution  
✅ **Type Safety**: All functions have type hints  
✅ **Logging**: Comprehensive logging at each step  
✅ **Modularity**: Each phase is a separate, testable module  
✅ **No Silent Failures**: Never load bad data  

## Data Flow

```
CSV Files → Extract → Transform → Validate → Load → DuckDB
                                     ↓
                                  [FAIL]
                                     ↓
                              Log Error & Exit
```
