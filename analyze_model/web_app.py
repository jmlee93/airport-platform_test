"""Streamlit dashboard for interactive spreadsheet analysis."""

from __future__ import annotations

import io
import json
import logging
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from .analysis import analyze_workbook
from .config import AnalysisConfig, load_config
from .logging_utils import configure_logging


st.set_page_config(page_title="Model Analyzer", layout="wide")


def _load_uploaded_config(uploaded_file) -> AnalysisConfig:
    if uploaded_file is None:
        return load_config(None)
    with tempfile.NamedTemporaryFile("wb", suffix=".yaml", delete=False) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = Path(tmp.name)
    try:
        return load_config(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _attach_stream_handler(logger: logging.Logger) -> io.StringIO:
    buffer = io.StringIO()
    for existing in list(logger.handlers):
        if getattr(existing, "name", "") == "streamlit":
            logger.removeHandler(existing)
    handler = logging.StreamHandler(buffer)
    handler.set_name("streamlit")
    handler.setFormatter(
        logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(handler)
    return buffer


st.sidebar.header("Configuration")
config_file = st.sidebar.file_uploader("Optional config.yaml", type=["yaml", "yml"])
config = _load_uploaded_config(config_file)
logger = configure_logging(config.log_dir)
log_buffer = _attach_stream_handler(logger)

uploaded_workbook = st.file_uploader("Upload Excel workbook", type=["xlsx", "xlsm"])

if uploaded_workbook:
    with tempfile.NamedTemporaryFile("wb", suffix=".xlsx", delete=False) as tmp:
        tmp.write(uploaded_workbook.getvalue())
        workbook_path = Path(tmp.name)

    try:
        result = analyze_workbook(workbook_path, config, audit_logger=logger)
    finally:
        workbook_path.unlink(missing_ok=True)

    st.success("Analysis completed")
    st.subheader("Workbook metadata")
    st.json(
        {
            "workbook": uploaded_workbook.name,
            "generated_at": result.generated_at.isoformat(),
            "missing_sheets": result.missing_sheets,
            "metadata": result.metadata,
        }
    )

    st.subheader("Sheet metrics")
    df = pd.DataFrame(
        [
            {
                "Sheet": metrics.name,
                "Total Cells": metrics.total_cells,
                "Formula Cells": metrics.formula_cells,
                "Empty Cells": metrics.empty_cells,
                "Error Cells": metrics.error_cells,
                "Issues": "\n".join(metrics.issues) if metrics.issues else "",
            }
            for metrics in result.sheet_metrics.values()
        ]
    )
    st.dataframe(df, use_container_width=True)

    st.subheader("Download report")
    report_data = json.dumps(result.to_dict(), indent=2)
    st.download_button(
        label="Download JSON report",
        data=report_data,
        file_name=f"analysis_{uploaded_workbook.name}.json",
        mime="application/json",
    )

    st.subheader("Audit log")
    log_buffer.seek(0)
    st.code(log_buffer.read() or "No log entries recorded.")
else:
    st.info("Upload an Excel workbook to begin the analysis.")
