"""Field type detection and analysis utilities."""

import re
from datetime import datetime
from typing import Any, List, Optional, Union

import numpy as np
import pandas as pd

from .models import FieldType


class FieldTypeDetector:
    """Detects the type of data in a pandas Series."""
    
    def __init__(self, categorical_threshold: float = 0.1) -> None:
        """
        Initialize the field type detector.
        
        Args:
            categorical_threshold: Maximum ratio of unique values to total values
                                 for a field to be considered categorical
        """
        self.categorical_threshold = categorical_threshold
    
    def detect_field_type(self, series: pd.Series) -> FieldType:
        """
        Detect the type of data in a pandas Series.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Detected FieldType
        """
        # Remove NaN values for analysis
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return FieldType.UNKNOWN
        
        # Check for ID type first (this should override other detections)
        if self._is_id_field(series):
            return FieldType.ID
        
        # Check for boolean type
        if self._is_boolean(series):
            return FieldType.BOOLEAN
        
        # Check for datetime type
        if self._is_datetime(series):
            return FieldType.DATETIME
        
        # Check for integer type
        if self._is_integer(series):
            return FieldType.INTEGER
        
        # Check for float type
        if self._is_float(series):
            return FieldType.FLOAT
        
        # Check for categorical type
        if self._is_categorical(series):
            return FieldType.CATEGORICAL
        
        # Default to string
        return FieldType.STRING
    
    def _is_id_field(self, series: pd.Series) -> bool:
        """
        Check if a field is an identifier column.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            True if the field appears to be an ID column
        """
        column_name = series.name.lower()
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return False
        
        # Check column name patterns that suggest ID fields
        id_patterns = [
            r'^id$',           # exact match for 'id'
            r'^.*_id$',        # ends with '_id'
            r'^id_.*$',        # starts with 'id_'
            r'^.*identifier.*$', # contains 'identifier'
            r'^.*key$',        # ends with 'key'
            r'^.*code$',       # ends with 'code'
            r'^uuid$',         # exact match for 'uuid'
            r'^.*uuid.*$',     # contains 'uuid'
            r'^pk$',           # primary key
            r'^.*pk$',         # ends with 'pk'
        ]
        
        # Check if column name matches any ID pattern
        name_matches = any(re.match(pattern, column_name) for pattern in id_patterns)
        
        if not name_matches:
            return False
        
        # Additional checks for ID characteristics
        total_count = len(series)
        unique_count = len(non_null_series.unique())
        
        # ID fields should have high uniqueness (close to 100%)
        uniqueness_ratio = unique_count / total_count if total_count > 0 else 0
        
        # For ID fields, we expect:
        # 1. High uniqueness (typically > 95% for most IDs)
        # 2. No missing values (or very few)
        # 3. Consistent data type
        
        if uniqueness_ratio < 0.9:  # Allow some flexibility for real-world data
            return False
        
        # Check for UUID pattern if it's a string field
        if series.dtype == 'object':
            # Sample some values to check for UUID pattern
            sample_size = min(10, len(non_null_series))
            sample = non_null_series.head(sample_size)
            
            uuid_pattern = re.compile(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                re.IGNORECASE
            )
            
            # If any sample looks like UUID, it's likely an ID
            if any(uuid_pattern.match(str(val)) for val in sample):
                return True
        
        # For numeric IDs, check if they're sequential or have ID-like characteristics
        if pd.api.types.is_numeric_dtype(series):
            # Check if values are mostly sequential or have ID-like patterns
            numeric_series = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_series) > 1:
                # Check if values are positive and reasonable for IDs
                if numeric_series.min() >= 0 and numeric_series.max() < 1e12:
                    return True
        
        return True
    
    def _is_boolean(self, series: pd.Series) -> bool:
        """Check if series contains boolean values."""
        # Check if all non-null values are boolean-like
        non_null = series.dropna()
        if len(non_null) == 0:
            return False
        
        # Check for pandas boolean type
        if series.dtype == 'bool':
            return True
        
        # Check for string representations of booleans
        if series.dtype == 'object':
            bool_patterns = {
                'true', 'false', 'yes', 'no', '1', '0', 
                't', 'f', 'y', 'n', 'on', 'off'
            }
            unique_values = set(str(val).lower().strip() for val in non_null)
            return unique_values.issubset(bool_patterns)
        
        return False
    
    def _is_datetime(self, series: pd.Series) -> bool:
        """Check if series contains datetime values."""
        # Check if pandas already detected it as datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return True
        
        # Try to parse as datetime
        if series.dtype == 'object':
            sample_size = min(100, len(series.dropna()))
            if sample_size == 0:
                return False
            
            sample = series.dropna().head(sample_size)
            datetime_count = 0
            
            for value in sample:
                if self._can_parse_datetime(value):
                    datetime_count += 1
            
            # If more than 80% of sample can be parsed as datetime
            return datetime_count / sample_size > 0.8
        
        return False
    
    def _can_parse_datetime(self, value: Any) -> bool:
        """Check if a value can be parsed as datetime."""
        if pd.isna(value):
            return False
        
        try:
            pd.to_datetime(value, errors='raise')
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_integer(self, series: pd.Series) -> bool:
        """Check if series contains integer values."""
        # Check if pandas already detected it as integer
        if pd.api.types.is_integer_dtype(series):
            return True
        
        # Try to convert to numeric and check if all values are integers
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            non_null = numeric_series.dropna()
            
            if len(non_null) == 0:
                return False
            
            # Check if all values are integers
            return all(float(val).is_integer() for val in non_null)
        except (ValueError, TypeError):
            return False
    
    def _is_float(self, series: pd.Series) -> bool:
        """Check if series contains float values."""
        # Check if pandas already detected it as float
        if pd.api.types.is_float_dtype(series):
            return True
        
        # Try to convert to numeric
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            non_null = numeric_series.dropna()
            
            if len(non_null) == 0:
                return False
            
            # If we can convert to numeric and not all are integers, it's float
            return not all(float(val).is_integer() for val in non_null)
        except (ValueError, TypeError):
            return False
    
    def _is_categorical(self, series: pd.Series) -> bool:
        """Check if series should be treated as categorical."""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return False
        
        # Calculate ratio of unique values to total values
        unique_ratio = len(non_null.unique()) / len(non_null)
        
        # If ratio is below threshold, consider it categorical
        if unique_ratio <= self.categorical_threshold:
            return True
        
        # Also check if it's a string field with limited unique values
        if series.dtype == 'object' and unique_ratio <= 0.3:
            return True
        
        return False


def get_sample_values(series: pd.Series, max_samples: int = 5) -> List[Any]:
    """
    Get a sample of values from a series.
    
    Args:
        series: Pandas Series to sample from
        max_samples: Maximum number of samples to return
        
    Returns:
        List of sample values
    """
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return []
    
    # Get unique values first
    unique_values = non_null.unique()
    
    # If we have fewer unique values than max_samples, return all
    if len(unique_values) <= max_samples:
        return unique_values.tolist()
    
    # Otherwise, sample from unique values
    return np.random.choice(unique_values, size=max_samples, replace=False).tolist() 