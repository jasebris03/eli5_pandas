"""Pydantic models for data analysis results."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class FieldType(str, Enum):
    """Enumeration of possible field types."""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    CATEGORICAL = "categorical"
    ID = "id"
    UNKNOWN = "unknown"


class CategoricalStats(BaseModel):
    """Statistics for categorical fields."""
    
    unique_count: int = Field(..., description="Number of unique values")
    top_values: List[Dict[str, Any]] = Field(..., description="Top 10 most frequent values with counts")
    missing_count: int = Field(..., description="Number of missing values")
    missing_percentage: float = Field(..., description="Percentage of missing values")


class NumericalStats(BaseModel):
    """Statistics for numerical fields."""
    
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum value")
    mean: Optional[float] = Field(None, description="Mean value")
    median: Optional[float] = Field(None, description="Median value")
    std_dev: Optional[float] = Field(None, description="Standard deviation")
    quartiles: Optional[Dict[str, float]] = Field(None, description="25th, 50th, 75th percentiles")
    missing_count: int = Field(..., description="Number of missing values")
    missing_percentage: float = Field(..., description="Percentage of missing values")


class StringStats(BaseModel):
    """Statistics for string fields."""
    
    min_length: Optional[int] = Field(None, description="Minimum string length")
    max_length: Optional[int] = Field(None, description="Maximum string length")
    avg_length: Optional[float] = Field(None, description="Average string length")
    unique_count: int = Field(..., description="Number of unique values")
    missing_count: int = Field(..., description="Number of missing values")
    missing_percentage: float = Field(..., description="Percentage of missing values")


class DateTimeStats(BaseModel):
    """Statistics for datetime fields."""
    
    min_date: Optional[datetime] = Field(None, description="Earliest date")
    max_date: Optional[datetime] = Field(None, description="Latest date")
    unique_count: int = Field(..., description="Number of unique values")
    missing_count: int = Field(..., description="Number of missing values")
    missing_percentage: float = Field(..., description="Percentage of missing values")


class FieldAnalysis(BaseModel):
    """Analysis results for a single field."""
    
    name: str = Field(..., description="Field name")
    field_type: FieldType = Field(..., description="Detected field type")
    total_count: int = Field(..., description="Total number of values")
    categorical_stats: Optional[CategoricalStats] = Field(None, description="Categorical statistics")
    numerical_stats: Optional[NumericalStats] = Field(None, description="Numerical statistics")
    string_stats: Optional[StringStats] = Field(None, description="String statistics")
    datetime_stats: Optional[DateTimeStats] = Field(None, description="Datetime statistics")
    sample_values: List[Any] = Field(..., description="Sample of actual values")


class AnalysisResult(BaseModel):
    """Complete analysis results for a dataset."""
    
    file_path: str = Field(..., description="Path to the analyzed file")
    file_type: str = Field(..., description="Type of file (CSV, JSON, etc.)")
    total_rows: int = Field(..., description="Total number of rows")
    total_columns: int = Field(..., description="Total number of columns")
    fields: List[FieldAnalysis] = Field(..., description="Analysis results for each field")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    processing_time_seconds: float = Field(..., description="Time taken to perform analysis") 