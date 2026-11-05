"""
Validate module - Ensure data quality before loading.
Fails loudly if any validation rule fails.
"""
import logging
from typing import List, Dict, Any
import pandas as pd

from src.config import Config

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails. Pipeline must stop."""
    pass


def check_required_columns(df: pd.DataFrame) -> None:
    """
    Verify all required columns are present.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If required columns are missing
    """
    missing_columns = [col for col in Config.REQUIRED_COLUMNS if col not in df.columns]
    
    if missing_columns:
        raise ValidationError(
            f"Missing required columns: {missing_columns}. "
            f"Available columns: {df.columns.tolist()}"
        )
    
    logger.debug("✓ All required columns present")


def check_for_nulls(df: pd.DataFrame) -> None:
    """
    Check for null values in required columns.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If nulls found in required columns
    """
    null_counts = df[Config.REQUIRED_COLUMNS].isnull().sum()
    columns_with_nulls = null_counts[null_counts > 0]
    
    if not columns_with_nulls.empty:
        null_info = columns_with_nulls.to_dict()
        raise ValidationError(
            f"Null values found in required columns: {null_info}. "
            "Cannot load incomplete data."
        )
    
    logger.debug("✓ No null values in required columns")


def check_duplicate_order_ids(df: pd.DataFrame) -> None:
    """
    Check for duplicate order_ids within the batch.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If duplicate order_ids found
    """
    duplicates = df[df['order_id'].duplicated(keep=False)]
    
    if not duplicates.empty:
        duplicate_ids = duplicates['order_id'].unique().tolist()
        raise ValidationError(
            f"Duplicate order_ids found in batch: {duplicate_ids[:10]}... "
            f"({len(duplicate_ids)} total). Each order_id must be unique."
        )
    
    logger.debug("✓ No duplicate order_ids in batch")


def check_data_types(df: pd.DataFrame) -> None:
    """
    Verify correct data types for each column.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If data types are incorrect
    """
    type_errors = []
    
    # Check order_id is string-like
    if not pd.api.types.is_string_dtype(df['order_id']) and not pd.api.types.is_object_dtype(df['order_id']):
        type_errors.append("order_id must be string type")
    
    # Check customer_id is string-like
    if not pd.api.types.is_string_dtype(df['customer_id']) and not pd.api.types.is_object_dtype(df['customer_id']):
        type_errors.append("customer_id must be string type")
    
    # Check order_date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
        type_errors.append(f"order_date must be datetime type, got {df['order_date'].dtype}")
    
    # Check amount is numeric
    if not pd.api.types.is_numeric_dtype(df['amount']):
        type_errors.append(f"amount must be numeric type, got {df['amount'].dtype}")
    
    # Check status is string-like
    if not pd.api.types.is_string_dtype(df['status']) and not pd.api.types.is_object_dtype(df['status']):
        type_errors.append("status must be string type")
    
    if type_errors:
        raise ValidationError(f"Data type validation failed: {'; '.join(type_errors)}")
    
    logger.debug("✓ All columns have correct data types")


def check_amount_values(df: pd.DataFrame) -> None:
    """
    Validate amount column values.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If invalid amounts found
    """
    # Check for negative amounts
    negative_amounts = df[df['amount'] < Config.MIN_AMOUNT]
    
    if not negative_amounts.empty:
        count = len(negative_amounts)
        examples = negative_amounts[['order_id', 'amount']].head(5).to_dict('records')
        raise ValidationError(
            f"Found {count} orders with amount < {Config.MIN_AMOUNT}. "
            f"Examples: {examples}"
        )
    
    # Check for unreasonably large amounts (optional warning)
    very_large = df[df['amount'] > 1_000_000]
    if not very_large.empty:
        logger.warning(
            f"Found {len(very_large)} orders with amount > $1,000,000. "
            "Please verify these are correct."
        )
    
    logger.debug(f"✓ All amounts >= {Config.MIN_AMOUNT}")


def check_status_values(df: pd.DataFrame) -> None:
    """
    Validate status column values against allowed values.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If invalid status values found
    """
    invalid_statuses = df[~df['status'].isin(Config.VALID_STATUSES)]
    
    if not invalid_statuses.empty:
        invalid_values = invalid_statuses['status'].unique().tolist()
        count = len(invalid_statuses)
        raise ValidationError(
            f"Found {count} orders with invalid status. "
            f"Invalid values: {invalid_values}. "
            f"Valid values are: {Config.VALID_STATUSES}"
        )
    
    logger.debug(f"✓ All status values valid: {Config.VALID_STATUSES}")


def check_date_range(df: pd.DataFrame) -> None:
    """
    Validate order_date values are reasonable.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If dates are unreasonable
    """
    min_date = df['order_date'].min()
    max_date = df['order_date'].max()
    
    # Check dates aren't in the future
    now = pd.Timestamp.now()
    future_dates = df[df['order_date'] > now]
    
    if not future_dates.empty:
        count = len(future_dates)
        examples = future_dates[['order_id', 'order_date']].head(3).to_dict('records')
        raise ValidationError(
            f"Found {count} orders with future dates. Examples: {examples}"
        )
    
    # Check dates aren't too old (optional warning)
    very_old = pd.Timestamp.now() - pd.Timedelta(days=365*10)  # 10 years
    old_dates = df[df['order_date'] < very_old]
    
    if not old_dates.empty:
        logger.warning(
            f"Found {len(old_dates)} orders older than 10 years. "
            "Please verify these are correct."
        )
    
    logger.debug(f"✓ Date range valid: {min_date.date()} to {max_date.date()}")


def validate_data(df: pd.DataFrame) -> None:
    """
    Run all validation checks on the DataFrame.
    Raises ValidationError immediately if any check fails.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If any validation fails
    """
    logger.info("Starting data validation")
    
    if df.empty:
        raise ValidationError("Cannot validate empty DataFrame")
    
    # Run all validation checks
    validation_checks = [
        ("Required Columns", check_required_columns),
        ("Null Values", check_for_nulls),
        ("Duplicate IDs", check_duplicate_order_ids),
        ("Data Types", check_data_types),
        ("Amount Values", check_amount_values),
        ("Status Values", check_status_values),
        ("Date Range", check_date_range),
    ]
    
    for check_name, check_func in validation_checks:
        try:
            check_func(df)
        except ValidationError as e:
            logger.error(f"❌ Validation failed: {check_name}")
            raise
    
    # All validations passed
    logger.info(f"✅ All validations passed. {len(df)} rows ready for loading.")


def get_validation_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a summary of the data for logging purposes.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {"status": "empty", "row_count": 0}
    
    summary = {
        "row_count": len(df),
        "unique_orders": df['order_id'].nunique(),
        "unique_customers": df['customer_id'].nunique(),
        "date_range": {
            "min": df['order_date'].min().strftime('%Y-%m-%d'),
            "max": df['order_date'].max().strftime('%Y-%m-%d')
        },
        "amount_stats": {
            "min": float(df['amount'].min()),
            "max": float(df['amount'].max()),
            "mean": float(df['amount'].mean()),
            "total": float(df['amount'].sum())
        },
        "status_distribution": df['status'].value_counts().to_dict()
    }
    
    return summary
