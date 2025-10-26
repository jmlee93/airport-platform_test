# Excel Workbook Analyzer

This repository provides utilities for exploring Excel workbooks and extracting
structured metadata that can be consumed by downstream systems. The core
features include:

1. Loading workbooks with `openpyxl` and creating a JSON-friendly metadata
   structure containing sheet information, named ranges, and per-cell
   annotations.
2. Parsing each cell's value, formula, and dependencies to build a
   workbook-level directed acyclic graph (DAG) that distinguishes explicit
   inputs from calculated outputs.
3. Detecting table-like regions in worksheets (both native Excel tables and
   heuristically identified ranges) and exposing their contents as
   `pandas.DataFrame` instances.
4. Identifying financial metrics (e.g., IRR, NPV, DSCR) that appear within
   formulas via a pluggable rule system.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from pathlib import Path
from excel_analyzer import WorkbookAnalyzer

analyzer = WorkbookAnalyzer()
result = analyzer.analyze(Path("path/to/workbook.xlsx"))

# Access workbook metadata
metadata = result.workbook

# Serialize to JSON
from excel_analyzer.parser import WorkbookParser
parser = WorkbookParser(Path("path/to/workbook.xlsx"))
json_payload = parser.to_json(metadata)

# Inspect dependency graph
graph = result.dependency_graph
ordered_nodes = graph.topological_sort()

# Review detected financial metrics
for metric in result.financial_metrics:
    print(metric.metric, metric.details)
```
