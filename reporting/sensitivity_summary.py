"""Utilities for generating scenario sensitivity summaries.

This module provides a high level helper function for summarising core
financial metrics such as Net Present Value (NPV) and Internal Rate of Return
(IRR) across multiple scenarios.  The output includes a tidy pandas
``DataFrame`` along with an optional visualisation produced via either
Matplotlib or Plotly.  Convenience helpers are included to persist the results
in multiple formats (Excel, HTML table, static image).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple, Union

import math

import pandas as pd

try:  # pragma: no cover - optional dependency
    import plotly.express as px
except Exception:  # pragma: no cover - Plotly is optional at runtime
    px = None  # type: ignore

try:  # pragma: no cover - matplotlib is optional
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None  # type: ignore

Number = Union[int, float]
ScenarioRecords = Union[pd.DataFrame, Sequence[Mapping[str, object]]]


@dataclass
class ScenarioConfig:
    """Configuration for a scenario used in IRR/NPV calculations."""

    name: str
    cash_flows: Sequence[Number]
    discount_rate: float

    def present_value(self, rate: float) -> float:
        """Compute the Net Present Value for the scenario."""

        return sum(
            cf / math.pow(1 + rate, period)
            for period, cf in enumerate(self.cash_flows)
        )

    def irr(self, guess: float = 0.1, tol: float = 1e-6, max_iter: int = 100) -> Optional[float]:
        """Compute the Internal Rate of Return using Newton-Raphson.

        Parameters
        ----------
        guess:
            Initial guess for the IRR calculation.
        tol:
            Termination tolerance for the iteration.
        max_iter:
            Maximum number of iterations to attempt.

        Returns
        -------
        Optional[float]
            The IRR if the iteration converges, ``None`` otherwise.
        """

        rate = guess
        for _ in range(max_iter):
            npv = 0.0
            d_npv = 0.0
            for period, cf in enumerate(self.cash_flows):
                discount_factor = math.pow(1 + rate, period)
                npv += cf / discount_factor
                if period:
                    d_npv -= period * cf / (discount_factor * (1 + rate))
            if abs(d_npv) < 1e-12:
                break
            next_rate = rate - npv / d_npv
            if abs(next_rate - rate) < tol:
                return next_rate
            rate = next_rate
        return None


def _normalise_records(
    scenarios: ScenarioRecords,
    default_discount_rate: Optional[float],
) -> List[ScenarioConfig]:
    """Normalise a collection of records into :class:`ScenarioConfig` values."""

    if isinstance(scenarios, pd.DataFrame):
        records = scenarios.to_dict(orient="records")
    else:
        records = list(scenarios)

    normalised: List[ScenarioConfig] = []
    for record in records:
        try:
            name = str(record["scenario"])
            cash_flows = record["cash_flows"]  # type: ignore[assignment]
        except KeyError as exc:  # pragma: no cover - guard clause
            raise KeyError("Each scenario must define 'scenario' and 'cash_flows'.") from exc

        if not isinstance(cash_flows, Sequence):  # pragma: no cover - validation
            raise TypeError("'cash_flows' must be a sequence of numbers.")

        discount_rate = record.get("discount_rate", default_discount_rate)
        if discount_rate is None:
            raise ValueError("A discount rate must be supplied either globally or per scenario.")

        normalised.append(
            ScenarioConfig(
                name=name,
                cash_flows=list(cash_flows),
                discount_rate=float(discount_rate),
            )
        )
    return normalised


def _build_summary_table(scenarios: Sequence[ScenarioConfig]) -> pd.DataFrame:
    """Construct the summary DataFrame for the provided scenarios."""

    rows: List[MutableMapping[str, object]] = []
    for config in scenarios:
        discount_rate = config.discount_rate
        npv = config.present_value(discount_rate)
        irr = config.irr()
        rows.append(
            {
                "scenario": config.name,
                "discount_rate": discount_rate,
                "NPV": npv,
                "IRR": irr,
            }
        )
    summary_df = pd.DataFrame(rows)
    summary_df.set_index("scenario", inplace=True)
    return summary_df


def _create_visualisation(
    summary_df: pd.DataFrame,
    backend: str = "matplotlib",
    chart_title: str = "Scenario sensitivity summary",
    **chart_kwargs: object,
):
    """Create a visualisation of the summary metrics.

    Parameters
    ----------
    summary_df:
        DataFrame with one row per scenario and metrics as columns.
    backend:
        Either ``"matplotlib"`` or ``"plotly"``.
    chart_title:
        Title to display on the chart.

    Returns
    -------
    Union["Figure", Tuple["Figure", "Axes"]]
        The generated figure object.
    """

    chart_kwargs = dict(chart_kwargs)

    long_df = summary_df.reset_index().melt(
        id_vars="scenario",
        value_vars=[col for col in summary_df.columns if col not in {"discount_rate"}],
        var_name="metric",
        value_name="value",
    )

    backend = backend.lower()
    if backend == "plotly":
        if px is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("Plotly is not installed; install plotly to use this backend.")
        fig = px.bar(
            long_df,
            x="scenario",
            y="value",
            color="metric",
            barmode="group",
            title=chart_title,
            **chart_kwargs,
        )
        return fig

    if backend != "matplotlib":  # pragma: no cover - validation
        raise ValueError("backend must be either 'matplotlib' or 'plotly'.")

    if plt is None:  # pragma: no cover - optional dependency guard
        raise RuntimeError(
            "matplotlib is not installed; install matplotlib to use the matplotlib backend."
        )

    figsize = chart_kwargs.pop("figsize", (10, 6))
    fig, ax = plt.subplots(figsize=figsize)
    metrics = [col for col in summary_df.columns if col not in {"discount_rate"}]
    x = range(len(summary_df))
    width = 0.8 / max(len(metrics), 1)
    for idx, metric in enumerate(metrics):
        offsets = [i + idx * width for i in x]
        ax.bar(offsets, summary_df[metric], width=width, label=metric)
    ax.set_xticks([i + (len(metrics) - 1) * width / 2 for i in x])
    ax.set_xticklabels(summary_df.index)
    ax.set_title(chart_title)
    ax.set_ylabel("Value")
    ax.legend()
    fig.tight_layout()
    return fig


def _save_outputs(
    summary_df: pd.DataFrame,
    figure,
    output_formats: Optional[Iterable[str]],
    output_path: Union[str, Path],
    backend: str,
) -> Mapping[str, Path]:
    """Persist the generated outputs to disk."""

    if not output_formats:
        return {}

    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: dict[str, Path] = {}
    for fmt in output_formats:
        fmt = fmt.lower()
        if fmt == "excel":
            path = output_dir / "sensitivity_summary.xlsx"
            summary_df.to_excel(path)
            saved_paths[fmt] = path
        elif fmt == "html":
            path = output_dir / "sensitivity_summary.html"
            summary_df.to_html(path)
            saved_paths[fmt] = path
        elif fmt == "image":
            path = output_dir / "sensitivity_summary.png"
            if backend == "plotly":
                if hasattr(figure, "write_image"):
                    figure.write_image(str(path))
                else:  # pragma: no cover - Plotly image export optional dep
                    raise RuntimeError(
                        "Plotly figure cannot be saved as an image without kaleido or orca installed."
                    )
            else:
                figure.savefig(path)
            saved_paths[fmt] = path
        else:  # pragma: no cover - validation
            raise ValueError(f"Unsupported output format: {fmt}")

    return saved_paths


def generate_sensitivity_summary(
    scenario_records: ScenarioRecords,
    *,
    default_discount_rate: Optional[float] = None,
    backend: str = "matplotlib",
    output_formats: Optional[Iterable[str]] = None,
    output_path: Union[str, Path] = "reports",
    chart_title: str = "Scenario sensitivity summary",
    **chart_kwargs: object,
) -> Tuple[pd.DataFrame, object, Mapping[str, Path]]:
    """Aggregate key metrics across scenarios and produce a summary report.

    Parameters
    ----------
    scenario_records:
        Iterable of dictionaries/DataFrame rows describing the scenarios. Each
        record must contain ``scenario`` (name) and ``cash_flows`` (sequence of
        cashflows).  A per-scenario ``discount_rate`` can optionally be
        provided.
    default_discount_rate:
        Discount rate applied when a scenario does not include
        ``discount_rate``.  When omitted, each scenario must provide its own
        rate.
    backend:
        Visualisation backend to use (``"matplotlib"`` or ``"plotly"``).
    output_formats:
        Iterable of desired output formats. Supported values are ``"excel"``,
        ``"html"`` and ``"image"``.
    output_path:
        Directory in which to store generated outputs.
    chart_title:
        Title for the generated chart.
    **chart_kwargs:
        Additional keyword arguments forwarded to the plotting backend.

    Returns
    -------
    tuple[pandas.DataFrame, object, dict[str, pathlib.Path]]
        A tuple containing the summary table, the generated figure and a mapping
        of any saved outputs.
    """

    if default_discount_rate is None and isinstance(scenario_records, pd.DataFrame):
        # Allow DataFrame level attribute
        default_discount_rate = scenario_records.attrs.get("default_discount_rate")

    scenarios = _normalise_records(
        scenario_records,
        default_discount_rate=default_discount_rate,
    )

    summary_df = _build_summary_table(scenarios)
    figure = _create_visualisation(summary_df, backend=backend, chart_title=chart_title, **chart_kwargs)
    saved_paths = _save_outputs(
        summary_df,
        figure,
        output_formats,
        output_path,
        backend=backend,
    )

    return summary_df, figure, saved_paths


__all__ = ["generate_sensitivity_summary"]
