import pytest
import pandas as pd
from eli5_pandas.charts import ChartGenerator
from eli5_pandas.models import FieldAnalysis, FieldType
from eli5_pandas.analyzer import DataAnalyzer
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent.parent / "sample_data"


def test_chart_generator_initialization():
    """Test ChartGenerator initialization."""
    generator = ChartGenerator()
    assert generator is not None


def test_categorical_chart_generation():
    """Test categorical chart generation."""
    generator = ChartGenerator()
    
    # Create sample categorical data
    data = pd.Series(['A', 'B', 'A', 'C', 'B', 'A', 'D', 'C'])
    field = FieldAnalysis(
        name="test_categorical",
        field_type=FieldType.CATEGORICAL,
        total_count=8,
        categorical_stats=None,
        numerical_stats=None,
        string_stats=None,
        datetime_stats=None,
        sample_values=['A', 'B', 'C']
    )
    
    chart_html = generator.generate_field_chart(field, data)
    assert chart_html is not None
    assert "plotly" in chart_html.lower()
    assert "bar" in chart_html.lower()


def test_numerical_chart_generation():
    """Test numerical chart generation."""
    generator = ChartGenerator()
    
    # Create sample numerical data
    data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    field = FieldAnalysis(
        name="test_numerical",
        field_type=FieldType.INTEGER,
        total_count=10,
        categorical_stats=None,
        numerical_stats=None,
        string_stats=None,
        datetime_stats=None,
        sample_values=[1, 2, 3]
    )
    
    chart_html = generator.generate_field_chart(field, data)
    assert chart_html is not None
    assert "plotly" in chart_html.lower()
    assert "histogram" in chart_html.lower()


def test_boolean_chart_generation():
    """Test boolean chart generation."""
    generator = ChartGenerator()
    
    # Create sample boolean data
    data = pd.Series([True, False, True, True, False])
    field = FieldAnalysis(
        name="test_boolean",
        field_type=FieldType.BOOLEAN,
        total_count=5,
        categorical_stats=None,
        numerical_stats=None,
        string_stats=None,
        datetime_stats=None,
        sample_values=[True, False]
    )
    
    chart_html = generator.generate_field_chart(field, data)
    assert chart_html is not None
    assert "plotly" in chart_html.lower()
    assert "pie" in chart_html.lower()


def test_summary_charts_generation():
    """Test summary charts generation."""
    generator = ChartGenerator()
    
    # Create sample data and fields
    data = pd.DataFrame({
        'category': ['A', 'B', 'A', 'C'],
        'number': [1, 2, 3, 4],
        'boolean': [True, False, True, False]
    })
    
    fields = [
        FieldAnalysis(
            name="category",
            field_type=FieldType.CATEGORICAL,
            total_count=4,
            categorical_stats=None,
            numerical_stats=None,
            string_stats=None,
            datetime_stats=None,
            sample_values=['A', 'B', 'C']
        ),
        FieldAnalysis(
            name="number",
            field_type=FieldType.INTEGER,
            total_count=4,
            categorical_stats=None,
            numerical_stats=None,
            string_stats=None,
            datetime_stats=None,
            sample_values=[1, 2, 3, 4]
        ),
        FieldAnalysis(
            name="boolean",
            field_type=FieldType.BOOLEAN,
            total_count=4,
            categorical_stats=None,
            numerical_stats=None,
            string_stats=None,
            datetime_stats=None,
            sample_values=[True, False]
        )
    ]
    
    charts = generator.generate_summary_charts(fields, data)
    assert 'field_types' in charts
    assert charts['field_types'] is not None
    assert "plotly" in charts['field_types'].lower()


def test_analyzer_with_charts():
    """Test analyzer with chart generation."""
    analyzer = DataAnalyzer()
    file_path = SAMPLE_DIR / "sample_data.csv"
    
    # Perform analysis
    result = analyzer.analyze_file(str(file_path))
    
    # Generate charts
    charts = analyzer.generate_charts(result)
    
    # Check that charts were generated
    assert len(charts) > 0
    
    # Check that we have summary charts
    assert 'field_types' in charts
    
    # Check that we have field charts for some fields
    field_charts = [k for k in charts.keys() if k.startswith('field_')]
    assert len(field_charts) > 0 