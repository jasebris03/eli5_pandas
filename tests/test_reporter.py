import pytest
from eli5_pandas.analyzer import DataAnalyzer
from eli5_pandas.reporter import HTMLReporter
from pathlib import Path
import os

SAMPLE_DIR = Path(__file__).parent.parent / "sample_data"

@pytest.mark.parametrize("filename", [
    "sample_data.csv",
    "sample_data.json",
    "sample_data.xlsx",
    "sample_data.parquet",
])
def test_generate_html_report(tmp_path, filename):
    analyzer = DataAnalyzer()
    reporter = HTMLReporter()
    file_path = SAMPLE_DIR / filename
    result = analyzer.analyze_file(str(file_path))
    html_path = tmp_path / f"{filename}.html"
    reporter.generate_report(result, str(html_path))
    assert html_path.exists()
    content = html_path.read_text()
    assert "<html" in content.lower()
    assert result.file_path in content


def test_generate_html_from_json(tmp_path):
    analyzer = DataAnalyzer()
    reporter = HTMLReporter()
    file_path = SAMPLE_DIR / "sample_data.csv"
    result = analyzer.analyze_file(str(file_path))
    json_path = tmp_path / "analysis.json"
    html_path = tmp_path / "report.html"
    analyzer.save_analysis_to_json(result, str(json_path))
    reporter.generate_from_json(str(json_path), str(html_path))
    assert html_path.exists()
    content = html_path.read_text()
    assert "<html" in content.lower()
    assert result.file_path in content 