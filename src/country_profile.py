"""
Country-level helpers for the CO₂ emissions dataset.

Loads the processed Excel file, filters one country by ISO Alpha-3 code, and exposes
summary stats, world ranking, and plots. See the main notebook for the full cleaning pipeline.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes

# Columns that are not year-by-year emissions (everything else is treated as a year column).
_META_COLS = frozenset({"Country", "Region", "country_code"})

# Visual style: selected country always pops; peers stay in the background.
_HIGHLIGHT_COLOR = "#b71c1c"
_HIGHLIGHT_EDGE = "#ffffff"
_PEER_COLOR = "#9e9e9e"
_PEER_ALPHA = 0.5
_PEER_LINEWIDTH = 1.0
_HIGHLIGHT_LINEWIDTH = 2.6
_HIGHLIGHT_MARKERSIZE = 6
_HIGHLIGHT_MARKER_EDGES = 0.9

_STYLE_LOCK = False


def _ensure_matplotlib_style() -> None:
    """One-time rcParams so charts look consistent without requiring seaborn."""
    global _STYLE_LOCK
    if _STYLE_LOCK:
        return
    plt.rcParams.update(
        {
            "figure.facecolor": "#f8f9fa",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#cfd8dc",
            "axes.labelcolor": "#263238",
            "axes.titlecolor": "#1a237e",
            "axes.titleweight": "600",
            "axes.linewidth": 0.8,
            "axes.axisbelow": True,
            "axes.grid": True,
            "grid.color": "#eceff1",
            "grid.linestyle": "-",
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.size": 10,
            "legend.frameon": True,
            "legend.framealpha": 0.96,
            "legend.edgecolor": "#eceff1",
            "xtick.color": "#455a64",
            "ytick.color": "#455a64",
        }
    )
    _STYLE_LOCK = True


def _style_axes(ax: Axes) -> None:
    """Remove chart junk, keep a light frame."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#b0bec5")
    ax.spines["bottom"].set_color("#b0bec5")


# Display: few decimals for emissions stats; world share always with a % sign.
_SUMMARY_DECIMALS = 3
_PCT_DECIMALS = 2


def _format_share_pct(pct_value: float | None) -> str:
    """Turn a 0–100 scale share into a readable percentage string."""
    if pct_value is None or pd.isna(pct_value):
        return "—"
    return f"{float(pct_value):.{_PCT_DECIMALS}f}%"


def _processed_excel_path() -> Path:
    """Path to ``Co2_Emission_with_code.xlsx`` (project root / data / processed)."""
    return (
        Path(__file__).resolve().parent.parent
        / "data"
        / "processed"
        / "Co2_Emission_with_code.xlsx"
    )


def country_reference_table() -> pd.DataFrame:
    """
    Lookup table: country name, ISO Alpha-3 code, and region — sorted by country name.

    Use this to pick the code passed to ``CountryProfile("<code>")``. Reads the same
    processed workbook as ``CountryProfile`` (via ``Path(__file__)``, not the notebook cwd).
    """
    path = _processed_excel_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"Processed file not found: {path}. Export it from the notebook first."
        )
    df = pd.read_excel(path, usecols=["Country", "country_code", "Region"])
    df = df.copy()
    df["country_code"] = df["country_code"].astype(str).str.strip().str.upper()
    return df.sort_values("Country", kind="stable").reset_index(drop=True)


def _display_frames(*frames: pd.DataFrame) -> None:
    """Show tables without the index column; friendly number formatting in notebooks."""
    try:
        from IPython.display import HTML, display

        for df in frames:
            display(
                HTML(
                    df.to_html(
                        index=False,
                        escape=False,
                        na_rep="—",
                        float_format=lambda x: (
                            "—"
                            if pd.isna(x)
                            else format(float(x), f",.{_SUMMARY_DECIMALS}f")
                        ),
                    )
                )
            )
    except ImportError:
        for df in frames:
            print(df.to_string(index=False))
            print()


