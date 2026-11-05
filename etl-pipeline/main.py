"""
Main entry point for ETL pipeline.
Run this script to execute the complete pipeline.
"""
import logging
import sys
from pathlib import Path

from src.config import Config
from src.pipeline import run_pipeline, verify_database, PipelineError


def setup_logging() -> None:
    """Configure logging for the application."""
    # Create logs directory
    Config.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(Config.LOG_PATH, mode='a')
        ]
    )
    
    # Set library loggers to WARNING to reduce noise
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('duckdb').setLevel(logging.WARNING)


def main() -> int:
    """
    Main execution function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("ETL Pipeline Started")
        logger.info(f"Configuration:")
        logger.info(f"  Raw data path: {Config.RAW_DATA_PATH}")
        logger.info(f"  Database path: {Config.DB_PATH}")
        logger.info(f"  Log level: {Config.LOG_LEVEL}")
        
        # Run the pipeline
        result = run_pipeline(archive_files=True)
        
        # Verify final state
        logger.info("\nVerifying database state...")
        db_stats = verify_database()
        
        if db_stats.get("exists"):
            logger.info(f"Database verification successful:")
            logger.info(f"  Total rows: {db_stats.get('total_rows', 0)}")
            logger.info(f"  Unique customers: {db_stats.get('unique_customers', 0)}")
            logger.info(f"  Date range: {db_stats.get('min_date')} to {db_stats.get('max_date')}")
            logger.info(f"  Total amount: ${db_stats.get('total_amount', 0):,.2f}")
        
        logger.info("\n✅ Pipeline completed successfully!")
        return 0
        
    except PipelineError as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        logger.error("Check the log file for details.")
        return 1
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
