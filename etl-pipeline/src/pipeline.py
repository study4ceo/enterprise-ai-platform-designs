"""
Pipeline orchestration - Coordinate ETL workflow.
Manages the flow from extract through load with proper error handling.
"""
import logging
from typing import Dict, Any
import pandas as pd

from src.extract import extract_all, ExtractionError
from src.transform import transform_data, TransformationError
from src.validate import validate_data, get_validation_summary, ValidationError
from src.load import load_data, LoadError
from src.config import Config

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when pipeline execution fails."""
    pass


def run_pipeline(archive_files: bool = True) -> Dict[str, Any]:
    """
    Execute the complete ETL pipeline.
    
    Pipeline stages:
    1. Extract: Read CSV files from raw directory
    2. Transform: Clean and standardize data
    3. Validate: Check data quality (fails loudly on errors)
    4. Load: Insert/update data in DuckDB (idempotent)
    
    Args:
        archive_files: Whether to archive processed files after loading
        
    Returns:
        Dictionary with pipeline results and statistics
        
    Raises:
        PipelineError: If any stage fails
    """
    logger.info("=" * 60)
    logger.info("Starting ETL Pipeline")
    logger.info("=" * 60)
    
    pipeline_result = {
        "status": "running",
        "stages_completed": [],
        "error": None
    }
    
    try:
        # ==================== EXTRACT ====================
        logger.info("\n[1/4] EXTRACT: Reading CSV files")
        logger.info("-" * 60)
        
        try:
            df_raw = extract_all()
            pipeline_result["stages_completed"].append("extract")
            pipeline_result["rows_extracted"] = len(df_raw)
            logger.info(f"✓ Extract complete: {len(df_raw)} rows")
            
        except ExtractionError as e:
            raise PipelineError(f"Extraction failed: {e}")
        
        # ==================== TRANSFORM ====================
        logger.info("\n[2/4] TRANSFORM: Cleaning and standardizing data")
        logger.info("-" * 60)
        
        try:
            df_transformed = transform_data(df_raw)
            pipeline_result["stages_completed"].append("transform")
            logger.info(f"✓ Transform complete: {len(df_transformed)} rows")
            
        except TransformationError as e:
            raise PipelineError(f"Transformation failed: {e}")
        
        # ==================== VALIDATE ====================
        logger.info("\n[3/4] VALIDATE: Checking data quality")
        logger.info("-" * 60)
        
        try:
            # Get summary before validation
            summary = get_validation_summary(df_transformed)
            logger.info(f"Data summary: {summary}")
            
            # Run validation (fails loudly on errors)
            validate_data(df_transformed)
            
            pipeline_result["stages_completed"].append("validate")
            pipeline_result["validation_summary"] = summary
            logger.info("✓ Validation complete: All checks passed")
            
        except ValidationError as e:
            # Validation failed - DO NOT LOAD DATA
            logger.error(f"❌ VALIDATION FAILED: {e}")
            raise PipelineError(f"Validation failed: {e}")
        
        # ==================== LOAD ====================
        logger.info("\n[4/4] LOAD: Writing to DuckDB")
        logger.info("-" * 60)
        
        try:
            load_result = load_data(df_transformed, archive_files=archive_files)
            pipeline_result["stages_completed"].append("load")
            pipeline_result["load_result"] = load_result
            logger.info(f"✓ Load complete: {load_result.get('rows_loaded', 0)} rows")
            
        except LoadError as e:
            raise PipelineError(f"Load failed: {e}")
        
        # ==================== SUCCESS ====================
        pipeline_result["status"] = "success"
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Stages: {' → '.join(pipeline_result['stages_completed'])}")
        logger.info(f"Rows processed: {pipeline_result.get('rows_extracted', 0)}")
        logger.info(f"Rows loaded: {load_result.get('rows_loaded', 0)}")
        
        if load_result.get('table_stats'):
            stats = load_result['table_stats']
            logger.info(f"Total rows in database: {stats.get('total_rows', 0)}")
            logger.info(f"Total amount: ${stats.get('total_amount', 0):,.2f}")
        
        logger.info("=" * 60)
        
        return pipeline_result
        
    except PipelineError as e:
        pipeline_result["status"] = "failed"
        pipeline_result["error"] = str(e)
        
        logger.error("\n" + "=" * 60)
        logger.error("❌ PIPELINE FAILED")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        logger.error(f"Stages completed: {pipeline_result['stages_completed']}")
        logger.error("=" * 60)
        
        raise
    
    except Exception as e:
        pipeline_result["status"] = "failed"
        pipeline_result["error"] = str(e)
        
        logger.error("\n" + "=" * 60)
        logger.error("❌ UNEXPECTED ERROR")
        logger.error("=" * 60)
        logger.error(f"Error: {e}", exc_info=True)
        logger.error("=" * 60)
        
        raise PipelineError(f"Unexpected error: {e}")


def verify_database() -> Dict[str, Any]:
    """
    Verify the database state and return statistics.
    Useful for checking pipeline results.
    
    Returns:
        Dictionary with database statistics
    """
    from src.load import get_connection, get_table_stats
    
    try:
        conn = get_connection()
        
        # Check if table exists
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orders_clean'"
        ).fetchall()
        
        if not result:
            return {"exists": False, "message": "Table 'orders_clean' does not exist"}
        
        stats = get_table_stats(conn)
        stats["exists"] = True
        
        conn.close()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to verify database: {e}")
        return {"error": str(e)}
