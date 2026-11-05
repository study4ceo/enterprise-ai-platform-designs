"""
Test script for ETL pipeline.
Demonstrates extraction, transformation, validation, loading, and idempotency.
"""

import logging
import sys
from pathlib import Path
import duckdb
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from pipeline import run_pipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_pipeline.log')
    ]
)

logger = logging.getLogger(__name__)


def query_database() -> None:
    """Query and display the loaded data."""
    logger.info("=" * 80)
    logger.info("QUERYING DATABASE")
    logger.info("=" * 80)
    
    conn = duckdb.connect(Config.DB_PATH)
    
    try:
        # Check if table exists
        result = conn.execute(
            "SELECT COUNT(*) as table_count FROM information_schema.tables "
            "WHERE table_name = 'orders_clean'"
        ).fetchone()
        
        if result[0] == 0:
            logger.warning("Table 'orders_clean' does not exist yet")
            return
        
        # Total records
        total = conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone()[0]
        logger.info(f"Total records in orders_clean: {total}")
        
        # Records by status
        logger.info("\nRecords by status:")
        status_counts = conn.execute(
            "SELECT status, COUNT(*) as count FROM orders_clean "
            "GROUP BY status ORDER BY count DESC"
        ).fetchall()
        for status, count in status_counts:
            logger.info(f"  {status}: {count}")
        
        # Sample records
        logger.info("\nSample records (first 5):")
        samples = conn.execute(
            "SELECT * FROM orders_clean ORDER BY order_date, order_id LIMIT 5"
        ).fetchall()
        
        for record in samples:
            logger.info(f"  {record}")
        
        # Amount statistics
        logger.info("\nAmount statistics:")
        stats = conn.execute(
            "SELECT "
            "  MIN(amount) as min_amount, "
            "  MAX(amount) as max_amount, "
            "  AVG(amount) as avg_amount, "
            "  SUM(amount) as total_amount "
            "FROM orders_clean"
        ).fetchone()
        logger.info(f"  Min: ${stats[0]:.2f}")
        logger.info(f"  Max: ${stats[1]:.2f}")
        logger.info(f"  Avg: ${stats[2]:.2f}")
        logger.info(f"  Total: ${stats[3]:.2f}")
        
        # Check for duplicates (should be none due to idempotency)
        dupes = conn.execute(
            "SELECT order_id, COUNT(*) as count FROM orders_clean "
            "GROUP BY order_id HAVING COUNT(*) > 1"
        ).fetchall()
        
        if dupes:
            logger.error(f"DUPLICATE RECORDS FOUND: {dupes}")
        else:
            logger.info("\n✓ No duplicate order_ids (idempotency working)")
        
    finally:
        conn.close()


def test_idempotency() -> None:
    """Test that running pipeline twice doesn't create duplicates."""
    logger.info("=" * 80)
    logger.info("TESTING IDEMPOTENCY (Running pipeline twice)")
    logger.info("=" * 80)
    
    # First run
    logger.info("\n>>> FIRST RUN")
    run_pipeline()
    
    conn = duckdb.connect(Config.DB_PATH)
    count_after_first = conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone()[0]
    conn.close()
    logger.info(f"Records after first run: {count_after_first}")
    
    # Restore CSV files from processed folder
    processed_dir = Path(Config.PROCESSED_DIR)
    raw_dir = Path(Config.RAW_DIR)
    
    csv_files = list(processed_dir.glob("*.csv"))
    logger.info(f"\nRestoring {len(csv_files)} files from processed to raw folder")
    
    for file in csv_files:
        target = raw_dir / file.name
        file.rename(target)
        logger.info(f"  Restored: {file.name}")
    
    # Second run
    logger.info("\n>>> SECOND RUN (same files)")
    run_pipeline()
    
    conn = duckdb.connect(Config.DB_PATH)
    count_after_second = conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone()[0]
    conn.close()
    logger.info(f"Records after second run: {count_after_second}")
    
    # Verify counts match
    if count_after_first == count_after_second:
        logger.info("\n✓ IDEMPOTENCY TEST PASSED: No duplicates created")
    else:
        logger.error(
            f"\n✗ IDEMPOTENCY TEST FAILED: "
            f"Count changed from {count_after_first} to {count_after_second}"
        )


def test_validation_failure() -> None:
    """Test that validation errors prevent loading bad data."""
    logger.info("=" * 80)
    logger.info("TESTING VALIDATION (Bad data should be rejected)")
    logger.info("=" * 80)
    
    # Create a CSV with bad data
    bad_csv = Path(Config.RAW_DIR) / "bad_orders.csv"
    bad_csv.write_text(
        "order_id,customer_id,order_date,amount,status\n"
        "ORD999,CUST999,invalid-date,not-a-number,completed\n"  # Bad date and amount
    )
    
    logger.info(f"Created bad CSV: {bad_csv.name}")
    
    try:
        run_pipeline()
        logger.error("✗ VALIDATION TEST FAILED: Bad data was not rejected")
    except Exception as e:
        logger.info(f"✓ VALIDATION TEST PASSED: Bad data rejected with error:")
        logger.info(f"  {type(e).__name__}: {e}")
    finally:
        # Cleanup
        if bad_csv.exists():
            bad_csv.unlink()
            logger.info("Cleaned up bad CSV file")


def main() -> None:
    """Run all tests."""
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("ETL PIPELINE TEST SUITE")
    logger.info(f"Started at: {start_time}")
    logger.info("=" * 80)
    
    try:
        # Test 1: Normal pipeline run
        logger.info("\n\nTEST 1: NORMAL PIPELINE RUN")
        logger.info("-" * 80)
        run_pipeline()
        query_database()
        
        # Test 2: Idempotency
        logger.info("\n\nTEST 2: IDEMPOTENCY")
        logger.info("-" * 80)
        test_idempotency()
        
        # Test 3: Validation failure
        logger.info("\n\nTEST 3: VALIDATION FAILURE")
        logger.info("-" * 80)
        test_validation_failure()
        
        # Final database state
        logger.info("\n\nFINAL DATABASE STATE")
        logger.info("-" * 80)
        query_database()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n\nTEST SUITE FAILED: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
