# ELI5 Pandas

**ELI5 Pandas** is a Python library and CLI tool for quickly analyzing flat files (CSV, JSON, Excel, Parquet) and generating professional, easy-to-read HTML reports. It automatically detects field types, computes relevant statistics, and outputs both structured JSON and beautiful HTML summaries with interactive charts. Designed for data scientists, analysts, and engineers who want fast, clear insights into their data.

---

## Features

- 📂 **Supports CSV, JSON, Excel, and Parquet files**
- 🧠 **Automatic field type detection** (categorical, numerical, string, datetime, boolean)
- 📊 **Relevant statistics** for each field (unique counts, missing data, mean, std, quartiles, etc.)
- 📈 **Interactive charts** (histograms for numerical data, bar charts for categorical, pie charts for boolean, time series for dates)
- 📝 **JSON output** for programmatic use
- 🌐 **Professional HTML reports** (responsive, modern, and easy to read)
- 🛠️ **Modular, type-safe, and mypy-friendly**
- 🖱️ **Easy CLI and Python API**
- 🔒 **Pydantic models for all results**
- 🚀 **Ready for extension** (e.g., more chart types, additional formats)

---

## Installation

```bash
pip install .[dev]
```

Or, for development:

```bash
git clone https://github.com/yourusername/eli5-pandas.git
cd eli5-pandas
pip install -e .[dev]
```

---

## Usage

### CLI

Analyze a file and generate both JSON and HTML reports with charts:

```bash
eli5-analyze analyze data.csv --output-json report.json --output-html report.html --with-charts
```

Quick analysis with auto-named outputs and charts:

```bash
eli5-analyze quick-analyze data.csv --with-charts
```

Generate an HTML report from a JSON analysis:

```bash
eli5-analyze generate-html report.json report.html
```

See all options:

```bash
eli5-analyze --help
```

### Python Library

```python
from eli5_pandas import DataAnalyzer, HTMLReporter

# Basic analysis
analyzer = DataAnalyzer()
result = analyzer.analyze_file('data.csv')
analyzer.save_analysis_to_json(result, 'report.json')

# Generate charts
charts = analyzer.generate_charts(result)

# Create HTML report with charts
reporter = HTMLReporter()
reporter.generate_report(result, 'report.html', charts)
```

---

## Chart Types

The library automatically generates appropriate charts based on field types:

- **📊 Histograms** for numerical fields (integer, float)
- **📈 Bar charts** for categorical fields (horizontal, showing value distribution)
- **🥧 Pie charts** for boolean fields (true/false distribution)
- **📅 Time series** for datetime fields (timeline of occurrences)
- **📋 Summary charts** for overall dataset insights (field type distribution, missing data)

---

## Development

- Code is formatted with **black** and **isort**
- Type checking with **mypy**
- Linting with **flake8**
- Tests with **pytest**
- Pre-commit hooks are recommended

### Run all checks

```bash
pre-commit run --all-files
pytest
mypy eli5_pandas
```

---

## Contributing

Contributions are welcome! Please open issues or pull requests. Make sure to:

- Write clear, tested, and type-annotated code
- Run pre-commit and tests before submitting
- Follow the code style enforced by black/isort/flake8

---

## License

MIT 