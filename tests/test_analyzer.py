import pytest
from eli5_pandas.analyzer import DataAnalyzer
from eli5_pandas.models import AnalysisResult
from pathlib import Path
import os

SAMPLE_DIR = Path(__file__).parent.parent / "sample_data"

@pytest.mark.parametrize("filename", [
    "sample_data.csv",
    "sample_data.json",
    "sample_data.xlsx",
    "sample_data.parquet",
    "sample_data_with_missing.csv",
    "sample_data_with_missing.json",
])
def test_analyze_file(filename):
    analyzer = DataAnalyzer()
    file_path = SAMPLE_DIR / filename
    assert file_path.exists(), f"Sample file does not exist: {file_path}"
    result = analyzer.analyze_file(str(file_path))
    assert isinstance(result, AnalysisResult)
    assert result.total_rows > 0
    assert result.total_columns > 0
    assert len(result.fields) == result.total_columns
    # Check that at least one field is detected as categorical, string, or numerical
    field_types = {field.field_type.value for field in result.fields}
    assert any(ft in field_types for ft in ["categorical", "string", "integer", "float"])


def test_save_and_load_json(tmp_path):
    analyzer = DataAnalyzer()
    file_path = SAMPLE_DIR / "sample_data.csv"
    result = analyzer.analyze_file(str(file_path))
    json_path = tmp_path / "analysis.json"
    analyzer.save_analysis_to_json(result, str(json_path))
    assert json_path.exists()
    loaded = analyzer.load_analysis_from_json(str(json_path))
    assert loaded == result 