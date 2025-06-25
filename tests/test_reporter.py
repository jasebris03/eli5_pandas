import pytest
from eli5_pandas.analyzer import DataAnalyzer
from eli5_pandas.reporter import HTMLReporter
from pathlib import Path
import os
import tempfile
import pandas as pd

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

@pytest.mark.parametrize("sample_type", ["head", "random"])
def test_html_report_includes_sample_table(sample_type):
    analyzer = DataAnalyzer()
    result = analyzer.analyze_file("sample_data/sample_data.csv")
    sample_df = analyzer.get_sample(n=4, sample_type=sample_type)
    charts = analyzer.generate_charts(result)
    reporter = HTMLReporter()
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        reporter.generate_report(result, tmp_path, charts, sample_df)
        with open(tmp_path, "r", encoding="utf-8") as f:
            html = f.read()
        # Check that the sample table section is present
        assert "Sample Data (4 rows)" in html
        # Check that at least one value from the sample appears in the HTML
        for val in sample_df.iloc[0].astype(str):
            assert val in html
    finally:
        os.remove(tmp_path)

def test_html_report_sample_table_size():
    analyzer = DataAnalyzer()
    result = analyzer.analyze_file("sample_data/sample_data.csv")
    for n in [1, 3, 7]:
        sample_df = analyzer.get_sample(n=n, sample_type="head")
        charts = analyzer.generate_charts(result)
        reporter = HTMLReporter()
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            reporter.generate_report(result, tmp_path, charts, sample_df)
            with open(tmp_path, "r", encoding="utf-8") as f:
                html = f.read()
            assert f"Sample Data ({n} rows)" in html
        finally:
            os.remove(tmp_path) 