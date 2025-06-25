"""ELI5 Pandas - A comprehensive data analysis library for flat files."""

__version__ = "0.1.0"

from .analyzer import DataAnalyzer
from .charts import ChartGenerator
from .models import AnalysisResult, FieldAnalysis, FieldType
from .reporter import HTMLReporter

__all__ = ["DataAnalyzer", "ChartGenerator", "AnalysisResult", "FieldAnalysis", "FieldType", "HTMLReporter"] 