# ETL Pipeline - Usage Guide

## Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to project directory
cd etl-pipeline

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template (optional)
cp .env.example .env
```

### 2. Prepare Data

Place your CSV files in `data/raw/`:

```bash
data/raw/
├── orders_2024-01-15.csv
├── orders_2024-01-16.csv
└── orders_2024-01-17.csv
```

### 3. Run Pipeline

```bash
python main.py
```

## Understanding the Output

### Success Output

```
2024-01-20 10:30:00 - INFO - Starting ETL Pipeline
============================================================
[1/4] EXTRACT: Reading CSV files
------------------------------------------------------------
2024-01-20 10:30:00 - INFO - Found 3 CSV file(s)
2024-01-20 10:30:00 - INFO - Extracted 150 rows
✓ Extract complete: 150 rows

[2/4] TRANSFORM: Cleaning and standardizing data
------------------------------------------------------------
2024-01-20 10:30:01 - INFO - Transformation complete
✓ Transform complete: 150 rows

[3/4] VALIDATE: Checking data quality
------------------------------------------------------------
2024-01-20 10:30:01 - INFO - ✓ All required columns present
2024-01-20 10:30:01 - INFO - ✓ No null values in required columns
2024-01-20 10:30:01 - INFO - ✓ No duplicate order_ids
2024-01-20 10:30:01 - INFO - ✓ All columns have correct data types
2024-01-20 10:30:01 - INFO - ✓ All amounts >= 0.0
2024-01-20 10:30:01 - INFO - ✓ All status values valid
2024-01-20 10:30:01 - INFO - ✓ Date range valid
✓ Validation complete: All checks passed

[4/4] LOAD: Writing to DuckDB
------------------------------------------------------------
2024-01-20 10:30:02 - INFO - Upserting 150 rows
2024-01-20 10:30:02 - INFO - ✅ Upsert complete. Total rows in table: 150
✓ Load complete: 150 rows

============================================================
✅ PIPELINE COMPLETED SUCCESSFULLY
============================================================
Stages: extract → transform → validate → load
Rows processed: 150
Rows loaded: 150
Total rows in database: 150
Total amount: $45,678.90
============================================================
```

### Failure Output

```
============================================================
[3/4] VALIDATE: Checking data quality
------------------------------------------------------------
2024-01-20 10:30:01 - ERROR - ❌ Validation failed: Amount Values
2024-01-20 10:30:01 - ERROR - Found 5 orders with amount < 0.0
Examples: [{'order_id': '1001', 'amount': -50.00}, ...]

============================================================
❌ PIPELINE FAILED
============================================================
Error: Validation failed: Found 5 orders with amount < 0.0
Stages completed: ['extract', 'transform']
============================================================
```

## Common Scenarios

### Scenario 1: First Run

```bash
# Place CSV files in data/raw/
python main.py
```

**Result:** 
- Data extracted, validated, and loaded
- Files moved to `data/processed/`
- Database created with data

### Scenario 2: Running Again with Same Files

```bash
# Files already processed and archived
python main.py
```

**Result:**
```
ERROR - No CSV files found in data/raw
PIPELINE FAILED
```

**Solution:** Add new CSV files to `data/raw/`

### Scenario 3: Running with New + Duplicate Data

```bash
# Add orders_2024-01-18.csv (contains some duplicate order_ids)
python main.py
```

**Result:**
- Existing records updated (by order_id)
- New records inserted
- No duplicates created ✅

### Scenario 4: Validation Failure

```bash
# CSV contains negative amounts
python main.py
```

**Result:**
- Pipeline stops at validation
- **NO DATA LOADED** ✅
- Error logged with details
- Files remain in `data/raw/`

**Fix:** Correct the data and run again

## Testing Idempotency

### Test 1: Load Same Data Twice

```bash
# First run
python main.py

