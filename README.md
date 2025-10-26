# Model Analyzer Toolkit

This repository provides a unified toolkit for auditing Excel-based financial models.
It includes:

1. **Command line interface** – run `./analyze-model input.xlsx --config config.yaml` to
   generate JSON reports and structured logs.
2. **Streamlit dashboard** – upload spreadsheets through a web UI, explore the metrics,
   and download the latest report.
3. **Batch scheduler** – periodically process multiple files, compare them with previous
   runs, and write audit logs to disk.
4. **Audit logging** – warnings about parse errors, missing worksheets, and broken
   formulas surface in both the CLI and web flows.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CLI usage

```bash
./analyze-model path/to/model.xlsx --config config.yaml --report reports/model.json
```

Arguments:

- `input.xlsx` – path to the workbook you want to analyze.
- `--config` – optional YAML file (see `config.sample.yaml`).
- `--report` – optional output location for the JSON report (defaults to `reports/`).
- `--verbose` – add detailed rows to the audit log.

### Batch scheduler

Add a `batch` section to your configuration (paths are created automatically) and run:

```bash
./analyze-model batch --config config.yaml --iterations 1
```

Set `--iterations 0` to keep the scheduler running continuously. Each iteration stores a
snapshot in `batch_state/` and logs deltas between runs.

### Streamlit dashboard

```bash
streamlit run analyze_model/web_app.py
```

Upload `config.yaml` (optional) and your Excel workbook to see sheet-level metrics and to
download the JSON report directly from the browser.

### Logs

Audit logs are written to `logs/audit.log` and `logs/errors.log`. The Streamlit app shows
recent entries in-line. Missing sheets, Excel error cells, and parsing failures are always
highlighted.

## Project structure

```
analyze_model/
    analysis.py      # Core analysis routines
    batch.py         # Batch scheduler and change tracking
    cli.py           # CLI entry point
    config.py        # Configuration loader
    logging_utils.py # Logging helpers
    report.py        # Report writers
    web_app.py       # Streamlit dashboard
```

Use `config.sample.yaml` as a starting point for new projects.
