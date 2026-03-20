# CO₂ Emissions — Data Cleaning & Exploratory Analysis

A full data pipeline project covering raw data ingestion, systematic cleaning, anomaly detection, and exploratory visualizations using a real-world CO₂ emissions dataset.

---

## Overview

This project works with the **World Bank CO₂ emissions per capita dataset (1990–2019)**, covering 191 countries across 7 world regions.

The goal is to demonstrate a complete data analysis workflow:
- Identifying and fixing data quality issues
- Validating country codes against an international standard (ISO 3166)
- Detecting anomalous year-over-year spikes
- Exploring emission trends through meaningful visualizations

---

## Project Structure

```
co2-emissions-cleaning-analysis/
│
├── data/
│   ├── raw/
│   │   └── co2_Emissions.xlsx              # Original dataset (never modified)
│   ├── processed/
│   │   ├── Co2_Emission_cleaned.xlsx       # After cleaning
│   │   └── df2_sorted_interpolated.xlsx    # After interpolation, sorted
│   └── output/
│       ├── differences_alpha3_vs_df.xlsx   # ISO 3166 validation results
│       ├── Highest_spikes.xlsx             # Flagged anomalies
│       └── co2_race.gif                    # Bar chart race animation
│
├── notebook/
│   └── co2_EDA.ipynb                       # Main analysis notebook
│
├── references/
│   └── iso3166.csv                         # ISO 3166 country code reference
│
└── README.md
```

---

## Pipeline

### 1. Dataset Overview
Initial exploration: shape, data types, basic statistics and missing value distribution.

### 2. Data Cleaning
- Removed rows where all emission values were null
- Identified and dropped a duplicate `2019` column
- Checked for duplicate rows
- Validated country codes against **ISO 3166 Alpha-3** — flagged mismatches and corrected the only true error found (country listed as "tokyo" with Mali's country code)
- Dropped auxiliary columns no longer needed after validation

### 3. Missing Values & Interpolation
- Identified NaN values within emission time series
- Applied **linear interpolation** restricted to internal gaps of up to 3 consecutive years
- Built a custom `find_spikes()` function to detect extreme year-over-year changes (> +11,100% or < -99.1%)
- Corrected Mali's zero value in 1996 (data entry error)
- Kept Mauritania's 1992–1993 anomaly flagged but unchanged, as it is consistent with documented real-world events

### 4. Exploratory Data Analysis
- Top 5 emitters — all time and 2019
- Total emissions by region (pie chart)
- Regional emissions over time (line chart, 1990–2019)
- Bar chart race — top 10 emitters animated across all years

---

## Technologies

| Tool | Usage |
|---|---|
| Python 3 | Core language |
| Pandas | Data manipulation and cleaning |
| NumPy | Numerical operations |
| Matplotlib | Static visualizations |
| bar_chart_race | Animated bar chart race |
| Jupyter Notebook | Interactive development environment |

---

## How to Run

1. Clone the repository:
```bash
git clone https://github.com/your-username/co2-emissions-cleaning-analysis.git
```

2. Install dependencies:
```bash
pip install pandas numpy matplotlib bar_chart_race
```

3. Open the notebook:
```bash
jupyter notebook notebook/co2_EDA.ipynb
```

> The notebook will automatically skip re-generating files that already exist in `data/`.

---

## Dataset Source

World Bank — CO₂ emissions (kt) per capita, available on [Kaggle]([https://www.kaggle.com/](https://www.kaggle.com/datasets/koustavghosh149/co2-emission-around-the-world?resource=download)).
