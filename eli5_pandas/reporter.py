"""HTML report generator for analysis results."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template

from .models import AnalysisResult, FieldAnalysis, FieldType


def _format_number(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return value


class HTMLReporter:
    """Generates professional HTML reports from analysis results."""
    
    def __init__(self) -> None:
        """Initialize the HTML reporter."""
        self.env = Environment(loader=FileSystemLoader(self._get_template_dir()))
        self.env.filters['format_number'] = _format_number
    
    def _get_template_dir(self) -> str:
        """Get the directory containing HTML templates."""
        return str(Path(__file__).parent / "templates")
    
    def generate_report(self, analysis_result: AnalysisResult, output_path: str, charts: Optional[Dict[str, str]] = None, sample_df: Optional[Any] = None, show_all_stats: bool = False) -> None:
        """
        Generate an HTML report from analysis results.
        
        Args:
            analysis_result: AnalysisResult object
            output_path: Path where to save the HTML file
            charts: Optional dictionary of charts to include
            sample_df: Optional sample DataFrame to display
            show_all_stats: Whether to show all available statistics in the HTML report
        """
        template = self.env.get_template("report.html")
        
        # Prepare template context
        context = self._prepare_context(analysis_result, charts, sample_df, show_all_stats)
        
        # Render the template
        html_content = template.render(**context)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _prepare_context(self, analysis_result: AnalysisResult, charts: Optional[Dict[str, str]] = None, sample_df: Optional[Any] = None, show_all_stats: bool = False) -> Dict[str, Any]:
        """
        Prepare context data for the HTML template.
        
        Args:
            analysis_result: AnalysisResult object
            charts: Optional dictionary of charts
            sample_df: Optional sample DataFrame
            show_all_stats: Whether to show all available statistics in the HTML report
            
        Returns:
            Dictionary with template context
        """
        # Group fields by type
        fields_by_type = self._group_fields_by_type(analysis_result.fields)
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_stats(analysis_result)
        
        # Convert sample_df to records for Jinja2
        sample_table = None
        sample_columns = None
        if sample_df is not None:
            sample_table = sample_df.to_dict(orient='records')
            sample_columns = list(sample_df.columns)
        
        return {
            "analysis": analysis_result,
            "fields_by_type": fields_by_type,
            "summary_stats": summary_stats,
            "field_types": [ft.value for ft in FieldType],
            "charts": charts or {},
            "sample_table": sample_table,
            "sample_columns": sample_columns,
            "show_all_stats": show_all_stats,
        }
    
    def _group_fields_by_type(self, fields: List[FieldAnalysis]) -> Dict[str, List[FieldAnalysis]]:
        """
        Group fields by their detected type.
        
        Args:
            fields: List of FieldAnalysis objects
            
        Returns:
            Dictionary mapping field types to lists of fields
        """
        grouped = {}
        for field in fields:
            field_type = field.field_type.value
            if field_type not in grouped:
                grouped[field_type] = []
            grouped[field_type].append(field)
        
        return grouped
    
    def _calculate_summary_stats(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Calculate summary statistics for the dataset.
        
        Args:
            analysis_result: AnalysisResult object
            
        Returns:
            Dictionary with summary statistics
        """
        total_fields = len(analysis_result.fields)
        total_missing = sum(
            field.categorical_stats.missing_count if field.categorical_stats else 0
            or field.numerical_stats.missing_count if field.numerical_stats else 0
            or field.string_stats.missing_count if field.string_stats else 0
            or field.datetime_stats.missing_count if field.datetime_stats else 0
            for field in analysis_result.fields
        )
        
        # Count fields by type
        type_counts = {}
        for field in analysis_result.fields:
            field_type = field.field_type.value
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        return {
            "total_fields": total_fields,
            "total_missing": total_missing,
            "type_counts": type_counts,
            "completeness_percentage": round(
                ((analysis_result.total_rows * total_fields) - total_missing) / 
                (analysis_result.total_rows * total_fields) * 100, 2
            ) if total_fields > 0 else 0
        }
    
    def generate_from_json(self, json_path: str, output_path: str) -> None:
        """
        Generate HTML report directly from a JSON file.
        
        Args:
            json_path: Path to the JSON analysis file
            output_path: Path where to save the HTML file
        """
        # Load analysis result from JSON
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        analysis_result = AnalysisResult.model_validate(data)
        self.generate_report(analysis_result, output_path)