# Move files back from processed to raw
mv data/processed/*.csv data/raw/

# Second run
python main.py
```

**Verify:**
```python
import duckdb
conn = duckdb.connect('orders.duckdb')
print(conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone())
# Should be same count, no duplicates
```

### Test 2: Partial Duplicate Data

**orders_batch1.csv:**
```csv
order_id,customer_id,order_date,amount,status
1001,C001,2024-01-15,100.00,completed
1002,C002,2024-01-15,200.00,pending
```

**orders_batch2.csv:**
```csv
order_id,customer_id,order_date,amount,status
1002,C002,2024-01-15,250.00,completed  # Updated amount and status
1003,C003,2024-01-16,300.00,pending    # New order
```

**Expected Result:**
- order_id 1001: Unchanged
- order_id 1002: Updated to $250.00, status completed
- order_id 1003: New insert
- Total rows: 3 (not 4)

## Querying the Database

### Python

```python
import duckdb

conn = duckdb.connect('orders.duckdb')

# Total orders
print(conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone())

# Orders by status
print(conn.execute("""
    SELECT status, COUNT(*) as count, SUM(amount) as total
    FROM orders_clean
    GROUP BY status
""").fetchall())

# Recent orders
print(conn.execute("""
    SELECT * FROM orders_clean
    ORDER BY order_date DESC
    LIMIT 10
""").fetchdf())

conn.close()
```

### DuckDB CLI

```bash
duckdb orders.duckdb

D SELECT COUNT(*) FROM orders_clean;
D SELECT * FROM orders_clean LIMIT 5;
D .quit
```

## Monitoring & Logs

### View Real-time Logs

```bash
# Watch logs as pipeline runs
tail -f logs/pipeline.log
```

### Check Last Run

```bash
# View last 50 lines
tail -n 50 logs/pipeline.log
```

### Search for Errors

```bash
grep "ERROR" logs/pipeline.log
grep "Validation failed" logs/pipeline.log
```

## Troubleshooting

### Problem: "No CSV files found"

**Cause:** No files in `data/raw/`

**Solution:** 
```bash
# Check directory
ls data/raw/

# Add CSV files
cp /path/to/orders.csv data/raw/
```

### Problem: "Missing required columns"

**Cause:** CSV has different column names

**Solution:** Update `COLUMN_MAPPING` in `src/config.py`:

```python
COLUMN_MAPPING: dict = {
    "order_id": ["order_id", "OrderID", "id", "order_number", "YOUR_COLUMN_NAME"],
    # ... add your column name variations
}
```

### Problem: "Validation failed: Invalid status"

**Cause:** CSV contains status values not in `VALID_STATUSES`

**Solution 1:** Update `.env`:
```ini
VALID_STATUSES=pending,completed,cancelled,refunded,your_new_status
```

**Solution 2:** Fix the CSV data

### Problem: "Database locked"

**Cause:** Another process has database open

**Solution:**
```bash
# Close any DuckDB connections
# Kill python processes if needed
pkill -9 python

# Or use a different database path
export DB_PATH=orders_new.duckdb
python main.py
```

## Advanced Usage

### Custom Configuration

Create `.env` file:

```ini
# Use different paths
RAW_DATA_PATH=./input
PROCESSED_DATA_PATH=./archive
DB_PATH=production.duckdb

# Custom validation
MIN_AMOUNT=10.0
VALID_STATUSES=confirmed,shipped,delivered

# More verbose logging
LOG_LEVEL=DEBUG
```

### Programmatic Usage

```python
from src.pipeline import run_pipeline, verify_database

# Run pipeline
result = run_pipeline(archive_files=True)

if result['status'] == 'success':
    print(f"Loaded {result['load_result']['rows_loaded']} rows")
    
    # Check database
    stats = verify_database()
    print(f"Total rows: {stats['total_rows']}")
```

### Disable File Archiving

```python
# Keep files in data/raw after processing
result = run_pipeline(archive_files=False)
```

## Performance Tips

### Large Files

For very large CSV files:

1. **Chunk Processing:** Modify `extract.py` to use `pd.read_csv(chunksize=10000)`
2. **Increase Memory:** Ensure sufficient RAM
3. **Batch Loading:** Load in smaller batches

### Many Files

For many small files:

1. Files are processed sequentially (safe)
2. Consider combining files first:
   ```bash
   cat data/raw/*.csv > combined.csv
   ```

## Next Steps

1. **Add Tests:** See `tests/` directory
2. **Schedule Pipeline:** Use cron or Task Scheduler
3. **Add Monitoring:** Integrate with monitoring tools
4. **Extend Validation:** Add business-specific rules
5. **Add Notifications:** Email/Slack on failure

## Support

For issues:
1. Check `logs/pipeline.log` first
2. Enable DEBUG logging: `LOG_LEVEL=DEBUG` in `.env`
3. Review validation errors carefully
4. Check CSV data format
