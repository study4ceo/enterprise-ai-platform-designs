"""
Load module - Load validated data into DuckDB.
Implements idempotent UPSERT logic to prevent duplicates.
"""
import logging
from pathlib import Path
from typing import Optional
import pandas as pd
import duckdb

from src.config import Config

logger = logging.getLogger(__name__)


class LoadError(Exception):
    """Raised when loading fails."""
    pass


def get_connection(db_path: str = Config.DB_PATH) -> duckdb.DuckDBPyConnection:
    """
    Create and return DuckDB connection.
    
    Args:
        db_path: Path to DuckDB database file
        
    Returns:
        DuckDB connection object
        
    Raises:
        LoadError: If connection fails
    """
    try:
        conn = duckdb.connect(db_path)
        logger.debug(f"Connected to DuckDB: {db_path}")
        return conn
    except Exception as e:
        raise LoadError(f"Failed to connect to DuckDB at {db_path}: {e}")


def create_table_if_not_exists(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Create orders_clean table with proper schema if it doesn't exist.
    
    Args:
        conn: DuckDB connection
        
    Raises:
        LoadError: If table creation fails
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS orders_clean (
        order_id VARCHAR PRIMARY KEY,
        customer_id VARCHAR NOT NULL,
        order_date DATE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        status VARCHAR NOT NULL,
        processed_at TIMESTAMP NOT NULL
    );
    """
    
    try:
        conn.execute(create_table_sql)
        logger.info("Table 'orders_clean' ready")
    except Exception as e:
        raise LoadError(f"Failed to create table: {e}")


def upsert_data(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> int:
    """
    Insert or update data in DuckDB (idempotent operation).
    Uses INSERT OR REPLACE to handle duplicates based on order_id.
    
    Args:
        conn: DuckDB connection
        df: DataFrame with validated and transformed data
        
    Returns:
        Number of rows affected
        
    Raises:
        LoadError: If upsert fails
    """
    if df.empty:
        logger.warning("No data to load (empty DataFrame)")
        return 0
    
    try:
        # Create a temporary table from the DataFrame
        conn.register('temp_orders', df)
        
        # Use INSERT OR REPLACE for idempotent behavior
        # This will update existing records and insert new ones
        upsert_sql = """
        INSERT OR REPLACE INTO orders_clean 
        SELECT 
            order_id,
            customer_id,
            order_date,
            amount,
            status,
            processed_at
        FROM temp_orders;
        """
        
        logger.info(f"Upserting {len(df)} rows into orders_clean")
        # Execute and complete the insert
        conn.sql(upsert_sql)
        
        # Unregister temp table
        try:
            conn.unregister('temp_orders')
        except:
            pass  # Ignore unregister errors
        
        # Get count of rows in table (after unregister)
        result = conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone()
        total_rows = result[0] if result else 0
        
        logger.info(f"✅ Upsert complete. Total rows in table: {total_rows}")
        
        return len(df)
        
    except Exception as e:
        # Try to clean up temp table
        try:
            conn.unregister('temp_orders')
        except:
            pass
        raise LoadError(f"Failed to upsert data: {e}")


def get_table_stats(conn: duckdb.DuckDBPyConnection) -> dict:
    """
    Get statistics about the orders_clean table.
    
    Args:
        conn: DuckDB connection
        
    Returns:
        Dictionary with table statistics
    """
    try:
        stats = {}
        
        # Total rows
        result = conn.execute("SELECT COUNT(*) FROM orders_clean").fetchone()
        stats['total_rows'] = result[0] if result else 0
        
        # Unique customers
        result = conn.execute("SELECT COUNT(DISTINCT customer_id) FROM orders_clean").fetchone()
        stats['unique_customers'] = result[0] if result else 0
        
        # Date range
        result = conn.execute(
            "SELECT MIN(order_date), MAX(order_date) FROM orders_clean"
        ).fetchone()
        if result:
            stats['min_date'] = str(result[0]) if result[0] else None
            stats['max_date'] = str(result[1]) if result[1] else None
        
        # Total amount
        result = conn.execute("SELECT SUM(amount) FROM orders_clean").fetchone()
        stats['total_amount'] = float(result[0]) if result and result[0] else 0.0
        
        # Status distribution
        rows = conn.execute(
            "SELECT status, COUNT(*) as count FROM orders_clean GROUP BY status"
        ).fetchall()
        stats['status_distribution'] = {row[0]: row[1] for row in rows}
        
        return stats
        
    except Exception as e:
        logger.warning(f"Failed to get table stats: {e}")
        return {}


def archive_processed_file(file_path: Path, 
                          archive_dir: Path = Config.PROCESSED_DATA_PATH) -> None:
    """
    Move processed CSV file to archive directory.
    
    Args:
        file_path: Path to processed CSV file
        archive_dir: Directory to move file to
        
    Raises:
        LoadError: If file move fails
    """
    try:
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique filename with timestamp if file exists
        dest_path = archive_dir / file_path.name
        if dest_path.exists():
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            stem = file_path.stem
            suffix = file_path.suffix
            dest_path = archive_dir / f"{stem}_{timestamp}{suffix}"
        
        file_path.rename(dest_path)
        logger.info(f"Archived: {file_path.name} -> {dest_path}")
        
    except Exception as e:
        raise LoadError(f"Failed to archive file {file_path}: {e}")


def load_data(df: pd.DataFrame, 
              archive_files: bool = True,
              db_path: str = Config.DB_PATH) -> dict:
    """
    Load validated data into DuckDB and optionally archive source files.
    
    Args:
        df: Validated and transformed DataFrame
        archive_files: Whether to archive processed CSV files
        db_path: Path to DuckDB database
        
    Returns:
        Dictionary with load results and statistics
        
    Raises:
        LoadError: If loading fails
    """
    logger.info("Starting data load")
    
    if df.empty:
        logger.warning("No data to load")
        return {"rows_loaded": 0, "status": "empty"}
    
    conn = None
    try:
        # Connect to DuckDB
        conn = get_connection(db_path)
        
        # Ensure table exists
        create_table_if_not_exists(conn)
        
        # Upsert data (idempotent)
        rows_loaded = upsert_data(conn, df)
        
        # Get table statistics
        stats = get_table_stats(conn)
        
        # Archive processed files if requested
        if archive_files:
            csv_files = list(Config.RAW_DATA_PATH.glob("*.csv"))
            for csv_file in csv_files:
                try:
                    archive_processed_file(csv_file)
                except LoadError as e:
                    logger.error(f"Archive failed but data loaded: {e}")
        
        result = {
            "rows_loaded": rows_loaded,
            "status": "success",
            "table_stats": stats
        }
        
        logger.info(f"✅ Load complete: {rows_loaded} rows loaded")
        return result
        
    except Exception as e:
        logger.error(f"Load failed: {e}")
        raise LoadError(f"Failed to load data: {e}")
        
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")
