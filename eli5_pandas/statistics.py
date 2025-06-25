"""Statistics calculation for different field types."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .models import CategoricalStats, DateTimeStats, NumericalStats, StringStats


class StatisticsCalculator:
    """Calculates statistics for different field types."""
    
    def __init__(self) -> None:
        """Initialize the statistics calculator."""
        pass
    
    def calculate_categorical_stats(self, series: pd.Series) -> CategoricalStats:
        """
        Calculate statistics for categorical fields.
        
        Args:
            series: Pandas Series containing categorical data
            
        Returns:
            CategoricalStats object
        """
        total_count = len(series)
        missing_count = series.isna().sum()
        missing_percentage = (missing_count / total_count) * 100 if total_count > 0 else 0
        
        # Get value counts for top values
        value_counts = series.value_counts().head(10)
        top_values = [
            {"value": str(val), "count": int(count), "percentage": (count / total_count) * 100}
            for val, count in value_counts.items()
        ]
        
        unique_count = len(series.unique())
        
        return CategoricalStats(
            unique_count=unique_count,
            top_values=top_values,
            missing_count=int(missing_count),
            missing_percentage=round(missing_percentage, 2)
        )
    
    def calculate_numerical_stats(self, series: pd.Series) -> NumericalStats:
        """
        Calculate statistics for numerical fields.
        
        Args:
            series: Pandas Series containing numerical data
            
        Returns:
            NumericalStats object
        """
        total_count = len(series)
        missing_count = series.isna().sum()
        missing_percentage = (missing_count / total_count) * 100 if total_count > 0 else 0
        
        # Convert to numeric, coercing errors to NaN
        numeric_series = pd.to_numeric(series, errors='coerce')
        non_null_series = numeric_series.dropna()
        
        if len(non_null_series) == 0:
            return NumericalStats(
                min_value=None,
                max_value=None,
                mean=None,
                median=None,
                std_dev=None,
                quartiles=None,
                missing_count=int(missing_count),
                missing_percentage=round(missing_percentage, 2)
            )
        
        # Calculate basic statistics
        min_value = float(non_null_series.min())
        max_value = float(non_null_series.max())
        mean = float(non_null_series.mean())
        median = float(non_null_series.median())
        std_dev = float(non_null_series.std())
        
        # Calculate quartiles
        quartiles = {
            "q25": float(non_null_series.quantile(0.25)),
            "q50": float(non_null_series.quantile(0.50)),
            "q75": float(non_null_series.quantile(0.75))
        }
        
        return NumericalStats(
            min_value=min_value,
            max_value=max_value,
            mean=round(mean, 4),
            median=round(median, 4),
            std_dev=round(std_dev, 4),
            quartiles=quartiles,
            missing_count=int(missing_count),
            missing_percentage=round(missing_percentage, 2)
        )
    
    def calculate_string_stats(self, series: pd.Series) -> StringStats:
        """
        Calculate statistics for string fields.
        
        Args:
            series: Pandas Series containing string data
            
        Returns:
            StringStats object
        """
        total_count = len(series)
        missing_count = series.isna().sum()
        missing_percentage = (missing_count / total_count) * 100 if total_count > 0 else 0
        
        # Convert to string and calculate lengths
        string_series = series.astype(str)
        non_null_series = string_series[string_series != 'nan']
        
        if len(non_null_series) == 0:
            return StringStats(
                min_length=None,
                max_length=None,
                avg_length=None,
                unique_count=0,
                missing_count=int(missing_count),
                missing_percentage=round(missing_percentage, 2)
            )
        
        # Calculate string lengths
        lengths = non_null_series.str.len()
        min_length = int(lengths.min())
        max_length = int(lengths.max())
        avg_length = float(lengths.mean())
        
        unique_count = len(non_null_series.unique())
        
        return StringStats(
            min_length=min_length,
            max_length=max_length,
            avg_length=round(avg_length, 2),
            unique_count=unique_count,
            missing_count=int(missing_count),
            missing_percentage=round(missing_percentage, 2)
        )
    
    def calculate_datetime_stats(self, series: pd.Series) -> DateTimeStats:
        """
        Calculate statistics for datetime fields.
        
        Args:
            series: Pandas Series containing datetime data
            
        Returns:
            DateTimeStats object
        """
        total_count = len(series)
        missing_count = series.isna().sum()
        missing_percentage = (missing_count / total_count) * 100 if total_count > 0 else 0
        
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(series):
            datetime_series = pd.to_datetime(series, errors='coerce')
        else:
            datetime_series = series
        
        non_null_series = datetime_series.dropna()
        
        if len(non_null_series) == 0:
            return DateTimeStats(
                min_date=None,
                max_date=None,
                unique_count=0,
                missing_count=int(missing_count),
                missing_percentage=round(missing_percentage, 2)
            )
        
        min_date = non_null_series.min().to_pydatetime()
        max_date = non_null_series.max().to_pydatetime()
        unique_count = len(non_null_series.unique())
        
        return DateTimeStats(
            min_date=min_date,
            max_date=max_date,
            unique_count=unique_count,
            missing_count=int(missing_count),
            missing_percentage=round(missing_percentage, 2)
        )
    
    def calculate_field_statistics(
        self, 
        series: pd.Series, 
        field_type: str
    ) -> Optional[Union[CategoricalStats, NumericalStats, StringStats, DateTimeStats]]:
        """
        Calculate statistics based on field type.
        
        Args:
            series: Pandas Series to analyze
            field_type: Type of field (from FieldType enum)
            
        Returns:
            Appropriate statistics object or None
        """
        if field_type == "categorical":
            return self.calculate_categorical_stats(series)
        elif field_type in ["integer", "float"]:
            return self.calculate_numerical_stats(series)
        elif field_type == "string":
            return self.calculate_string_stats(series)
        elif field_type == "datetime":
            return self.calculate_datetime_stats(series)
        elif field_type == "boolean":
            # Treat boolean as categorical for statistics
            return self.calculate_categorical_stats(series)
        else:
            return None 