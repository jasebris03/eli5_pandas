"""Main data analyzer for flat files."""

import json
import time
from pathlib import Path
from typing import Optional

import pandas as pd

from .field_detector import FieldTypeDetector, get_sample_values
from .models import AnalysisResult, FieldAnalysis, FieldType
from .statistics import StatisticsCalculator
from .charts import ChartGenerator


class DataAnalyzer:
    """Main class for analyzing flat files and generating comprehensive reports."""
    
    def __init__(self, categorical_threshold: float = 0.1) -> None:
        """
        Initialize the data analyzer.
        
        Args:
            categorical_threshold: Threshold for determining categorical fields
        """
        self.field_detector = FieldTypeDetector(categorical_threshold)
        self.stats_calculator = StatisticsCalculator()
        self.chart_generator = ChartGenerator()
        self._data: Optional[pd.DataFrame] = None
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Analyze a flat file and return comprehensive analysis results.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            AnalysisResult object with complete analysis
        """
        start_time = time.time()
        
        # Load the data
        self._data = self._load_data(file_path)
        
        # Analyze each field
        field_analyses = []
        for column in self._data.columns:
            field_analysis = self._analyze_field(self._data[column], column)
            field_analyses.append(field_analysis)
        
        processing_time = time.time() - start_time
        
        # Create the analysis result
        result = AnalysisResult(
            file_path=file_path,
            file_type=self._get_file_type(file_path),
            total_rows=len(self._data),
            total_columns=len(self._data.columns),
            fields=field_analyses,
            processing_time_seconds=round(processing_time, 2)
        )
        
        return result
    
    def generate_charts(self, analysis_result: AnalysisResult) -> dict:
        """
        Generate charts for the analysis result.
        
        Args:
            analysis_result: AnalysisResult object
            
        Returns:
            Dictionary containing charts for each field and summary charts
        """
        if self._data is None:
            raise ValueError("No data loaded. Call analyze_file() first.")
        
        charts = {}
        
        # Generate charts for each field
        for field in analysis_result.fields:
            field_chart = self.chart_generator.generate_field_chart(field, self._data[field.name])
            if field_chart:
                charts[f"field_{field.name}"] = field_chart
        
        # Generate summary charts
        summary_charts = self.chart_generator.generate_summary_charts(analysis_result.fields, self._data)
        charts.update(summary_charts)
        
        return charts
    
    def _load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Pandas DataFrame
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() == '.json':
            return pd.read_json(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif file_path.suffix.lower() == '.parquet':
            return pd.read_parquet(file_path)
        else:
            # Try to read as CSV by default
            try:
                return pd.read_csv(file_path)
            except Exception:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _get_file_type(self, file_path: str) -> str:
        """
        Get the file type based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File type string
        """
        return Path(file_path).suffix.lower().lstrip('.')
    
    def _analyze_field(self, series: pd.Series, column_name: str) -> FieldAnalysis:
        """
        Analyze a single field/column.
        
        Args:
            series: Pandas Series to analyze
            column_name: Name of the column
            
        Returns:
            FieldAnalysis object
        """
        # Detect field type
        field_type = self.field_detector.detect_field_type(series)
        
        # Get sample values
        sample_values = get_sample_values(series)
        
        # Calculate statistics based on field type
        categorical_stats = None
        numerical_stats = None
        string_stats = None
        datetime_stats = None
        
        if field_type == FieldType.CATEGORICAL:
            categorical_stats = self.stats_calculator.calculate_categorical_stats(series)
        elif field_type in [FieldType.INTEGER, FieldType.FLOAT]:
            numerical_stats = self.stats_calculator.calculate_numerical_stats(series)
        elif field_type == FieldType.STRING:
            string_stats = self.stats_calculator.calculate_string_stats(series)
        elif field_type == FieldType.DATETIME:
            datetime_stats = self.stats_calculator.calculate_datetime_stats(series)
        elif field_type == FieldType.BOOLEAN:
            # Treat boolean as categorical for statistics
            categorical_stats = self.stats_calculator.calculate_categorical_stats(series)
        elif field_type == FieldType.ID:
            # Treat ID as categorical for statistics (since IDs are unique identifiers)
            categorical_stats = self.stats_calculator.calculate_categorical_stats(series)
        
        return FieldAnalysis(
            name=column_name,
            field_type=field_type,
            total_count=len(series),
            categorical_stats=categorical_stats,
            numerical_stats=numerical_stats,
            string_stats=string_stats,
            datetime_stats=datetime_stats,
            sample_values=sample_values
        )
    
    def save_analysis_to_json(self, analysis_result: AnalysisResult, output_path: str) -> None:
        """
        Save analysis results to a JSON file.
        
        Args:
            analysis_result: AnalysisResult object to save
            output_path: Path where to save the JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(analysis_result.model_dump(), f, indent=2, default=str)
    
    def load_analysis_from_json(self, json_path: str) -> AnalysisResult:
        """
        Load analysis results from a JSON file.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            AnalysisResult object
        """
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return AnalysisResult.model_validate(data)
    
    def get_sample(self, n: int = 5, sample_type: str = 'head') -> Optional[pd.DataFrame]:
        """
        Return a sample of the loaded data (head or random).
        Args:
            n: Number of rows to return
            sample_type: 'head' for first n rows, 'random' for random n rows
        Returns:
            Sample DataFrame or None if no data loaded
        """
        if self._data is None:
            return None
        if sample_type == 'random':
            return self._data.sample(n=min(n, len(self._data)), random_state=42)
        else:
            return self._data.head(n) 