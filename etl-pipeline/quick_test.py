"""
Quick test script - runs pipeline once and shows results.
"""

import logging
import sys
from pathlib import Path
import duckdb

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from pipeline import run_pipeline

# Simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Run pipeline and display results."""
    print("=" * 60)
    print("ETL PIPELINE QUICK TEST")
    print("=" * 60)
    
    # Run pipeline
    print("\n1. Running pipeline...")
    try:
        run_pipeline()
        print("✓ Pipeline completed successfully")
    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        sys.exit(1)
    
    # Query results
    print("\n2. Querying results...")
    conn = duckdb.connect(Config.DB_PATH)
    
    try:
        # Count
        total = conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone()[0]
        print(f"   Total records: {total}")
        
        # By status
        print("\n   Records by status:")
        for row in conn.execute(
            "SELECT status, COUNT(*) FROM orders_clean "
            "GROUP BY status ORDER BY status"
        ).fetchall():
            print(f"     {row[0]}: {row[1]}")
        
        # Date range
        print("\n   Date range:")
        dates = conn.execute(
            "SELECT MIN(order_date), MAX(order_date) FROM orders_clean"
        ).fetchone()
        print(f"     From {dates[0]} to {dates[1]}")
        
        # Amount summary
        print("\n   Amount summary:")
        stats = conn.execute(
            "SELECT MIN(amount), MAX(amount), AVG(amount), SUM(amount) "
            "FROM orders_clean"
        ).fetchone()
        print(f"     Min: ${stats[0]:.2f}")
        print(f"     Max: ${stats[1]:.2f}")
        print(f"     Avg: ${stats[2]:.2f}")
        print(f"     Total: ${stats[3]:.2f}")
        
        # Sample records
        print("\n   Sample records:")
        for row in conn.execute(
            "SELECT order_id, customer_id, order_date, amount, status "
            "FROM orders_clean ORDER BY order_date DESC LIMIT 3"
        ).fetchall():
            print(f"     {row}")
        
        print("\n" + "=" * 60)
        print("✓ TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
