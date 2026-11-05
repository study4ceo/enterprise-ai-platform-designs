# ETL Pipeline - Production-Style Data Processing

A robust, production-ready ETL pipeline for processing daily CSV order files into a clean DuckDB database.

## Features

✅ **Modular Design** - Separate extract, transform, validate, and load phases  
✅ **Idempotent** - Safe to run multiple times, no duplicates  
✅ **Fail-Safe** - Validates data before loading, never loads bad data  
✅ **Type-Safe** - Full type hints throughout  
✅ **Comprehensive Logging** - Detailed logging at each step  
✅ **Flexible Input** - Handles CSV files with varying column names  

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (optional, defaults work fine)
```

### 3. Add Data

```bash
# Place your CSV files in data/raw/
# Example: data/raw/orders_2024-01-15.csv
```

### 4. Run Pipeline

```bash
python main.py
```

## Project Structure

```
etl-pipeline/
├── data/
│   ├── raw/              # Input CSV files
│   └── processed/        # Archived processed files
├── src/
│   ├── config.py         # Configuration management
│   ├── extract.py        # CSV extraction logic
│   ├── transform.py      # Data transformation
│   ├── validate.py       # Data validation
│   ├── load.py           # DuckDB loading
│   └── pipeline.py       # Orchestration
├── logs/                 # Application logs
├── orders.duckdb         # DuckDB database
└── main.py               # Entry point
```

## Module Overview

### Extract (`src/extract.py`)
- Reads CSV files from `data/raw/`
- Maps varying column names to standard names
- Selects only required columns
- Returns pandas DataFrame

### Transform (`src/transform.py`)
- Standardizes data types
- Cleans and formats data
- Handles missing values
- Applies business logic

### Validate (`src/validate.py`)
- Checks required columns exist
- Validates data types
- Checks business rules
- **Raises exceptions on failure** - pipeline stops immediately

### Load (`src/load.py`)
- Connects to DuckDB
- Creates table with proper schema
- Performs UPSERT operation (idempotent)
- Archives processed files

## Configuration

Edit `.env` file to customize:

```ini
# Database
DB_PATH=orders.duckdb

# Paths
RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed

# Logging
LOG_LEVEL=INFO
LOG_PATH=./logs/pipeline.log

# Required Columns
REQUIRED_COLUMNS=order_id,customer_id,order_date,amount,status

# Validation Rules
MIN_AMOUNT=0.0
VALID_STATUSES=pending,completed,cancelled,refunded
```

## CSV Format

### Expected Columns
The pipeline looks for these columns (various naming conventions supported):

- **order_id**: Unique identifier (also accepts: OrderID, order_number, id)
- **customer_id**: Customer identifier (also accepts: CustomerID, cust_id)
- **order_date**: Order date (also accepts: OrderDate, date, order_datetime)
- **amount**: Order amount (also accepts: Amount, total, order_total, price)
- **status**: Order status (also accepts: Status, order_status, state)

### Example CSV

```csv
order_id,customer_id,order_date,amount,status
1001,C001,2024-01-15,99.99,completed
1002,C002,2024-01-15,150.00,pending
```

## Idempotency

The pipeline uses `order_id` as the primary key. Running the pipeline multiple times with the same data will:
- Update existing records (UPSERT)
- Insert new records
- **Never create duplicates**

## Error Handling

### Validation Failures
If validation fails, the pipeline will:
1. Log detailed error information
2. Raise an exception
3. Stop execution immediately
4. **NOT load any data**

### Common Validation Errors
- Missing required columns
- Invalid data types
- Negative amounts
- Invalid status values
- Null values in required fields

## Logging

Logs are written to:
- Console (stdout)
- File: `./logs/pipeline.log`

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Testing

**Quick Test** (runs pipeline once, shows results):
```bash
python quick_test.py
```

**Full Test Suite** (tests normal run, idempotency, validation):
```bash
python test_pipeline.py
```

Sample test data is provided in `data/raw/`:
- `orders_2024_01_15.csv` - 5 orders with lowercase_underscore columns
- `orders_2024_01_16.csv` - 4 orders with PascalCase columns

The test suite validates:
- ✓ Normal pipeline execution
- ✓ Idempotency (no duplicates on re-run)
- ✓ Validation failure (bad data rejected)
- ✓ Column mapping (different CSV formats)
- ✓ Data archiving

## Database Schema

```sql
CREATE TABLE orders_clean (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR NOT NULL,
    order_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing

### Quick Test
Runs pipeline once and shows results:
```bash
python quick_test.py
```

### Full Test Suite
Tests normal run, idempotency, and validation:
```bash
python test_pipeline.py
```

**Sample test data** is provided in `data/raw/`:
- `orders_2024_01_15.csv` - 5 orders with lowercase_underscore columns
- `orders_2024_01_16.csv` - 4 orders with PascalCase columns

**The test suite validates:**
- ✓ Normal pipeline execution
- ✓ Idempotency (no duplicates on re-run)
- ✓ Validation failure (bad data rejected)
- ✓ Column mapping (different CSV formats)
- ✓ Data archiving

## Development

### Adding New Validation Rules

Edit `src/validate.py` and add your rules to the `validate_data()` function.

### Changing Column Mappings

Edit `COLUMN_MAPPING` in `src/config.py` to add new column name variations.

### Modifying Transformations

Edit `src/transform.py` to add new transformation logic.

## Troubleshooting

### "No CSV files found"
- Check files are in `data/raw/` directory
- Ensure files have `.csv` extension

### "Validation failed"
- Check log file for details: `logs/pipeline.log`
- Verify CSV data meets validation rules
- Check for missing or incorrect column names

### "Database locked"
- Close any DuckDB connections
- Only one process should access DuckDB at a time

## License

MIT

## Support

For issues or questions, check the logs first:
```bash
tail -f logs/pipeline.log
```
