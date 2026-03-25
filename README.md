# CO₂ Emissions — Data Cleaning & Exploratory Analysis

A full data pipeline project covering raw data ingestion, systematic cleaning, anomaly detection, exploratory visualizations, and a **second, interactive track** with a reusable **country dashboard** module — all using a real-world CO₂ emissions dataset.

---

## Overview

This project works with the **World Bank CO₂ emissions per capita dataset (1990–2019)**, covering 191 countries across 7 world regions.

The main goals:

- Identify and fix data quality issues  
- Validate country codes against **ISO 3166 Alpha-3**  
- Detect anomalous year-over-year spikes  
- Explore emission trends with static and animated visualizations  
- **(Interactive track)** Run a shorter cleaning slice in a documented notebook and explore **one country at a time** via the `CountryProfile` Python class (tables + charts, including **regional comparison** with the selected country highlighted)

---

## Project structure

```
co2-emissions-cleaning-analysis/
│
├── data/
│   ├── raw/
│   │   └── co2_Emissions.xlsx              # Original dataset (never modified)
│   ├── processed/
│   │   ├── Co2_Emission_cleaned.xlsx       # After cleaning (main pipeline)
│   │   ├── Co2_Emission_pre_drop.xlsx      # Input for the interactive notebook
│   │   ├── Co2_Emission_with_code.xlsx     # Exported from interactive nb; read by CountryProfile
│   │   └── df2_sorted_interpolated.xlsx    # After interpolation, sorted (main pipeline)
│   └── output/
│       ├── differences_alpha3_vs_df.xlsx   # ISO 3166 validation results
│       ├── Highest_spikes.xlsx             # Flagged anomalies
│       └── co2_race.gif                    # Bar chart race animation
│
├── notebook/
│   ├── co2_EDA.ipynb                       # Full EDA & cleaning narrative (main)
│   └── co2_EDA_interactive.ipynb           # Interactive “v2” notebook + CountryProfile demo
│
├── src/
│   ├── __init__.py
│   └── country_profile.py                  # CountryProfile + country_reference_table()
│
├── references/
│   └── iso3166.csv                         # ISO 3166 country code reference
│
├── pyrightconfig.json                      # Extra paths for editors (e.g. Pylance / src)
└── README.md
```

---

## Pipeline (main notebook — `co2_EDA.ipynb`)

### 1. Dataset overview
Initial exploration: shape, dtypes, basic statistics, missing-value patterns.

### 2. Data cleaning
- Removed rows where all emission values were null  
- Identified and dropped a duplicate `2019` column  
- Checked for duplicate rows  
- Validated country codes against **ISO 3166 Alpha-3** — flagged mismatches and corrected the erroneous “tokyo” / Mali code case  
- Dropped auxiliary columns no longer needed after validation  

### 3. Missing values & interpolation
- Identified NaNs in emission time series  
- **Linear interpolation** along years, limited to internal gaps (e.g. up to 3 consecutive years in the documented workflow)  
- Custom spike detection (`find_spikes()`): extreme year-over-year changes  
- Corrected Mali’s 1996 zero (data entry error); left Mauritania’s 1992–1993 spike flagged but unchanged (documented real-world context)  

### 4. Exploratory analysis
- Top emitters (all time and latest year)  
- Emissions by region (pie) and regional trends over time  
- Bar chart race (top emitters over years)  

---

## Interactive notebook & `CountryProfile` (`co2_EDA_interactive.ipynb` + `src/country_profile.py`)

This is a **streamlined second path**: it starts from **`Co2_Emission_pre_drop.xlsx`**, documents each step in **Markdown** (load data, column cleanup, missing-value audit, imputation, export), then wires in Python code.

### What the interactive notebook does
- Drops redundant metadata columns (e.g. `Indicator Name`), isolates **year columns**, lists rows still missing values  
- Applies **linear interpolation** along the year axis with controlled limits  
- **Exports** `data/processed/Co2_Emission_with_code.xlsx` **only if the file does not exist** (avoids accidental overwrite)  
- Adds **`src/`** to `sys.path` so the notebook can `import` the local module  
- Includes a **Help** section: runs **`country_reference_table()`** so users see every **country name**, **ISO Alpha-3 code**, and **region** before choosing a code  
- Demonstrates **`CountryProfile("<CODE>").show_analysis()`** for a single country  

### What `country_profile.py` provides

| Piece | Role |
|--------|------|
| **`country_reference_table()`** | Returns a sorted `DataFrame` (`Country`, `country_code`, `Region`) from the same Excel file the class uses — lookup for `CountryProfile("XXX")`. |
| **`CountryProfile(code)`** | Loads `Co2_Emission_with_code.xlsx` via **`Path(__file__)`** (stable path regardless of notebook working directory), filters one row by **ISO Alpha-3** (case-insensitive). |
| **`emission_summary()`** | One-row `DataFrame`: `mean`, `median`, `missing_years`. |
| **`rank_in_world_by_total()`** | One-row `DataFrame`: `rank_world` and `rank_in_region` as **`position/total`**, plus **`share_of_world`** as a readable **`%`** string. |
| **`pct_of_world_total()`** | Same share as a **float** (0–100) for programmatic use. |
| **`plot_emissions_over_time()`** | Single-country line chart (styled highlight). |
| **`plot_region_peers_over_time()`** | All countries in the **same region** in gray; **selected country** drawn on top in a strong highlight style. |
| **`show_analysis()`** | Prints country label, shows summary tables (HTML without index in Jupyter), and plots **two panels**: solo country + regional context. |

**Note:** ranks are by **sum of yearly values** in the sheet (same rule for every country). The **share of world** is relative to that summed metric; with per-capita columns it is **not** the same as “share of global tonnes” unless your sheet represents that.

---

## Technologies

| Tool | Usage |
|------|--------|
| Python 3 | Core language |
| Pandas | Data manipulation and cleaning |
| NumPy | Numerical operations |
| Matplotlib | Static visualizations |
| openpyxl | Reading/writing `.xlsx` with pandas |
| bar_chart_race | Animated bar chart race (main notebook) |
| Jupyter Notebook | Interactive development |

---

## How to run

1. Clone the repository:

```bash
git clone https://github.com/your-username/co2-emissions-cleaning-analysis.git
cd co2-emissions-cleaning-analysis
```

2. Install dependencies:

```bash
pip install pandas numpy matplotlib openpyxl bar_chart_race
```

3. **Main pipeline & full EDA** — open and run from the repo (kernel **working directory** should allow paths like `data/` as used in the notebook, or adjust paths to match your setup):

```bash
jupyter notebook notebook/co2_EDA.ipynb
```

4. **Interactive notebook + country dashboard** — use the **`notebook/`** folder as the kernel working directory so relative paths like `../data/processed/...` resolve correctly:

```bash
jupyter notebook notebook/co2_EDA_interactive.ipynb
```

Run cells **top to bottom** at least through the export step so **`Co2_Emission_with_code.xlsx`** exists before importing **`CountryProfile`** or calling **`country_reference_table()`**.

> The main notebook may skip re-generating some artifacts if output files already exist under `data/`.

---

## Dataset source

World Bank — CO₂ emissions (metric tons per capita). Example mirror: [Kaggle — CO2 emission around the world](https://www.kaggle.com/datasets/koustavghosh149/co2-emission-around-the-world?resource=download).
