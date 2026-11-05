"""
Transform module - Clean and standardize data.
Applies type conversions, handles missing values, and business logic.
"""
import logging
from typing import Any
import pandas as pd
from datetime import datetime

from src.config import Config

logger = logging.getLogger(__name__)


class TransformationError(Exception):
    """Raised when transformation fails."""
    pass


def clean_string_column(series: pd.Series) -> pd.Series:
    """
    Clean string column by stripping whitespace and handling nulls.
    
    Args:
        series: Pandas Series to clean
        
    Returns:
        Cleaned Series
    """
    return series.astype(str).str.strip()


def parse_date(series: pd.Series) -> pd.Series:
    """
    Parse date column to datetime, handling multiple formats.
    
    Args:
        series: Series containing date strings
        
    Returns:
        Series with datetime type
        
    Raises:
        TransformationError: If dates cannot be parsed
    """
    try:
        # Fill NaN with empty string, convert to string
        cleaned = series.fillna('').astype(str)
        
        # Replace empty strings back to NaN for proper parsing
        cleaned = cleaned.replace('', pd.NA)
        cleaned = cleaned.replace('nan', pd.NA)
        
        # Try multiple date formats
        parsed = pd.to_datetime(cleaned, errors='coerce')
        
        # Check if any dates failed to parse
        null_count = parsed.isna().sum()
        original_null_count = series.isna().sum()
        
        if null_count > original_null_count:
            failed_count = null_count - original_null_count
            logger.warning(f"Failed to parse {failed_count} date values")
            # Show which values failed
            failed_indices = parsed.isna() & ~series.isna()
            if failed_indices.any():
                logger.warning(f"Failed values: {series[failed_indices].tolist()[:5]}")
        
        return parsed
        
    except Exception as e:
        raise TransformationError(f"Failed to parse dates: {e}")


def clean_amount(series: pd.Series) -> pd.Series:
    """
    Clean and convert amount column to float.
    Removes currency symbols and handles formatting.
    
    Args:
        series: Series containing amount values
        
    Returns:
        Series with float type
        
    Raises:
        TransformationError: If amounts cannot be converted
    """
    try:
        # Convert to string first (handle any type)
        cleaned = series.fillna('').astype(str)
        
        # Remove common currency symbols and commas
        cleaned = cleaned.str.replace('$', '', regex=False)
        cleaned = cleaned.str.replace('€', '', regex=False)
        cleaned = cleaned.str.replace('£', '', regex=False)
        cleaned = cleaned.str.replace(',', '', regex=False)
        cleaned = cleaned.str.replace(' ', '', regex=False)  # Remove spaces
        cleaned = cleaned.str.strip()
        
        # Replace empty strings with NaN
        cleaned = cleaned.replace('', pd.NA)
        cleaned = cleaned.replace('nan', pd.NA)
        
        # Convert to float
        result = pd.to_numeric(cleaned, errors='coerce')
        
        # Check for conversion failures
        null_count = result.isna().sum()
        original_null_count = series.isna().sum()
        
        if null_count > original_null_count:
            failed_count = null_count - original_null_count
            logger.warning(f"Failed to convert {failed_count} amount values to numeric")
            # Show which values failed
            failed_indices = result.isna() & ~series.isna()
            if failed_indices.any():
                logger.warning(f"Failed values: {series[failed_indices].tolist()[:5]}")
        
        return result
        
    except Exception as e:
        raise TransformationError(f"Failed to clean amount column: {e}")


def standardize_status(series: pd.Series) -> pd.Series:
    """
    Standardize status values to lowercase and strip whitespace.
    
    Args:
        series: Series containing status values
        
    Returns:
        Series with standardized status values
    """
    return series.astype(str).str.strip().str.lower()


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all transformations to the DataFrame.
    
    Transformations applied:
    - Clean string columns (order_id, customer_id)
    - Parse order_date to datetime
    - Clean and convert amount to float
    - Standardize status to lowercase
    - Add processed_at timestamp
    
    Args:
        df: Raw DataFrame from extraction
        
    Returns:
        Transformed DataFrame
        
    Raises:
        TransformationError: If transformation fails
    """
    logger.info("Starting data transformation")
    
    if df.empty:
        logger.warning("Received empty DataFrame for transformation")
        return df
    
    df_transformed = df.copy()
    
    try:
        # Clean string columns
        logger.debug("Cleaning order_id and customer_id")
        df_transformed['order_id'] = clean_string_column(df_transformed['order_id'])
        df_transformed['customer_id'] = clean_string_column(df_transformed['customer_id'])
        
        # Parse dates
        logger.debug("Parsing order_date")
        df_transformed['order_date'] = parse_date(df_transformed['order_date'])
        
        # Clean amounts
        logger.debug("Cleaning amount column")
        df_transformed['amount'] = clean_amount(df_transformed['amount'])
        
        # Standardize status
        logger.debug("Standardizing status values")
        df_transformed['status'] = standardize_status(df_transformed['status'])
        
        # Add processing timestamp
        df_transformed['processed_at'] = datetime.now()
        
        # Log transformation summary
        logger.info(f"Transformation complete. Rows: {len(df_transformed)}")
        logger.debug(f"Data types after transformation:\n{df_transformed.dtypes}")
        
        return df_transformed
        
    except Exception as e:
        raise TransformationError(f"Transformation failed: {e}")
