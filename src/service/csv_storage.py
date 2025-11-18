"""CSV storage abstraction for reading/writing CSV files from cloud or local storage."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from src.service.cloudflare import (
    CLOUD_STORAGE_ENABLED,
    file_exists_in_cloud,
    read_csv_from_cloud,
    write_csv_to_cloud,
)


def _get_cloud_path(local_path: Path) -> str:
    """Get cloud path from local path.
    
    Args:
        local_path: Local file path
        
    Returns:
        Cloud storage path
    """
    # Use just filename (stored at bucket root)
    return local_path.name


def read_csv(cloud_path: str | None, local_path: Path) -> pd.DataFrame | None:
    """Read CSV file from cloud (if available) or local storage.
    
    Priority: Cloud > Local
    
    Args:
        cloud_path: Cloud storage path (if None, uses local_path.name)
        local_path: Local file path
        
    Returns:
        DataFrame if successful, None otherwise
    """
    # Try cloud first if enabled
    if CLOUD_STORAGE_ENABLED:
        cloud_key = cloud_path or _get_cloud_path(local_path)
        df = read_csv_from_cloud(cloud_key)
        if df is not None:
            return df
    
    # Fallback to local
    if local_path.exists():
        try:
            return pd.read_csv(local_path)
        except Exception:
            return None
    
    return None


def write_csv(df: pd.DataFrame, cloud_path: str | None, local_path: Path) -> bool:
    """Write DataFrame to CSV file in cloud (if enabled) and local storage.
    
    Args:
        df: DataFrame to write
        cloud_path: Cloud storage path (if None, uses local_path.name)
        local_path: Local file path
        
    Returns:
        True if at least one write succeeded, False otherwise
    """
    success = False
    
    # Write to cloud if enabled
    if CLOUD_STORAGE_ENABLED:
        cloud_key = cloud_path or _get_cloud_path(local_path)
        if write_csv_to_cloud(df, cloud_key):
            success = True
    
    # Always write to local (fallback)
    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(local_path, index=False)
        success = True
    except Exception:
        pass
    
    return success


def get_last_date_from_csv(cloud_path: str | None, local_path: Path) -> datetime | None:
    """Get the last report date from CSV file (cloud or local).
    
    Args:
        cloud_path: Cloud storage path (if None, uses local_path.name)
        local_path: Local file path
        
    Returns:
        Last report date as datetime, or None if CSV doesn't exist or is empty
    """
    df = read_csv(cloud_path, local_path)
    if df is None or df.empty:
        return None
    
    if 'Report_Date' not in df.columns:
        return None
    
    try:
        df['Report_Date'] = pd.to_datetime(df['Report_Date'])
        last_date = df['Report_Date'].max()
        return last_date.to_pydatetime() if pd.notna(last_date) else None
    except Exception:
        return None


def csv_exists(cloud_path: str | None, local_path: Path) -> bool:
    """Check if CSV file exists in cloud or local storage.
    
    Args:
        cloud_path: Cloud storage path (if None, uses local_path.name)
        local_path: Local file path
        
    Returns:
        True if file exists, False otherwise
    """
    # Check cloud first if enabled
    if CLOUD_STORAGE_ENABLED:
        cloud_key = cloud_path or _get_cloud_path(local_path)
        if file_exists_in_cloud(cloud_key):
            return True
    
    # Check local
    return local_path.exists()

