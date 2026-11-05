"""
Extract module - Read CSV files and standardize column names.
Handles CSV files with varying column naming conventions.
"""
import logging
from pathlib import Path
from typing import List, Optional
import pandas as pd

from src.config import Config

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Raised when extraction fails."""
    pass


def find_csv_files(directory: Path) -> List[Path]:
    """
    Find all CSV files in the specified directory.
    
    Args:
        directory: Path to search for CSV files
        
    Returns:
        List of Path objects for CSV files
        
    Raises:
        ExtractionError: If directory doesn't exist or no files found
    """
    if not directory.exists():
        raise ExtractionError(f"Directory does not exist: {directory}")
    
    csv_files = list(directory.glob("*.csv"))
    
    if not csv_files:
        raise ExtractionError(f"No CSV files found in {directory}")
    
    logger.info(f"Found {len(csv_files)} CSV file(s): {[f.name for f in csv_files]}")
    return csv_files


def map_column_name(df_columns: List[str], target_column: str) -> Optional[str]:
    """
    Map a column name from CSV to standard name using Config.COLUMN_MAPPING.
    
    Args:
        df_columns: List of actual column names in DataFrame
        target_column: Target standard column name (e.g., 'order_id')
        
    Returns:
        Actual column name from DataFrame that matches, or None if not found
    """
    possible_names = Config.COLUMN_MAPPING.get(target_column, [])
    
    for possible_name in possible_names:
        if possible_name in df_columns:
            logger.debug(f"Mapped '{possible_name}' -> '{target_column}'")
            return possible_name
    
    return None


def extract_from_csv(file_path: Path) -> pd.DataFrame:
    """
    Extract data from a single CSV file.
    Maps varying column names to standard names and selects required columns.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        DataFrame with standardized column names
        
    Raises:
        ExtractionError: If file cannot be read or required columns missing
    """
    logger.info(f"Extracting data from: {file_path.name}")
    
    try:
        df = pd.read_csv(file_path)
        logger.debug(f"Read {len(df)} rows from {file_path.name}")
        logger.debug(f"Original columns: {df.columns.tolist()}")
        
    except Exception as e:
        raise ExtractionError(f"Failed to read CSV file {file_path}: {e}")
    
    # Map columns to standard names
    column_mapping = {}
    missing_columns = []
    
    for target_col in Config.REQUIRED_COLUMNS:
        actual_col = map_column_name(df.columns.tolist(), target_col)
        
        if actual_col:
            column_mapping[actual_col] = target_col
        else:
            missing_columns.append(target_col)
    
    if missing_columns:
        raise ExtractionError(
            f"Required columns not found in {file_path.name}: {missing_columns}. "
            f"Available columns: {df.columns.tolist()}"
        )
    
    # Select and rename columns
    df_selected = df[list(column_mapping.keys())].copy()
    df_selected.rename(columns=column_mapping, inplace=True)
    
    logger.info(f"Extracted {len(df_selected)} rows with columns: {df_selected.columns.tolist()}")
    
    return df_selected


def extract_all(directory: Path = Config.RAW_DATA_PATH) -> pd.DataFrame:
    """
    Extract and combine data from all CSV files in directory.
    
    Args:
        directory: Directory containing CSV files (default: from Config)
        
    Returns:
        Combined DataFrame from all CSV files
        
    Raises:
        ExtractionError: If extraction fails
    """
    logger.info(f"Starting extraction from {directory}")
    
    csv_files = find_csv_files(directory)
    
    dataframes = []
    for csv_file in csv_files:
        try:
            df = extract_from_csv(csv_file)
            dataframes.append(df)
        except ExtractionError as e:
            logger.error(f"Failed to extract {csv_file.name}: {e}")
            raise
    
    # Combine all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Total rows extracted: {len(combined_df)}")
    
    return combined_df
