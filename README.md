# ELI5 Pandas

**ELI5 Pandas** is a Python library and CLI tool for quickly analyzing flat files (CSV, JSON, Excel, Parquet) and generating professional, easy-to-read HTML reports. It automatically detects field types, computes relevant statistics, and outputs both structured JSON and beautiful HTML summaries with interactive charts. Designed for data scientists, analysts, and engineers who want fast, clear insights into their data.

---

## Features

- 📂 **Supports CSV, JSON, Excel, and Parquet files**
- 🧠 **Automatic field type detection** (categorical, numerical, string, datetime, boolean, ID)
- 📊 **Smart ID detection** - automatically identifies identifier columns (integer IDs, UUIDs, codes, keys)
- 📝 **Sample table** - configurable sample of your data (head or random, default 5 rows) shown at the top of the HTML report
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

Quick analysis with auto-named outputs, charts, and a random sample of 8 rows:

```bash
eli5-analyze quick-analyze data.csv --with-charts --sample-size 8 --sample-type random
```

**Sample Table Options:**
- `--sample-size N` (default: 5) — number of rows to show in the sample table
- `--sample-type head|random` (default: head) — show the first N rows or a random N rows

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
sample_df = analyzer.get_sample(n=8, sample_type='random')
charts = analyzer.generate_charts(result)

# Create HTML report with charts and sample table
reporter = HTMLReporter()
reporter.generate_report(result, 'report.html', charts, sample_df)
```

---

## Chart Types

The library automatically generates appropriate charts based on field types:

- **📊 Histograms** for numerical fields (integer, float)
- **📈 Bar charts** for categorical fields (horizontal, showing value distribution)
- **🥧 Pie charts** for boolean fields (true/false distribution)
- **📅 Time series** for datetime fields (timeline of occurrences)
- **📋 Summary charts** for overall dataset insights (field type distribution, missing data)

## Field Type Detection

The library intelligently detects field types based on data characteristics and column names:

### Supported Field Types
- **String**: Text data with high variability
- **Integer**: Whole numbers
- **Float**: Decimal numbers
- **Boolean**: True/false values (including string representations)
- **Datetime**: Date and time values
- **Categorical**: Limited set of unique values (configurable threshold)
- **ID**: Identifier columns with high uniqueness

### Smart ID Detection
The library automatically identifies ID columns based on:
- **Column name patterns**: `id`, `user_id`, `product_code`, `uuid`, `pk`, etc.
- **Data characteristics**: High uniqueness (>90%), consistent format
- **UUID detection**: Recognizes standard UUID format strings
- **Numeric ID validation**: Positive integers within reasonable range

ID fields are treated as categorical for statistics and charts, since they represent unique identifiers rather than numerical data for analysis.

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