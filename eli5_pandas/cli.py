"""Command-line interface for ELI5 Pandas."""

import sys
from pathlib import Path
from typing import Optional

import click

from .analyzer import DataAnalyzer
from .reporter import HTMLReporter


@click.group()
@click.version_option()
def main() -> None:
    """ELI5 Pandas - A comprehensive data analysis library for flat files."""
    pass


@main.command()
@click.argument('file_path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--output-json',
    '-j',
    type=click.Path(path_type=Path),
    help='Path to save JSON analysis results'
)
@click.option(
    '--output-html',
    '-h',
    type=click.Path(path_type=Path),
    help='Path to save HTML report'
)
@click.option(
    '--categorical-threshold',
    '-t',
    type=float,
    default=0.1,
    help='Threshold for determining categorical fields (default: 0.1)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output'
)
def analyze(
    file_path: Path,
    output_json: Optional[Path],
    output_html: Optional[Path],
    categorical_threshold: float,
    verbose: bool
) -> None:
    """
    Analyze a flat file and generate comprehensive reports.
    
    FILE_PATH: Path to the file to analyze (CSV, JSON, Excel, or Parquet)
    """
    try:
        if verbose:
            click.echo(f"🔍 Analyzing file: {file_path}")
            click.echo(f"📊 Categorical threshold: {categorical_threshold}")
        
        # Initialize analyzer
        analyzer = DataAnalyzer(categorical_threshold=categorical_threshold)
        
        # Perform analysis
        if verbose:
            click.echo("⏳ Starting analysis...")
        
        analysis_result = analyzer.analyze_file(str(file_path))
        
        if verbose:
            click.echo(f"✅ Analysis completed in {analysis_result.processing_time_seconds}s")
            click.echo(f"📈 Found {analysis_result.total_rows} rows and {analysis_result.total_columns} columns")
        
        # Save JSON output if requested
        if output_json:
            if verbose:
                click.echo(f"💾 Saving JSON results to: {output_json}")
            analyzer.save_analysis_to_json(analysis_result, str(output_json))
            click.echo(f"✅ JSON results saved to: {output_json}")
        
        # Generate HTML report if requested
        if output_html:
            if verbose:
                click.echo(f"🌐 Generating HTML report: {output_html}")
            reporter = HTMLReporter()
            reporter.generate_report(analysis_result, str(output_html))
            click.echo(f"✅ HTML report saved to: {output_html}")
        
        # Display summary if no output files specified
        if not output_json and not output_html:
            _display_summary(analysis_result)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('json_path', type=click.Path(exists=True, path_type=Path))
@click.argument('output_path', type=click.Path(path_type=Path))
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output'
)
def generate_html(json_path: Path, output_path: Path, verbose: bool) -> None:
    """
    Generate HTML report from existing JSON analysis results.
    
    JSON_PATH: Path to the JSON analysis file
    OUTPUT_PATH: Path where to save the HTML report
    """
    try:
        if verbose:
            click.echo(f"📄 Loading analysis from: {json_path}")
            click.echo(f"🌐 Generating HTML report: {output_path}")
        
        reporter = HTMLReporter()
        reporter.generate_from_json(str(json_path), str(output_path))
        
        click.echo(f"✅ HTML report saved to: {output_path}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument('file_path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    help='Path to save the analysis results (default: auto-generated)'
)
@click.option(
    '--categorical-threshold',
    '-t',
    type=float,
    default=0.1,
    help='Threshold for determining categorical fields (default: 0.1)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Enable verbose output'
)
def quick_analyze(
    file_path: Path,
    output: Optional[Path],
    categorical_threshold: float,
    verbose: bool
) -> None:
    """
    Quick analysis with automatic output file generation.
    
    FILE_PATH: Path to the file to analyze
    """
    try:
        if verbose:
            click.echo(f"🚀 Quick analysis of: {file_path}")
        
        # Generate output paths if not provided
        if not output:
            output = file_path.parent / f"{file_path.stem}_analysis"
        
        json_path = output.with_suffix('.json')
        html_path = output.with_suffix('.html')
        
        if verbose:
            click.echo(f"📊 JSON output: {json_path}")
            click.echo(f"🌐 HTML output: {html_path}")
        
        # Initialize analyzer
        analyzer = DataAnalyzer(categorical_threshold=categorical_threshold)
        
        # Perform analysis
        if verbose:
            click.echo("⏳ Analyzing...")
        
        analysis_result = analyzer.analyze_file(str(file_path))
        
        # Save results
        analyzer.save_analysis_to_json(analysis_result, str(json_path))
        
        reporter = HTMLReporter()
        reporter.generate_report(analysis_result, str(html_path))
        
        click.echo(f"✅ Analysis complete!")
        click.echo(f"📄 JSON results: {json_path}")
        click.echo(f"🌐 HTML report: {html_path}")
        
        # Display summary
        _display_summary(analysis_result)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


def _display_summary(analysis_result) -> None:
    """Display a summary of the analysis results."""
    click.echo("\n" + "="*60)
    click.echo("📊 ANALYSIS SUMMARY")
    click.echo("="*60)
    click.echo(f"📁 File: {analysis_result.file_path}")
    click.echo(f"📋 Type: {analysis_result.file_type.upper()}")
    click.echo(f"📈 Rows: {analysis_result.total_rows:,}")
    click.echo(f"📋 Columns: {analysis_result.total_columns}")
    click.echo(f"⚡ Processing time: {analysis_result.processing_time_seconds}s")
    
    # Field type breakdown
    type_counts = {}
    for field in analysis_result.fields:
        field_type = field.field_type.value
        type_counts[field_type] = type_counts.get(field_type, 0) + 1
    
    click.echo("\n📊 Field Types:")
    for field_type, count in sorted(type_counts.items()):
        click.echo(f"   • {field_type.title()}: {count}")
    
    # Data quality summary
    total_missing = sum(
        field.categorical_stats.missing_count if field.categorical_stats else 0
        or field.numerical_stats.missing_count if field.numerical_stats else 0
        or field.string_stats.missing_count if field.string_stats else 0
        or field.datetime_stats.missing_count if field.datetime_stats else 0
        for field in analysis_result.fields
    )
    
    total_cells = analysis_result.total_rows * analysis_result.total_columns
    completeness = ((total_cells - total_missing) / total_cells * 100) if total_cells > 0 else 0
    
    click.echo(f"\n✅ Data Quality:")
    click.echo(f"   • Completeness: {completeness:.1f}%")
    click.echo(f"   • Missing values: {total_missing:,}")
    
    click.echo("="*60)


if __name__ == '__main__':
    main() 