class CountryProfile:
    """
    One country, one row of data, plus access to the full table for comparisons.

    Attributes
    ----------
    country_code : str
        Normalized Alpha-3 code (e.g. "BRA").
    df : DataFrame
        Single-row slice for this country (all columns).
    _full_df : DataFrame
        Entire dataset — needed to rank the country against everyone else.
    year_cols : list
        Column names for each year (int years in the Excel).
    emissions_by_year : Series
        Index = year, values = emissions for this country only.
    region : object
        Region label from the dataset (same row as the client country).
    """

    def __init__(self, country_code: str):
        # Normalize so "bra", "BRA", " Bra " all match the file.
        code = country_code.strip().upper()
        self.country_code = code

        # Path from this file: src/ -> project root -> data/processed/...
        # Using __file__ avoids broken paths when the notebook/kernel cwd is not the repo root.
        data_path = _processed_excel_path()
        df = pd.read_excel(data_path)
        self._full_df = df.copy()

        mask = df["country_code"].astype(str).str.strip().str.upper() == code
        self.df = df.loc[mask].copy()
        if self.df.empty:
            raise ValueError(f"No row found for country code {code!r}")

        self.year_cols = [c for c in df.columns if c not in _META_COLS]
        if not self.year_cols:
            raise ValueError("No year columns left after skipping metadata columns.")

        # One row -> one Series over time; index as int years for cleaner plots/labels.
        self.emissions_by_year = self.df[self.year_cols].iloc[0]
        self.emissions_by_year.index = self.emissions_by_year.index.astype(int)

        # Keep region for filtering peer countries in the same geographic group on comparison plots.
        self.region = self.df["Region"].iloc[0]

    def emission_summary(self) -> pd.DataFrame:
        """
        Descriptive stats on this country's time series (across years).

        Returns
        -------
        One-row DataFrame: ``mean`` / ``median`` rounded for readability, ``missing_years`` as int.
        """
        s = self.emissions_by_year
        mean_v = s.mean()
        med_v = s.median()
        row = {
            "mean": round(float(mean_v), _SUMMARY_DECIMALS) if pd.notna(mean_v) else np.nan,
            "median": round(float(med_v), _SUMMARY_DECIMALS) if pd.notna(med_v) else np.nan,
            "missing_years": int(s.isna().sum()),
        }
        return pd.DataFrame([row])

    def rank_in_world_by_total(self) -> pd.DataFrame:
        """
        Ranks by sum of emissions over all year columns (same rule for every country).

        Returns one row with:

        - ``rank_world``: ``\"91/191\"`` style (position among all countries / total countries).
        - ``rank_in_region``: same within the country's region, or ``\"—\"`` if region is missing.
        - ``share_of_world``: same metric as ``pct_of_world_total()``, formatted as e.g. ``\"2.35%\"``.
        """
        full = self._full_df
        idx = self.df.index[0]
        totals = full[self.year_cols].sum(axis=1)

        ranked_world = totals.rank(ascending=False, method="min")
        pos_w = int(ranked_world.loc[idx])
        n_world = int(len(totals))
        rank_world = f"{pos_w}/{n_world}"

        if pd.isna(self.region):
            rank_in_region = "—"
        else:
            reg_mask = full["Region"].eq(self.region)
            regional_totals = totals.loc[reg_mask]
            ranked_reg = regional_totals.rank(ascending=False, method="min")
            pos_r = int(ranked_reg.loc[idx])
            n_reg = int(len(regional_totals))
            rank_in_region = f"{pos_r}/{n_reg}"

        country_total = float(self.emissions_by_year.sum())
        world_total = float(totals.sum())
        if world_total and pd.notna(world_total):
            pct_num = 100.0 * country_total / world_total
        else:
            pct_num = None
        share_str = _format_share_pct(pct_num)

        return pd.DataFrame(
            [
                {
                    "rank_world": rank_world,
                    "rank_in_region": rank_in_region,
                    "share_of_world": share_str,
                }
            ]
        )

    def pct_of_world_total(self) -> float:
        """
        Share of the global sum of (per-country totals over years), as float 0–100.

        Same quantity as the ``share_of_world`` string in ``rank_in_world_by_total`` (display format).

        Note: with per-capita input columns, this is not the same as share of global tonnes;
        it is the share of the summed metric used in this dataset.
        """
        country_total = self.emissions_by_year.sum()
        world_total = self._full_df[self.year_cols].sum(axis=1).sum()
        if not world_total or pd.isna(world_total):
            return float("nan")
        return float(100.0 * float(country_total) / float(world_total))

    def _series_for_row(self, row) -> pd.Series:
        """Year-by-year series from one DataFrame row (same shape as ``emissions_by_year``)."""
        s = row[self.year_cols].copy()
        s.index = s.index.astype(int)
        return s.astype(float)

    def _plot_highlight_line(self, ax: Axes, x, y, *, label: str) -> None:
        """Selected country: strong line + markers with light edge so it reads on busy charts."""
        xa = np.asarray(x, dtype=float)
        ya = np.asarray(y, dtype=float)
        ax.plot(
            xa,
            ya,
            color=_HIGHLIGHT_COLOR,
            linewidth=_HIGHLIGHT_LINEWIDTH,
            marker="o",
            markersize=_HIGHLIGHT_MARKERSIZE,
            markeredgecolor=_HIGHLIGHT_EDGE,
            markeredgewidth=_HIGHLIGHT_MARKER_EDGES,
            zorder=5,
            label=label,
        )

    def plot_emissions_over_time(self, ax=None):
        """
        Line chart of this country's emissions by year (only this country).

        Uses the same color/weight as the regional chart so the selected country stays visually
        consistent when switching between views.

        Parameters
        ----------
        ax : matplotlib Axes, optional
            Draw on an existing axes; if None, a new figure is created.

        Returns
        -------
        The Axes used for plotting (useful to tweak labels or savefig).
        """
        _ensure_matplotlib_style()
        if ax is None:
            _, ax = plt.subplots(figsize=(10, 4.2))
        country_name = self.df["Country"].iloc[0]
        self._plot_highlight_line(
            ax,
            self.emissions_by_year.index,
            self.emissions_by_year.values,
            label=country_name,
        )
        ax.set_title(f"{country_name} — CO₂ (per capita) over time", pad=12)
        ax.set_xlabel("Year")
        ax.set_ylabel("CO₂ per capita (dataset units)")
        ax.legend(loc="upper left", frameon=True)
        _style_axes(ax)
        ax.grid(True, axis="y", alpha=0.35)
        return ax

    def plot_region_peers_over_time(self, ax=None):
        """
        Time series for all countries in the same region, with the client's country highlighted.

        Peers are drawn first (gray, thin, semi-transparent) for context; the selected country is
        drawn last (red, thick, higher zorder) so its line is never hidden behind the others.
        """
        _ensure_matplotlib_style()
        if ax is None:
            _, ax = plt.subplots(figsize=(12, 5.2))

        full = self._full_df
        client_idx = self.df.index[0]
        country_name = self.df["Country"].iloc[0]

        # No valid region: nothing to compare against — show only the client with a note in the title.
        if pd.isna(self.region):
            self._plot_highlight_line(
                ax,
                self.emissions_by_year.index,
                self.emissions_by_year.values,
                label=country_name,
            )
            ax.set_title(
                f"{country_name} — CO₂ per capita (no region in data; regional comparison unavailable)",
                pad=12,
            )
            ax.set_xlabel("Year")
            ax.set_ylabel("CO₂ per capita (dataset units)")
            ax.legend(loc="best")
            _style_axes(ax)
            ax.grid(True, axis="y", alpha=0.35)
            return ax

        # Same region as the client, excluding the client's own row.
        same_region = full["Region"].eq(self.region)
        peer_rows = full.loc[same_region & (full.index != client_idx)]

        # Sort peers by country name so draw order is stable and reproducible.
        for _, row in peer_rows.sort_values("Country").iterrows():
            s = self._series_for_row(row)
            # Background layer: many gray lines form a regional "envelope" without stealing focus.
            ax.plot(
                np.asarray(s.index, dtype=float),
                np.asarray(s.values, dtype=float),
                color=_PEER_COLOR,
                linewidth=_PEER_LINEWIDTH,
                alpha=_PEER_ALPHA,
                zorder=1,
            )

        # Foreground layer: client's country — always on top with its own legend entry.
        self._plot_highlight_line(
            ax,
            self.emissions_by_year.index,
            self.emissions_by_year.values,
            label=f"{country_name} (selected)",
        )

        n_peers = len(peer_rows)
        if n_peers == 0:
            peer_note = "no other countries in region"
        elif n_peers == 1:
            peer_note = "1 peer country in region"
        else:
            peer_note = f"{n_peers} peer countries in region"
        ax.set_title(
            f"Region: {self.region} — CO₂ per capita | {country_name} highlighted ({peer_note})",
            pad=12,
        )
        ax.set_xlabel("Year")
        ax.set_ylabel("CO₂ per capita (dataset units)")
        # Legend proxy: one gray entry stands in for all background lines (keeps the legend small).
        if n_peers > 0:
            ax.plot(
                [],
                [],
                color=_PEER_COLOR,
                linewidth=_PEER_LINEWIDTH,
                alpha=_PEER_ALPHA,
                label="Other countries in region",
            )
        ax.legend(loc="best", ncol=1)
        _style_axes(ax)
        ax.grid(True, axis="y", alpha=0.35)
        return ax

    def show_analysis(self) -> None:
        """
        Show summary tables as DataFrames and a two-panel figure:
        (1) selected country only, highlighted; (2) same country with regional peers for context.
        """
        print(f"Country: {self.df['Country'].iloc[0]} ({self.country_code})")
        _display_frames(self.emission_summary(), self.rank_in_world_by_total())
        _ensure_matplotlib_style()
        fig, axes = plt.subplots(2, 1, figsize=(10, 8.2), constrained_layout=True)
        self.plot_emissions_over_time(ax=axes[0])
        self.plot_region_peers_over_time(ax=axes[1])
        plt.show()
