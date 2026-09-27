import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="COVID-19 India Analytics",
    page_icon="📊",
    layout="wide",
)

# ---------- Load data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("COVID_India_Master_Analysis.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)
    return df

df = load_data()

# ---------- Header ----------
st.title("COVID-19 India Data Analysis & Visualization")
st.caption(
    "Week 6 • Data Analytics Internship • Yash Vijay • MBA – Business Analytics"
)

# ---------- Sidebar ----------
st.sidebar.header("Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(start_date, tuple):
    start_date, end_date = start_date

filtered = df[
    (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
].copy()

# ---------- Helper ----------
def latest_value(frame, column):
    s = frame[column].dropna()
    return s.iloc[-1] if not s.empty else None

def fmt_int(value):
    return "N/A" if value is None else f"{int(value):,}"

def fmt_pct(value):
    return "N/A" if value is None else f"{value:.2f}%"

# ---------- KPI row ----------
latest = filtered.iloc[-1] if not filtered.empty else None

if latest is not None:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Cumulative Cases", fmt_int(latest["cum_cases"]))
    c2.metric("Deaths", fmt_int(latest["cum_death"]))
    c3.metric("Recoveries", fmt_int(latest["cum_recovered"]))
    c4.metric("Active Cases", fmt_int(latest["cum_active_cases"]))
    c5.metric("Recovery Rate", fmt_pct(latest["recovery_rate_pct"]))

st.divider()

# ---------- Case trend ----------
st.subheader("COVID-19 Case Trend")

fig_cases = px.line(
    filtered,
    x="date",
    y="new_cases",
    labels={"date": "Date", "new_cases": "Daily New Cases"},
)
fig_cases.update_layout(
    margin=dict(l=10, r=10, t=20, b=10),
    hovermode="x unified",
)
st.plotly_chart(fig_cases, use_container_width=True)

peak_cases = filtered.loc[filtered["new_cases"].idxmax()]
st.info(
    f"Peak daily new cases in the selected period: "
    f"{int(peak_cases['new_cases']):,} on {peak_cases['date'].strftime('%d %B %Y')}."
)

# ---------- Death & recovery ----------
st.subheader("Death and Recovery Trends")
left, right = st.columns(2)

with left:
    fig_deaths = px.line(
        filtered,
        x="date",
        y="new_death",
        labels={"date": "Date", "new_death": "New Deaths"},
    )
    fig_deaths.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_deaths, use_container_width=True)

with right:
    fig_recoveries = px.line(
        filtered,
        x="date",
        y="new_recovered",
        labels={"date": "Date", "new_recovered": "New Recoveries"},
    )
    fig_recoveries.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_recoveries, use_container_width=True)

# ---------- Rates ----------
st.subheader("Recovery, Mortality and Active Rates")
r1, r2, r3 = st.columns(3)
r1.metric("Recovery Rate", fmt_pct(latest["recovery_rate_pct"]))
r2.metric("Mortality Rate", fmt_pct(latest["mortality_rate_pct"]))
r3.metric("Active Rate", fmt_pct(latest["active_rate_pct"]))

# ---------- Vaccination ----------
st.subheader("Vaccination Progress")
vax_cols = [
    "date",
    "total_vaccinations",
    "people_vaccinated",
    "people_fully_vaccinated",
]
vax = filtered[vax_cols].dropna(subset=["total_vaccinations"])

if not vax.empty:
    vax_long = vax.melt(
        id_vars="date",
        value_vars=[
            "total_vaccinations",
            "people_vaccinated",
            "people_fully_vaccinated",
        ],
        var_name="metric",
        value_name="people",
    )
    labels = {
        "total_vaccinations": "Total Vaccinations",
        "people_vaccinated": "People Vaccinated",
        "people_fully_vaccinated": "Fully Vaccinated",
    }
    vax_long["metric"] = vax_long["metric"].map(labels)

    fig_vax = px.line(
        vax_long,
        x="date",
        y="people",
        color="metric",
        labels={"date": "Date", "people": "People / Doses"},
    )
    fig_vax.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig_vax, use_container_width=True)

# ---------- Cases vs vaccination ----------
st.subheader("Cases and Vaccination Trend Comparison")
st.caption(
    "Indexed comparison for descriptive analysis only. "
    "This does not establish a causal relationship."
)

comparison = filtered[[
    "date", "new_cases", "total_vaccinations"
]].copy()

if not comparison["total_vaccinations"].dropna().empty:
    case_max = comparison["new_cases"].max()
    vax_max = comparison["total_vaccinations"].max()

    if case_max > 0:
        comparison["New Cases Index"] = comparison["new_cases"] / case_max * 100
    else:
        comparison["New Cases Index"] = 0

    comparison["Vaccination Index"] = (
        comparison["total_vaccinations"] / vax_max * 100
    )

    indexed = comparison.melt(
        id_vars="date",
        value_vars=["New Cases Index", "Vaccination Index"],
        var_name="metric",
        value_name="index",
    )

    fig_compare = px.line(
        indexed,
        x="date",
        y="index",
        color="metric",
        labels={"date": "Date", "index": "Index"},
    )
    fig_compare.update_yaxes(range=[0, 105])
    fig_compare.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig_compare, use_container_width=True)

# ---------- Key findings ----------
st.subheader("Key Findings")
if not filtered.empty:
    peak_deaths = filtered.loc[filtered["new_death"].idxmax()]
    peak_recoveries = filtered.loc[filtered["new_recovered"].idxmax()]

    findings = [
        f"Highest daily cases in the selected period: {int(peak_cases['new_cases']):,} on {peak_cases['date'].strftime('%d %B %Y')}.",
        f"Highest daily deaths in the selected period: {int(peak_deaths['new_death']):,} on {peak_deaths['date'].strftime('%d %B %Y')}.",
        f"Highest daily recoveries in the selected period: {int(peak_recoveries['new_recovered']):,} on {peak_recoveries['date'].strftime('%d %B %Y')}.",
        f"Ending active cases in the selected period: {int(latest['cum_active_cases']):,}.",
        f"Ending recovery rate in the selected period: {latest['recovery_rate_pct']:.2f}%.",
    ]
    for item in findings:
        st.write("• " + item)

# ---------- Download ----------
st.subheader("Download Data")
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered dataset (CSV)",
    data=csv_bytes,
    file_name="COVID_India_filtered_analysis.csv",
    mime="text/csv",
)

st.caption(
    "Source dataset: COVID_India_Master_Analysis.csv | "
    "Analysis prepared for Week 6 Data Analytics Internship project."
)
