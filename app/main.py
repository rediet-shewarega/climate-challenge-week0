"""
African Climate Trend Analysis — Streamlit Dashboard
COP32 Preparatory Analysis | EthioClimate Analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# Allow import of utils from same directory
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    COUNTRIES, VARIABLE_LABELS, COLORS,
    load_all, monthly_agg, annual_agg,
    compute_warming_trend, extreme_heat_days, max_consecutive_dry_days,
)

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="African Climate Trends | COP32",
    page_icon="🌍",
    layout="wide",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main-header { font-size:2rem; font-weight:700; color:#E63946; margin-bottom:0; }
  .sub-header  { font-size:0.95rem; color:#666; margin-top:0; }
  .metric-card { background:#f8f9fa; border-radius:8px; padding:12px 18px;
                 border-left:4px solid #E63946; }
  div[data-testid="metric-container"] { background:#f8f9fa; border-radius:8px;
                                         padding:10px; }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">🌍 African Climate Trend Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">COP32 Preparatory Analysis · Ethiopia, Kenya, Sudan, Tanzania, Nigeria · NASA POWER 2015–2026</p>', unsafe_allow_html=True)
st.divider()

# ─── Sidebar Controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Flag_of_Ethiopia.svg/200px-Flag_of_Ethiopia.svg.png", width=80)
    st.title("Dashboard Controls")

    selected_countries = st.multiselect(
        "Select Countries",
        options=COUNTRIES,
        default=COUNTRIES,
        help="Filter the analysis by country",
    )

    year_range = st.slider(
        "Year Range",
        min_value=2015,
        max_value=2026,
        value=(2015, 2026),
        step=1,
    )

    variable = st.selectbox(
        "Climate Variable",
        options=list(VARIABLE_LABELS.keys()),
        format_func=lambda v: VARIABLE_LABELS[v],
        index=0,
    )

    heat_threshold = st.slider(
        "Extreme Heat Threshold (°C)",
        min_value=30,
        max_value=45,
        value=35,
        step=1,
        help="T2M_MAX threshold for extreme heat day counting",
    )

    st.divider()
    st.caption("Data: NASA POWER | Analysis: EthioClimate Analytics")

# ─── Load Data ──────────────────────────────────────────────────────────────
if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

with st.spinner("Loading data..."):
    df_raw = load_all(selected_countries)

if df_raw.empty:
    st.error(
        "No cleaned data files found in `data/`. "
        "Run the EDA notebooks first to generate `data/<country>_clean.csv` files."
    )
    st.info("Expected files: " + ", ".join(f"`data/{c.lower()}_clean.csv`" for c in selected_countries))
    st.stop()

# Filter by year range
df = df_raw[(df_raw["Year"] >= year_range[0]) & (df_raw["Year"] <= year_range[1])].copy()
available_countries = df["Country"].unique().tolist()

# ─── KPI Row ────────────────────────────────────────────────────────────────
st.subheader("Key Metrics Snapshot")
kpi_cols = st.columns(len(available_countries))
for col, country in zip(kpi_cols, available_countries):
    sub = df[df["Country"] == country]
    mean_t = sub["T2M"].mean()
    trend = compute_warming_trend(sub, country)
    col.metric(
        label=country,
        value=f"{mean_t:.1f}°C",
        delta=f"{trend:+.2f}°C/decade",
        delta_color="inverse",
    )

st.divider()

# ─── Tab Layout ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Temperature Trends",
    "🌧️ Precipitation",
    "🔥 Extreme Events",
    "🏆 Vulnerability Ranking",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Temperature Trends
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader(f"{VARIABLE_LABELS.get(variable, variable)} — Monthly Trend")

    monthly = monthly_agg(df, variable)

    fig = px.line(
        monthly,
        x="YearMonth",
        y=variable,
        color="Country",
        color_discrete_map=COLORS,
        labels={"YearMonth": "Date", variable: VARIABLE_LABELS.get(variable, variable)},
        title=f"Monthly {VARIABLE_LABELS.get(variable, variable)} — {year_range[0]}–{year_range[1]}",
    )
    fig.update_traces(line_width=2)
    fig.update_layout(height=420, legend_title="Country", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # Summary table
    st.subheader("Summary Statistics")
    summary = df.groupby("Country")[variable].agg(
        Mean="mean", Median="median", Std="std", Min="min", Max="max"
    ).round(3)
    st.dataframe(summary, use_container_width=True)

    # Annual warming trend per country
    st.subheader("Warming Trend (°C / decade)")
    trends = {c: compute_warming_trend(df[df["Country"] == c], c) for c in available_countries}
    trend_df = pd.DataFrame.from_dict(trends, orient="index", columns=["Warming (°C/decade)"]).round(3)
    fig_trend = px.bar(
        trend_df.reset_index().rename(columns={"index": "Country"}),
        x="Country", y="Warming (°C/decade)",
        color="Country", color_discrete_map=COLORS,
        title="Estimated Warming Trend per Country",
    )
    fig_trend.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.4)
    fig_trend.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig_trend, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Precipitation
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Precipitation Distribution by Country")

    fig_box = px.box(
        df[df["PRECTOTCORR"].notna()],
        x="Country",
        y="PRECTOTCORR",
        color="Country",
        color_discrete_map=COLORS,
        points=False,
        labels={"PRECTOTCORR": "Daily Precipitation (mm/day)"},
        title="Daily Precipitation Distribution — All Countries",
    )
    fig_box.update_layout(height=420, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    # Seasonal cycle
    st.subheader("Seasonal Precipitation Cycle")
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    seasonal = df.groupby(["Country", "Month"])["PRECTOTCORR"].mean().reset_index()
    seasonal["MonthName"] = seasonal["Month"].apply(lambda x: month_names[x-1])

    fig_season = px.line(
        seasonal,
        x="Month",
        y="PRECTOTCORR",
        color="Country",
        color_discrete_map=COLORS,
        markers=True,
        labels={"PRECTOTCORR": "Avg Daily Precipitation (mm/day)", "Month": "Month"},
        title="Average Seasonal Precipitation Cycle",
    )
    fig_season.update_xaxes(tickvals=list(range(1, 13)), ticktext=month_names)
    fig_season.update_layout(height=400, hovermode="x unified")
    st.plotly_chart(fig_season, use_container_width=True)

    # Precipitation summary
    st.subheader("Precipitation Summary Statistics")
    prec_summary = df.groupby("Country")["PRECTOTCORR"].agg(
        Mean="mean", Median="median", Std="std",
        **{"90th Percentile": lambda x: x.quantile(0.9)},
    ).round(3)
    st.dataframe(prec_summary, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Extreme Events
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"Extreme Heat Days (T2M_MAX > {heat_threshold}°C)")
        heat = df[df["T2M_MAX"] > heat_threshold].groupby(["Country", "Year"]).size().reset_index(name="days")
        heat_avg = heat.groupby("Country")["days"].mean().reset_index(name="avg_days")

        fig_heat = px.bar(
            heat_avg.sort_values("avg_days", ascending=False),
            x="Country", y="avg_days",
            color="Country", color_discrete_map=COLORS,
            labels={"avg_days": "Avg Days / Year"},
            title=f"Avg Annual Extreme Heat Days (>{heat_threshold}°C)",
        )
        fig_heat.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_b:
        st.subheader("Max Consecutive Dry Days / Year")
        cdd_list = []
        for country in available_countries:
            for year, grp in df[df["Country"] == country].groupby("Year"):
                mcd = max_consecutive_dry_days(grp["PRECTOTCORR"])
                cdd_list.append({"Country": country, "Year": year, "max_cdd": mcd})
        cdd_df = pd.DataFrame(cdd_list)
        cdd_avg = cdd_df.groupby("Country")["max_cdd"].mean().reset_index(name="avg_cdd")

        fig_cdd = px.bar(
            cdd_avg.sort_values("avg_cdd", ascending=False),
            x="Country", y="avg_cdd",
            color="Country", color_discrete_map=COLORS,
            labels={"avg_cdd": "Avg Max Consecutive Dry Days"},
            title="Avg Max Consecutive Dry Days per Year",
        )
        fig_cdd.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig_cdd, use_container_width=True)

    # Heat days time series
    st.subheader("Extreme Heat Days Trend Over Time")
    if not heat.empty:
        fig_heat_time = px.line(
            heat,
            x="Year", y="days",
            color="Country", color_discrete_map=COLORS,
            markers=True,
            labels={"days": f"Extreme Heat Days (>{heat_threshold}°C)"},
            title="Annual Extreme Heat Day Count per Country",
        )
        fig_heat_time.update_layout(height=380)
        st.plotly_chart(fig_heat_time, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — Vulnerability Ranking
# ──────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Composite Climate Vulnerability Ranking")

    temp_mean = df.groupby("Country")["T2M"].mean()
    temp_std = df.groupby("Country")["T2M"].std()
    heat_score = heat_avg.set_index("Country")["avg_days"] if not heat_avg.empty else pd.Series(dtype=float)
    cdd_score = cdd_avg.set_index("Country")["avg_cdd"] if not cdd_df.empty else pd.Series(dtype=float)
    prec_cv = df.groupby("Country")["PRECTOTCORR"].std() / (df.groupby("Country")["PRECTOTCORR"].mean() + 1e-9)

    vuln = pd.DataFrame({
        "Mean T2M (°C)": temp_mean,
        "T2M Std": temp_std,
        "Extreme Heat Days/yr": heat_score,
        "Max CDD/yr": cdd_score,
        "Precip CV": prec_cv,
    }).dropna()

    if not vuln.empty:
        vuln_norm = (vuln - vuln.min()) / (vuln.max() - vuln.min() + 1e-9)
        weights = [0.20, 0.15, 0.30, 0.20, 0.15]
        vuln["Vulnerability Score"] = vuln_norm.mul(weights).sum(axis=1)
        vuln["Rank"] = vuln["Vulnerability Score"].rank(ascending=False).astype(int)
        vuln_display = vuln.sort_values("Rank").round(3)

        fig_vuln = px.bar(
            vuln_display.reset_index().rename(columns={"index": "Country"}),
            x="Vulnerability Score",
            y="Country",
            orientation="h",
            color="Country",
            color_discrete_map=COLORS,
            title="Composite Climate Vulnerability Score",
            labels={"Vulnerability Score": "Score (0 = least, 1 = most vulnerable)"},
        )
        fig_vuln.update_layout(height=380, showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_vuln, use_container_width=True)

        st.dataframe(vuln_display, use_container_width=True)

    st.subheader("COP32 Position — Key Observations")
    st.markdown("""
| # | Observation |
|---|---|
| 1 | **Fastest warming:** Sudan shows the steepest long-term warming trend due to its Sahelo-Saharan location, with peak summer temperatures already exceeding 45°C. |
| 2 | **Most unstable precipitation:** Nigeria exhibits the highest precipitation coefficient of variation, driven by the sharp Sahel-to-forest gradient across its territory. |
| 3 | **Extreme heat & drought stress:** Sudan and Nigeria lead extreme-heat day counts; Sudan also records the longest consecutive dry-day sequences — signalling compounding loss-and-damage exposure. |
| 4 | **Ethiopia's profile:** Intermediate average stress but acute sensitivity to season-length change; the 2020–2023 five-season drought drove 4M+ displacements — the strongest adaptation-finance argument. |
| 5 | **Priority for climate finance:** Sudan — highest heat exposure, longest droughts, lowest adaptive capacity — is Ethiopia's strongest nominee for priority Adaptation Fund and loss-and-damage allocation at COP32. |
""")
