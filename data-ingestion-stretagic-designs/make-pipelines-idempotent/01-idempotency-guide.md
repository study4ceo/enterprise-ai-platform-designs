# Making Data Pipelines Idempotent
## A Comprehensive Guide to Idempotency in Data Engineering

---

## Table of Contents
1. [Introduction](#introduction)
2. [What is Idempotency?](#what-is-idempotency)
3. [Why Idempotency Matters](#why-matters)
4. [Core Principles](#core-principles)
5. [Implementation Strategies](#implementation-strategies)
6. [Technology-Specific Patterns](#technology-patterns)
7. [Testing Idempotency](#testing)
8. [Common Pitfalls](#pitfalls)
9. [Real-World Examples](#examples)
10. [Best Practices](#best-practices)

---

## 1. Introduction {#introduction}

**Idempotency** is the property that allows an operation to be applied multiple times without changing the result beyond the initial application.

In data engineering:
```
Operation(data) = Result
Operation(Operation(data)) = Result
Operation(Operation(Operation(data))) = Result
```

**This guide covers:**
- Theoretical foundations
- Practical implementation patterns
- Code examples in Python, Java, SQL
- Real-world scenarios
- Testing strategies
- Common mistakes and solutions

---

## 2. What is Idempotency? {#what-is-idempotency}

### Mathematical Definition

An operation `f` is idempotent if:
```
f(f(x)) = f(x)
```

### Data Engineering Context

**Idempotent Pipeline:**
```
Pipeline(data, run_1) = Result
Pipeline(data, run_2) = Result  # Same result
Pipeline(data, run_3) = Result  # Same result
```

**Non-Idempotent Pipeline (Problematic):**
```
Pipeline(data, run_1) = Result_1
Pipeline(data, run_2) = Result_1 + Result_2  # Duplicates!
Pipeline(data, run_3) = Result_1 + Result_2 + Result_3  # More duplicates!
```

### Visual Example

**Idempotent (✅ Good):**
```
Source Data: [A, B, C]
   ↓
Run 1: Target = [A, B, C]
   ↓
Run 2: Target = [A, B, C]  ← Same result
   ↓
Run 3: Target = [A, B, C]  ← Same result
```

**Non-Idempotent (❌ Bad):**
```
Source Data: [A, B, C]
   ↓
Run 1: Target = [A, B, C]
   ↓
Run 2: Target = [A, B, C, A, B, C]  ← Duplicates!
   ↓
Run 3: Target = [A, B, C, A, B, C, A, B, C]  ← More duplicates!
```

---

## 3. Why Idempotency Matters {#why-matters}

### Real-World Scenarios Where Re-runs Happen

1. **Pipeline Failures**
   - Network timeout during write
   - Partial batch processing
   - System crash mid-execution

2. **Scheduled Re-runs**
   - Catching up after downtime
   - Backfilling historical data
   - Fixing data quality issues

3. **Orchestration Retries**
   - Airflow/Prefect automatic retries
   - Kubernetes pod restarts
   - Lambda function timeouts

4. **Manual Re-runs**
   - Debugging
   - Testing changes
   - Data refresh requests

### Consequences of Non-Idempotent Pipelines

❌ **Data Duplication**
```sql
-- Non-idempotent INSERT
INSERT INTO orders SELECT * FROM staging_orders;

-- Result after 3 runs:
-- Every order appears 3 times!
```

❌ **Incorrect Aggregations**
```python
# Non-idempotent aggregation
daily_total += batch_total

# After re-run: daily_total is doubled!
```

❌ **Data Corruption**
```python
# Non-idempotent UPDATE
UPDATE users SET login_count = login_count + 1

# After re-run: login_count is incorrect!
```

### Benefits of Idempotent Pipelines

✅ **Safe to Retry** - No fear of duplicates or corruption  
✅ **Easier Debugging** - Can re-run without cleanup  
✅ **Simpler Recovery** - Just re-run failed steps  
✅ **Reliable Backfills** - Process historical data safely  
✅ **Reduced Operational Burden** - Less manual intervention  

---

## 4. Core Principles {#core-principles}

### Principle 1: Deterministic Processing

**Same input → Same output**

```python
# ✅ Deterministic (Good)
def process_order(order):
    return {
        'order_id': order['id'],
        'total': order['amount'] * 1.1,  # Always 10% markup
        'status': 'processed'
    }

# ❌ Non-deterministic (Bad)
def process_order(order):
    return {
        'order_id': order['id'],
        'total': order['amount'] * random.uniform(1.0, 1.2),  # Random!
        'processed_at': datetime.now(),  # Changes every run!
        'status': 'processed'
    }
```

### Principle 2: Upsert Instead of Insert

**Replace existing data rather than appending**

```sql
-- ❌ Non-idempotent: Always inserts
INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com');

-- ✅ Idempotent: Replace if exists
INSERT INTO users (id, name, email)
VALUES (1, 'Alice', 'alice@example.com')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email;
```

### Principle 3: Delete Before Insert

**Clear destination before writing**

```python
# ✅ Idempotent pattern
def load_data(date):
    # 1. Delete existing data for this date
    cursor.execute("DELETE FROM daily_summary WHERE date = %s", (date,))
    
    # 2. Insert fresh data
    cursor.execute("""
        INSERT INTO daily_summary
        SELECT date, COUNT(*), SUM(amount)
        FROM orders
        WHERE date = %s
        GROUP BY date
    """, (date,))
    
    conn.commit()
```

### Principle 4: Use Unique Identifiers

**Every record has a stable, unique ID**

```python
# ✅ Good: Stable, deterministic ID
def generate_record_id(source_id, date):
    return f"{source_id}_{date.strftime('%Y%m%d')}"

# ❌ Bad: Non-deterministic ID
def generate_record_id():
    return str(uuid.uuid4())  # Different every time!
```

### Principle 5: State Tracking

**Track what has been processed**

```python
# ✅ Idempotent with state tracking
class IdempotentProcessor:
    def __init__(self):
        self.processed_ids = set()
        self.load_processed_state()
    
    def process(self, record):
        record_id = record['id']
        
        # Skip if already processed
        if record_id in self.processed_ids:
            return
        
        # Process record
        result = self.do_processing(record)
        
        # Mark as processed
        self.processed_ids.add(record_id)
        self.save_processed_state()
        
        return result
```

---

## 5. Implementation Strategies {#implementation-strategies}

### Strategy 1: Truncate and Load

**Best for:** Small to medium datasets, daily/weekly refreshes

```python
def truncate_and_load(date, data):
    """
    Truncate partition and reload
    """
    # Delete existing data
    cursor.execute("""
        DELETE FROM sales_daily 
        WHERE sale_date = %s
    """, (date,))
    
    # Load fresh data
    cursor.executemany("""
        INSERT INTO sales_daily (sale_date, product_id, amount)
        VALUES (%s, %s, %s)
    """, data)
    
    conn.commit()

# Multiple runs produce same result
truncate_and_load('2024-01-15', sales_data)  # Run 1
truncate_and_load('2024-01-15', sales_data)  # Run 2 (idempotent)
```

### Strategy 2: Merge/Upsert Pattern

**Best for:** Incremental updates, CDC, slowly changing dimensions

```sql
-- PostgreSQL MERGE (UPSERT)
INSERT INTO products (product_id, name, price, updated_at)
VALUES (123, 'Widget', 19.99, NOW())
ON CONFLICT (product_id) 
DO UPDATE SET
    name = EXCLUDED.name,
    price = EXCLUDED.price,
    updated_at = EXCLUDED.updated_at;

-- SQL Server MERGE
MERGE INTO products AS target
USING staging_products AS source
ON target.product_id = source.product_id
WHEN MATCHED THEN
    UPDATE SET 
        name = source.name,
        price = source.price,
        updated_at = GETDATE()
WHEN NOT MATCHED THEN
    INSERT (product_id, name, price, updated_at)
    VALUES (source.product_id, source.name, source.price, GETDATE());
```

**Python implementation:**
```python
def upsert_records(records):
    """
    Idempotent upsert using INSERT...ON CONFLICT
    """
    for record in records:
        cursor.execute("""
            INSERT INTO products (product_id, name, price)
            VALUES (%(product_id)s, %(name)s, %(price)s)
            ON CONFLICT (product_id) 
            DO UPDATE SET
                name = EXCLUDED.name,
                price = EXCLUDED.price
        """, record)
    
    conn.commit()

# Idempotent: Running multiple times produces same result
upsert_records(products)  # Run 1
upsert_records(products)  # Run 2 (no duplicates)
```

### Strategy 3: Checkpointing with State

**Best for:** Stream processing, incremental loads

```python
class CheckpointedProcessor:
    """
    Process data with checkpoint tracking
    """
    
    def __init__(self, checkpoint_file='checkpoint.json'):
        self.checkpoint_file = checkpoint_file
        self.checkpoint = self.load_checkpoint()
    
    def load_checkpoint(self):
        """Load last processed position"""
        try:
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'last_id': 0, 'last_timestamp': None}
    
    def save_checkpoint(self):
        """Save current position"""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f)
    
    def process(self):
        """Process new records since last checkpoint"""
        last_id = self.checkpoint['last_id']
        
        # Fetch only new records
        cursor.execute("""
            SELECT id, data, created_at
            FROM source_table
            WHERE id > %s
            ORDER BY id
        """, (last_id,))
        
        for row in cursor.fetchall():
            # Process record
            self.process_record(row)
            
            # Update checkpoint
            self.checkpoint['last_id'] = row['id']
            self.checkpoint['last_timestamp'] = row['created_at']
        
        # Save checkpoint
        self.save_checkpoint()
    
    def process_record(self, record):
        """Process individual record"""
        # Your processing logic here
        pass

# Idempotent: Re-running only processes new data
processor = CheckpointedProcessor()
processor.process()  # Processes records 1-100
processor.process()  # Processes records 101-200 (no re-processing)
```

### Strategy 4: Deterministic IDs

**Best for:** Event-driven systems, distributed processing

```python
import hashlib

def generate_deterministic_id(*components):
    """
    Generate deterministic ID from components
    """
    # Combine components
    content = '|'.join(str(c) for c in components)
    
    # Hash to create stable ID
    return hashlib.sha256(content.encode()).hexdigest()

# Usage
def process_event(user_id, event_type, timestamp):
    # Generate deterministic ID
    event_id = generate_deterministic_id(user_id, event_type, timestamp)
    
    # Use ID for idempotent insert
    cursor.execute("""
        INSERT INTO events (event_id, user_id, event_type, timestamp)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (event_id) DO NOTHING
    """, (event_id, user_id, event_type, timestamp))

# Idempotent: Same input produces same ID
process_event(123, 'click', '2024-01-15 10:30:00')  # Run 1
process_event(123, 'click', '2024-01-15 10:30:00')  # Run 2 (no duplicate)
```

### Strategy 5: Temporary Staging Pattern

**Best for:** Complex transformations, transaction safety

```python
def idempotent_load_with_staging(date, source_query):
    """
    Load data idempotently using staging table
    """
    try:
        # 1. Create/truncate staging table
        cursor.execute("""
            CREATE TEMP TABLE staging_data AS
            SELECT * FROM target_table WHERE 1=0
        """)
        
        # 2. Load data into staging
        cursor.execute(f"""
            INSERT INTO staging_data
            {source_query}
        """)
        
        # 3. Begin transaction
        cursor.execute("BEGIN")
        
        # 4. Delete existing data for this date
        cursor.execute("""
            DELETE FROM target_table
            WHERE date = %s
        """, (date,))
        
        # 5. Move from staging to target
        cursor.execute("""
            INSERT INTO target_table
            SELECT * FROM staging_data
        """)
        
        # 6. Commit transaction
        cursor.execute("COMMIT")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise

# Idempotent: Safe to retry on failure
idempotent_load_with_staging('2024-01-15', source_query)
```

---

## 6. Technology-Specific Patterns {#technology-patterns}

### Apache Spark - Idempotent Writes

```python
from pyspark.sql import SparkSession

def idempotent_spark_pipeline(date):
    """
    Idempotent Spark pipeline using overwrite mode
    """
    spark = SparkSession.builder.appName("Idempotent Pipeline").getOrCreate()
    
    # Read source data
    df = spark.read.parquet(f"s3://source/date={date}/")
    
    # Transform
    transformed = df.filter(df.amount > 0).groupBy("user_id").sum("amount")
    
    # Write idempotently (overwrite partition)
    transformed.write \
        .mode("overwrite") \
        .partitionBy("date") \
        .parquet(f"s3://target/")
    
    # Alternative: Use Delta Lake for ACID guarantees
    transformed.write \
        .format("delta") \
        .mode("overwrite") \
        .option("replaceWhere", f"date = '{date}'") \
        .save("s3://target/delta/")

# Idempotent: Multiple runs produce same result
idempotent_spark_pipeline('2024-01-15')
```

### Apache Kafka - Exactly-Once Semantics

```java
// Kafka idempotent producer
Properties props = new Properties();
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, "true");
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// Producer automatically deduplicates retries
producer.send(new ProducerRecord<>("topic", "key", "value"));
```

### Apache Airflow - Idempotent DAGs

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def idempotent_task(execution_date, **context):
    """
    Task that can be safely re-run
    """
    date_str = execution_date.strftime('%Y-%m-%d')
    
    # Idempotent processing
    cursor.execute("DELETE FROM summary WHERE date = %s", (date_str,))
    cursor.execute("""
        INSERT INTO summary
        SELECT date, COUNT(*), SUM(amount)
        FROM orders
        WHERE date = %s
        GROUP BY date
    """, (date_str,))
    conn.commit()

with DAG('idempotent_pipeline', schedule_interval='@daily') as dag:
    
    task = PythonOperator(
        task_id='process_data',
        python_callable=idempotent_task,
        provide_context=True
    )

# Airflow can safely retry or backfill this DAG
```

### dbt - Idempotent by Design

```sql
-- models/daily_summary.sql
-- dbt automatically makes this idempotent

{{ config(
    materialized='incremental',
    unique_key='date',
    on_schema_change='fail'
) }}

SELECT
    DATE(created_at) as date,
    COUNT(*) as order_count,
    SUM(amount) as total_amount
FROM {{ source('raw', 'orders') }}

{% if is_incremental() %}
    -- Only process new data
    WHERE created_at > (SELECT MAX(date) FROM {{ this }})
{% endif %}

GROUP BY date

-- dbt run: Idempotent execution
-- dbt run --full-refresh: Re-process all data
```

---

## Document Structure

This is document 1 of the series. Additional documents will cover:
- **02-advanced-patterns.md** - Complex scenarios and solutions
- **03-testing-strategies.md** - How to test idempotency
- **04-code-examples.md** - Complete working examples
- **05-troubleshooting.md** - Common issues and fixes

---

**Status**: Document 1 Complete ✅


## 7. Testing Idempotency {#testing}

### Test Strategy

**Idempotency Test Pattern:**
```python
def test_idempotency(pipeline_function, input_data):
    """
    Generic idempotency test
    """
    # Run pipeline first time
    result_1 = pipeline_function(input_data)
    
    # Run pipeline second time with same input
    result_2 = pipeline_function(input_data)
    
    # Run pipeline third time
    result_3 = pipeline_function(input_data)
    
    # All results should be identical
    assert result_1 == result_2 == result_3, "Pipeline is not idempotent!"
```

### Unit Tests

```python
import pytest
from datetime import datetime

def test_idempotent_upsert():
    """Test that upsert operation is idempotent"""
    # Setup
    db.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))")
    
    # Test data
    user_data = {'id': 1, 'name': 'Alice'}
    
    # First insert
    upsert_user(user_data)
    result_1 = db.query("SELECT * FROM users WHERE id = 1")
    
    # Second insert (should not duplicate)
    upsert_user(user_data)
    result_2 = db.query("SELECT * FROM users WHERE id = 1")
    
    # Third insert
    upsert_user(user_data)
    result_3 = db.query("SELECT * FROM users WHERE id = 1")
    
    # Assert same result
    assert len(result_1) == 1
    assert result_1 == result_2 == result_3
    
    # Assert no duplicates
    count = db.query("SELECT COUNT(*) FROM users WHERE id = 1")[0][0]
    assert count == 1

def test_deterministic_id_generation():
    """Test that ID generation is deterministic"""
    # Same inputs should produce same ID
    id_1 = generate_deterministic_id(user_id=123, event='click', timestamp='2024-01-15')
    id_2 = generate_deterministic_id(user_id=123, event='click', timestamp='2024-01-15')
    id_3 = generate_deterministic_id(user_id=123, event='click', timestamp='2024-01-15')
    
    assert id_1 == id_2 == id_3

def test_no_timestamp_in_output():
    """Test that output doesn't contain processing timestamps"""
    # Process same data twice
    result_1 = process_data({'value': 100})
    result_2 = process_data({'value': 100})
    
    # Results should be identical (no processing timestamps)
    assert result_1 == result_2
    
    # Make sure there's no 'processed_at' field with current time
    assert 'processed_at' not in result_1 or result_1['processed_at'] == result_2['processed_at']
```

### Integration Tests

```python
def test_end_to_end_idempotency():
    """Test full pipeline idempotency"""
    # Setup test data
    test_date = '2024-01-15'
    source_data = [
        {'id': 1, 'amount': 100},
        {'id': 2, 'amount': 200},
        {'id': 3, 'amount': 300}
    ]
    
    # Run pipeline first time
    run_pipeline(test_date, source_data)
    result_1 = db.query(f"SELECT * FROM summary WHERE date = '{test_date}'")
    
    # Run pipeline second time (simulating retry)
    run_pipeline(test_date, source_data)
    result_2 = db.query(f"SELECT * FROM summary WHERE date = '{test_date}'")
    
    # Run pipeline third time
    run_pipeline(test_date, source_data)
    result_3 = db.query(f"SELECT * FROM summary WHERE date = '{test_date}'")
    
    # All results should be identical
    assert result_1 == result_2 == result_3
    
    # Verify expected output
    assert len(result_1) == 1  # Should have exactly one summary row
    assert result_1[0]['total'] == 600  # Sum of amounts

def test_partial_failure_recovery():
    """Test that pipeline can recover from partial failures"""
    test_date = '2024-01-15'
    
    # First run: simulate failure after partial processing
    with pytest.raises(SimulatedFailure):
        run_pipeline_with_failure(test_date, fail_at_step=2)
    
    # Second run: complete successfully
    run_pipeline(test_date)
    result_after_recovery = db.query(f"SELECT * FROM summary WHERE date = '{test_date}'")
    
    # Third run: should produce same result
    run_pipeline(test_date)
    result_final = db.query(f"SELECT * FROM summary WHERE date = '{test_date}'")
    
    assert result_after_recovery == result_final
```

### Load Tests

```python
import concurrent.futures

def test_concurrent_idempotency():
    """Test idempotency under concurrent execution"""
    test_date = '2024-01-15'
    num_threads = 10
    
    # Run pipeline concurrently multiple times
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(run_pipeline, test_date) for _ in range(num_threads)]
        results = [f.result() for f in futures]
    
    # Query final state
    final_result = db.query(f"SELECT * FROM summary WHERE date = '{test_date}'")
    
    # Should have exactly one row (no duplicates)
    assert len(final_result) == 1
    
    # Verify data is correct
    assert final_result[0]['total'] == expected_total
```

---

## 8. Common Pitfalls {#pitfalls}

### Pitfall 1: Using Current Timestamp

```python
# ❌ Non-idempotent: Uses current timestamp
def process_order(order):
    return {
        'order_id': order['id'],
        'processed_at': datetime.now()  # Changes on every run!
    }

# ✅ Idempotent: Use source timestamp or remove it
def process_order(order):
    return {
        'order_id': order['id'],
        'created_at': order['timestamp']  # From source data
    }
```

### Pitfall 2: Auto-Increment IDs

```python
# ❌ Non-idempotent: Database auto-increment
cursor.execute("""
    INSERT INTO orders (amount, customer_id)
    VALUES (%s, %s)
""", (amount, customer_id))
# order_id is auto-generated - different on each run!

# ✅ Idempotent: Generate deterministic ID
order_id = generate_id(customer_id, order_date, sequence)
cursor.execute("""
    INSERT INTO orders (order_id, amount, customer_id)
    VALUES (%s, %s, %s)
    ON CONFLICT (order_id) DO UPDATE SET
        amount = EXCLUDED.amount
""", (order_id, amount, customer_id))
```

### Pitfall 3: Stateful Aggregations

```python
# ❌ Non-idempotent: Incremental counter
class Counter:
    def __init__(self):
        self.count = 0
    
    def process(self, item):
        self.count += 1  # Accumulates on each run!
        return self.count

# ✅ Idempotent: Calculate from source data
def count_items(items):
    return len(items)  # Always same for same input
```

### Pitfall 4: Append-Only Operations

```python
# ❌ Non-idempotent: Always appends
def save_results(results):
    with open('output.json', 'a') as f:  # Append mode!
        json.dump(results, f)

# ✅ Idempotent: Overwrite or use unique identifiers
def save_results(results, date):
    output_file = f'output_{date}.json'
    with open(output_file, 'w') as f:  # Write mode
        json.dump(results, f)
```

### Pitfall 5: External Dependencies Without Deduplication

```python
# ❌ Non-idempotent: Sends email on every run
def process_alert(alert):
    send_email(alert)  # Email sent multiple times!

# ✅ Idempotent: Track sent alerts
sent_alerts = set()

def process_alert(alert):
    alert_id = alert['id']
    if alert_id not in sent_alerts:
        send_email(alert)
        sent_alerts.add(alert_id)
```

---

## 9. Real-World Examples {#examples}

### Example 1: Daily Sales Summary Pipeline

```python
class DailySalesSummary:
    """
    Idempotent pipeline for daily sales aggregation
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def run(self, date):
        """
        Process sales for a specific date
        Idempotent: Can be run multiple times safely
        """
        # Step 1: Delete existing summary for this date
        self.db.execute("""
            DELETE FROM daily_sales_summary
            WHERE sale_date = %s
        """, (date,))
        
        # Step 2: Calculate fresh summary
        summary = self.db.query("""
            SELECT
                %s as sale_date,
                COUNT(*) as order_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_order_value,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM orders
            WHERE DATE(created_at) = %s
        """, (date, date))
        
        # Step 3: Insert summary
        self.db.execute("""
            INSERT INTO daily_sales_summary
                (sale_date, order_count, total_amount, avg_order_value, unique_customers)
            VALUES (%s, %s, %s, %s, %s)
        """, summary[0])
        
        self.db.commit()
        
        return summary[0]

# Usage: Safe to run multiple times
pipeline = DailySalesSummary(db)
result = pipeline.run('2024-01-15')  # Run 1
result = pipeline.run('2024-01-15')  # Run 2 (same result)
```

### Example 2: Event Stream Processing

```python
from kafka import KafkaConsumer
import hashlib

class IdempotentEventProcessor:
    """
    Process events idempotently using deterministic IDs
    """
    
    def __init__(self):
        self.consumer = KafkaConsumer('events')
        self.processed_events = set()
        self.load_processed_state()
    
    def generate_event_id(self, event):
        """Generate deterministic event ID"""
        content = f"{event['user_id']}_{event['event_type']}_{event['timestamp']}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def process_event(self, event):
        """Process event idempotently"""
        event_id = self.generate_event_id(event)
        
        # Skip if already processed
        if event_id in self.processed_events:
            return
        
        # Process event
        cursor.execute("""
            INSERT INTO processed_events (event_id, user_id, event_type, data)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING
        """, (event_id, event['user_id'], event['event_type'], event['data']))
        
        # Mark as processed
        self.processed_events.add(event_id)
        self.save_processed_state()
    
    def load_processed_state(self):
        """Load previously processed event IDs"""
        results = cursor.execute("SELECT event_id FROM processed_events")
        self.processed_events = {row[0] for row in results}
    
    def save_processed_state(self):
        """Persist processed state"""
        # Already saved in database
        pass

# Safe to restart: Only processes new events
processor = IdempotentEventProcessor()
processor.process_event({'user_id': 123, 'event_type': 'click', 'timestamp': '2024-01-15'})
processor.process_event({'user_id': 123, 'event_type': 'click', 'timestamp': '2024-01-15'})  # Skipped
```

### Example 3: File-Based Data Load

```python
import os
import shutil

class IdempotentFileLoader:
    """
    Load files idempotently using staging directory
    """
    
    def __init__(self, staging_dir, target_dir):
        self.staging_dir = staging_dir
        self.target_dir = target_dir
    
    def load_file(self, source_file, date):
        """
        Load file idempotently
        """
        # Step 1: Clear staging directory
        if os.path.exists(self.staging_dir):
            shutil.rmtree(self.staging_dir)
        os.makedirs(self.staging_dir)
        
        # Step 2: Copy to staging
        staging_file = os.path.join(self.staging_dir, os.path.basename(source_file))
        shutil.copy(source_file, staging_file)
        
        # Step 3: Process file in staging
        processed_data = self.process_file(staging_file)
        
        # Step 4: Atomically move to target
        target_file = os.path.join(self.target_dir, f'data_{date}.parquet')
        
        # Remove existing file if exists
        if os.path.exists(target_file):
            os.remove(target_file)
        
        # Save processed data
        processed_data.to_parquet(target_file)
        
        # Step 5: Cleanup staging
        shutil.rmtree(self.staging_dir)
        
        return target_file
    
    def process_file(self, file_path):
        """Process file (deterministic transformation)"""
        import pandas as pd
        df = pd.read_csv(file_path)
        # Deterministic processing
        return df.drop_duplicates()

# Usage: Safe to run multiple times
loader = IdempotentFileLoader('/tmp/staging', '/data/processed')
loader.load_file('source.csv', '2024-01-15')  # Run 1
loader.load_file('source.csv', '2024-01-15')  # Run 2 (same result)
```

---

## 10. Best Practices {#best-practices}

### ✅ DO

1. **Use UPSERT operations**
   ```sql
   INSERT ... ON CONFLICT DO UPDATE
   ```

2. **Generate deterministic IDs**
   ```python
   id = hash(user_id, event_type, timestamp)
   ```

3. **Delete before insert for full refreshes**
   ```python
   DELETE WHERE date = target_date
   INSERT INTO ... SELECT ...
   ```

4. **Track processed records**
   ```python
   if record_id not in processed_ids:
       process(record)
   ```

5. **Use transactional operations**
   ```python
   BEGIN TRANSACTION
   DELETE ...
   INSERT ...
   COMMIT
   ```

6. **Test idempotency explicitly**
   ```python
   assert run_pipeline(data) == run_pipeline(data)
   ```

7. **Avoid timestamps in output**
   ```python
   # Use source timestamp, not processing timestamp
   ```

8. **Document idempotency guarantees**
   ```python
   def process_data(date):
       """
       Idempotent: Can be run multiple times safely.
       Same date will produce same output.
       """
   ```

### ❌ DON'T

1. **Don't use auto-increment IDs**
2. **Don't append without deduplication**
3. **Don't use current timestamps**
4. **Don't rely on execution order**
5. **Don't accumulate state across runs**
6. **Don't skip testing idempotency**
7. **Don't ignore partial failures**
8. **Don't forget about concurrent execution**

---

## Quick Reference

### Idempotency Checklist

```
□ Operations use UPSERT or DELETE+INSERT
□ IDs are deterministic (no random UUIDs)
□ No current timestamps in output
□ State is tracked or cleared between runs
□ Tested with multiple executions
□ Safe for concurrent execution
□ Handles partial failures gracefully
□ External side effects are tracked
□ Documented as idempotent
□ Integrated with retry logic
```

### Common Patterns Summary

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| **Truncate & Load** | Daily refreshes | `DELETE WHERE date=X; INSERT SELECT` |
| **Upsert** | Incremental updates | `INSERT ON CONFLICT UPDATE` |
| **Deterministic IDs** | Event processing | `hash(key_fields)` |
| **State Tracking** | Stream processing | Track processed IDs in database |
| **Staging Tables** | Complex transforms | Temp table → atomic swap |
| **Checkpointing** | Incremental loads | Save last processed position |

---

## Additional Resources

### Related Documents

1. **[02-retries-and-backoff.md](./02-retries-and-backoff.md)** - Retry strategies for idempotent operations
2. **03-testing-strategies.md** - Comprehensive testing guide (coming soon)
3. **04-code-examples.md** - Complete working examples (coming soon)
4. **05-troubleshooting.md** - Common issues and solutions (coming soon)

### Further Reading

- **Martin Fowler**: Idempotent Receiver pattern
- **AWS**: Designing idempotent API operations
- **Google Cloud**: Best practices for idempotent operations
- **Apache Kafka**: Exactly-once semantics

---

## Summary

**Making pipelines idempotent is essential for:**
- ✅ Safe retries after failures
- ✅ Reliable backfills
- ✅ Simplified debugging
- ✅ Reduced operational burden
- ✅ Data consistency

**Key principles:**
1. Same input → Same output (deterministic)
2. Multiple executions = Single execution (idempotent)
3. Use UPSERT not INSERT (avoid duplicates)
4. Track what's been processed (state management)
5. Test with multiple runs (verify idempotency)

**Remember**: An hour spent making a pipeline idempotent saves weeks of debugging duplicate data issues!

---

**Document Status**: Complete ✅
**Project**: Data Ingestion Strategic Designs
**Path**: `make-pipelines-idempotent/`
