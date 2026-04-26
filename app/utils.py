"""Utility functions for data processing and visualization."""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

COUNTRIES = ["Ethiopia", "Kenya", "Sudan", "Tanzania", "Nigeria"]

NUMERIC_COLS = [
    "T2M", "T2M_MAX", "T2M_MIN", "T2M_RANGE",
    "PRECTOTCORR", "RH2M", "WS2M", "WS2M_MAX", "PS", "QV2M",
]

VARIABLE_LABELS = {
    "T2M": "Mean Temperature (°C)",
    "T2M_MAX": "Max Temperature (°C)",
    "T2M_MIN": "Min Temperature (°C)",
    "T2M_RANGE": "Temperature Range (°C)",
    "PRECTOTCORR": "Precipitation (mm/day)",
    "RH2M": "Relative Humidity (%)",
    "WS2M": "Wind Speed (m/s)",
    "WS2M_MAX": "Max Wind Speed (m/s)",
    "QV2M": "Specific Humidity (g/kg)",
}

COLORS = {
    "Ethiopia": "#E63946",
    "Kenya": "#2A9D8F",
    "Sudan": "#E9C46A",
    "Tanzania": "#264653",
    "Nigeria": "#F4A261",
}


def load_country(country: str) -> pd.DataFrame | None:
    """Load the cleaned CSV for a given country. Returns None if not found."""
    path = DATA_DIR / f"{country.lower()}_clean.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, parse_dates=["Date"])
    df["Country"] = country
    if "Month" not in df.columns:
        df["Month"] = df["Date"].dt.month
    if "Year" not in df.columns:
        df["Year"] = df["Date"].dt.year
    return df


def load_all(countries: list[str]) -> pd.DataFrame:
    """Load and concatenate cleaned CSVs for selected countries."""
    frames = [load_country(c) for c in countries]
    frames = [f for f in frames if f is not None]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def monthly_agg(df: pd.DataFrame, variable: str) -> pd.DataFrame:
    """Aggregate daily data to monthly means / totals."""
    agg_fn = "sum" if variable == "PRECTOTCORR" else "mean"
    monthly = (
        df.groupby(["Country", "Year", "Month"])[variable]
        .agg(agg_fn)
        .reset_index()
    )
    monthly["YearMonth"] = pd.to_datetime(monthly[["Year", "Month"]].assign(day=1))
    return monthly.sort_values("YearMonth")


def annual_agg(df: pd.DataFrame, variable: str) -> pd.DataFrame:
    agg_fn = "sum" if variable == "PRECTOTCORR" else "mean"
    return df.groupby(["Country", "Year"])[variable].agg(agg_fn).reset_index()


def compute_warming_trend(df: pd.DataFrame, country: str) -> float:
    """Return °C / decade warming trend for T2M via OLS."""
    sub = df[df["Country"] == country].dropna(subset=["T2M"])
    if len(sub) < 2:
        return 0.0
    x = (sub["Date"] - sub["Date"].min()).dt.days.values
    y = sub["T2M"].values
    slope, *_ = np.polyfit(x, y, 1)
    return slope * 365.25 * 10  # °C per decade


def extreme_heat_days(df: pd.DataFrame, threshold: float = 35.0) -> pd.DataFrame:
    return (
        df[df["T2M_MAX"] > threshold]
        .groupby(["Country", "Year"])
        .size()
        .reset_index(name="extreme_heat_days")
    )


def max_consecutive_dry_days(series: pd.Series, threshold: float = 1.0) -> int:
    is_dry = (series < threshold).astype(int).values
    max_run = run = 0
    for v in is_dry:
        run = run + 1 if v else 0
        max_run = max(max_run, run)
    return max_run