# Create a default HTML template if it doesn't exist
def create_default_template() -> None:
    """Create a default HTML template if it doesn't exist."""
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)
    
    template_path = template_dir / "report.html"
    
    if not template_path.exists():
        template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Analysis Report - {{ analysis.file_path }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .stat {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .charts-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .section-header h2 {
            color: #333;
            font-size: 1.5em;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        
        .chart-container {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            background: #fafbfc;
        }
        
        .field-type-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .field-grid {
            display: grid;
            gap: 20px;
            padding: 20px;
        }
        
        .field-card {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            background: #fafbfc;
        }
        
        .field-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .field-name {
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
        }
        
        .field-type-badge {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        
        .stat-label {
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
        }
        
        .sample-values {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .field-chart {
            margin-top: 15px;
            border-top: 1px solid #e9ecef;
            padding-top: 15px;
        }
        
        .missing-data {
            color: #dc3545;
        }
        
        .good-data {
            color: #28a745;
        }
        
        .warning-data {
            color: #ffc107;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header {
                padding: 20px 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .summary-cards {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Data Analysis Report</h1>
            <p>{{ analysis.file_path }} | Generated on {{ analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</p>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <h3>📈 Dataset Overview</h3>
                <div class="stat">{{ analysis.total_rows | format_number }}</div>
                <div class="stat-label">Total Rows</div>
            </div>
            <div class="card">
                <h3>📋 Fields</h3>
                <div class="stat">{{ analysis.total_columns }}</div>
                <div class="stat-label">Total Columns</div>
            </div>
            <div class="card">
                <h3>✅ Data Quality</h3>
                <div class="stat">{{ summary_stats.completeness_percentage }}%</div>
                <div class="stat-label">Completeness</div>
            </div>
            <div class="card">
                <h3>⚡ Performance</h3>
                <div class="stat">{{ analysis.processing_time_seconds }}s</div>
                <div class="stat-label">Processing Time</div>
            </div>
        </div>
        
        {% if charts %}
        <div class="charts-section">
            <div class="section-header">
                <h2>📊 Summary Charts</h2>
            </div>
            <div class="charts-grid">
                {% if charts.field_types %}
                <div class="chart-container">
                    <h3>Field Type Distribution</h3>
                    {{ charts.field_types | safe }}
                </div>
                {% endif %}
                {% if charts.missing_data %}
                <div class="chart-container">
                    <h3>Missing Data Overview</h3>
                    {{ charts.missing_data | safe }}
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
        
        {% for field_type, fields in fields_by_type.items() %}
        <div class="field-type-section">
            <div class="section-header">
                <h2>{{ field_type | title }} Fields ({{ fields | length }})</h2>
            </div>
            <div class="field-grid">
                {% for field in fields %}
                <div class="field-card">
                    <div class="field-header">
                        <div class="field-name">{{ field.name }}</div>
                        <div class="field-type-badge">{{ field.field_type.value }}</div>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">{{ field.total_count | format_number }}</div>
                            <div class="stat-label">Total Values</div>
                        </div>
                        
                        {% if field.categorical_stats %}
                        <div class="stat-item">
                            <div class="stat-value">{{ field.categorical_stats.unique_count | format_number }}</div>
                            <div class="stat-label">Unique Values</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {% if field.categorical_stats.missing_percentage > 10 %}missing-data{% elif field.categorical_stats.missing_percentage > 5 %}warning-data{% else %}good-data{% endif %}">
                                {{ field.categorical_stats.missing_percentage }}%
                            </div>
                            <div class="stat-label">Missing Data</div>
                        </div>
                        {% endif %}
                        
                        {% if field.numerical_stats %}
                        <div class="stat-item">
                            <div class="stat-value">{{ field.numerical_stats.mean | round(2) if field.numerical_stats.mean else 'N/A' }}</div>
                            <div class="stat-label">Mean</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ field.numerical_stats.std_dev | round(2) if field.numerical_stats.std_dev else 'N/A' }}</div>
                            <div class="stat-label">Std Dev</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {% if field.numerical_stats.missing_percentage > 10 %}missing-data{% elif field.numerical_stats.missing_percentage > 5 %}warning-data{% else %}good-data{% endif %}">
                                {{ field.numerical_stats.missing_percentage }}%
                            </div>
                            <div class="stat-label">Missing Data</div>
                        </div>
                        {% endif %}
                        
                        {% if field.string_stats %}
                        <div class="stat-item">
                            <div class="stat-value">{{ field.string_stats.avg_length | round(1) if field.string_stats.avg_length else 'N/A' }}</div>
                            <div class="stat-label">Avg Length</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ field.string_stats.unique_count | format_number }}</div>
                            <div class="stat-label">Unique Values</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {% if field.string_stats.missing_percentage > 10 %}missing-data{% elif field.string_stats.missing_percentage > 5 %}warning-data{% else %}good-data{% endif %}">
                                {{ field.string_stats.missing_percentage }}%
                            </div>
                            <div class="stat-label">Missing Data</div>
                        </div>
                        {% endif %}
                        
                        {% if field.datetime_stats %}
                        <div class="stat-item">
                            <div class="stat-value">{{ field.datetime_stats.min_date.strftime('%Y-%m-%d') if field.datetime_stats.min_date else 'N/A' }}</div>
                            <div class="stat-label">Earliest Date</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{{ field.datetime_stats.max_date.strftime('%Y-%m-%d') if field.datetime_stats.max_date else 'N/A' }}</div>
                            <div class="stat-label">Latest Date</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value {% if field.datetime_stats.missing_percentage > 10 %}missing-data{% elif field.datetime_stats.missing_percentage > 5 %}warning-data{% else %}good-data{% endif %}">
                                {{ field.datetime_stats.missing_percentage }}%
                            </div>
                            <div class="stat-label">Missing Data</div>
                        </div>
                        {% endif %}
                    </div>
                    
                    {% if field.sample_values %}
                    <div class="sample-values">
                        <strong>Sample Values:</strong> {{ field.sample_values | join(', ') }}
                    </div>
                    {% endif %}
                    
                    {% if charts['field_' + field.name] %}
                    <div class="field-chart">
                        {{ charts['field_' + field.name] | safe }}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>"""
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)


# Create the default template when the module is imported
create_default_template() 