# App
from __future__ import annotations

import random
from datetime import date
from typing import Dict, List

import altair as alt
import pandas as pd
import streamlit as st

# Warmer / richer RAG palette (more saturated, higher contrast)
# Dark / warm RAG palette (stronger, richer, "board-report" look)
# Classic, readable RAG palette (normal red / orange / green)
RAG_COLORS = {
    "Red": {
       # "bg":  "#F8D7DA",  # light red background
       # "fg":  "#842029",  # dark red text
        "bar": "#DC3545",  # normal red for chart bars
    },
    "Amber": {
       # "bg":  "#FFE5B4",  # light orange background
       # "fg":  "#6B3D00",  # dark orange/brown text
        "bar": "#FFA500",  # normal orange
    },
    "Green": {
       # "bg":  "#D1E7DD",  # light green background
       # "fg":  "#0F5132",  # dark green text
        "bar": "#198754",  # normal green
    },
}

from data_definitions import (
    BENCHMARKS,
    CONTROL_LIBRARY,
    DZ_LARGE_FIRMS,
    DZ_MEDIUM_FIRMS,
    METRIC_INFO,
    METRICS_MAP,
    METRIC_WEIGHTS,
    SCENARIOS,
)
from scoring import priority_from_rating, rate_metric


# ----------------------------
# Styling helpers
# ----------------------------
def _rag_cell_style(value: str) -> str:
    if value in RAG_COLORS:
        bg = RAG_COLORS[value]["bar"]     # <-- use the SAME colors as the chart
        fg = "#FFFFFF"                    # white text reads well on these strong colors
        return f"background-color: {bg}; color: {fg}; font-weight: 700;"
    return ""


def style_rag_column(
    df: pd.DataFrame,
    rag_column_name: str = "RAG",
    hide_text: bool = True,
) -> pd.io.formats.style.Styler:
    """
    Colors ONLY the specified RAG column cells (e.g., "RAG" or "RAG Reporting")
    """
    df_display = df.copy()

    if rag_column_name not in df_display.columns:
        return df_display.style

    # Keep true RAG values for styling
    rag_values = df_display[rag_column_name].astype(str)

    # Optionally hide text in the colored cell
    if hide_text:
        df_display[rag_column_name] = ""

    styler = df_display.style

    # Apply styles ONLY to the RAG column cells
    def _rag_col_styles(col: pd.Series):
        return [_rag_cell_style(rag_values.loc[i]) for i in col.index]

    styler = styler.apply(_rag_col_styles, axis=0, subset=[rag_column_name])

    # Strict numeric formatting
    numeric_cols = df_display.select_dtypes(include="number").columns.tolist()
    fmt: dict[str, str] = {}
    for col in numeric_cols:
        if col in {"Avg Score (1-3)", "Score (1-3)", "Total Weighted Score (1–3)"}:
            fmt[col] = "{:.2f}"
        else:
            fmt[col] = "{:.3f}"

    styler = styler.format(fmt)
    return styler


# ----------------------------
# Helpers
# ----------------------------
def _apply_scenario(metric: str, base_value: float, scenario_name: str) -> float:
    shock = SCENARIOS.get(scenario_name, {}).get(metric, 1.0)
    return base_value * shock


def simulate_firm_metrics(
    firm_size: str,
    scenario_name: str,
    *,
    seed: int | None = None,
    noise_sigma: float = 0.05,
) -> Dict[str, float]:
    """
    Scenario-driven simulation:
    value = benchmark * scenario_shock * noise
    where noise ~ Normal(1, noise_sigma) clipped to [0.75, 1.35]
    """
    if seed is not None:
        random.seed(seed)

    metrics: Dict[str, float] = {}
    for metric, benchmark in BENCHMARKS[firm_size].items():
        shocked = _apply_scenario(metric, benchmark, scenario_name)

        meta = METRIC_INFO[metric]
        is_base = scenario_name == "Base (Normal Conditions)"
        is_stress = not is_base

        # directional stress bias
        if is_stress:
            if meta.better_is_higher:
                shocked *= 0.92
            else:
                shocked *= 1.08

        # scenario-dependent volatility
        if is_base:
            sigma = 0.08
        elif "Recession" in scenario_name:
            sigma = 0.14
        else:
            sigma = 0.18

        demo_mode = st.session_state.get("demo_mode", False)
        if demo_mode:
            sigma *= 1.5

        noise = random.gauss(1.0, sigma)
        noise = max(0.6, min(1.6, noise))

        value = shocked * noise

        # simple rounding by unit
        unit = METRIC_INFO[metric].unit
        if unit == "%":
            metrics[metric] = round(value, 2)
        elif unit in {"score", "count"}:
            metrics[metric] = round(value, 0)
        else:  # ratios
            metrics[metric] = round(value, 4)

    return metrics


def build_assessment_df(
    firm_size: str,
    firm_name: str,
    scenario_name: str,
    *,
    seed: int | None,
) -> pd.DataFrame:
    firm_metrics = simulate_firm_metrics(firm_size, scenario_name, seed=seed)

    rows: List[dict] = []
    for metric, value in firm_metrics.items():
        meta = METRIC_INFO[metric]

        if meta.unit in {"score", "count"}:
            value = int(round(value))

        benchmark = BENCHMARKS[firm_size][metric]
        group = METRICS_MAP[metric]
        w = METRIC_WEIGHTS.get(metric, 1.0)

        mr = rate_metric(value, benchmark, better_is_higher=meta.better_is_higher)
        rows.append(
            {
                "Firm": firm_name,
                "Size": firm_size,
                "Scenario": scenario_name,
                "AsOf": str(date.today()),
                "Risk Area": group,
                "Metric": metric,
                "Value": value,
                "Benchmark": benchmark,
                "Unit": meta.unit,
                "Direction": "Higher is better" if meta.better_is_higher else "Lower is better",
                "Rating": mr.rating,
                "RAG": mr.rag,
                "Score (1-3)": mr.score,
                "Weight": w,
                "Weighted Score": mr.score * w,
                "Control Suggestion": CONTROL_LIBRARY.get(
                    metric, "Review metric definition and update relevant controls/policies."
                ),
                "Priority": priority_from_rating(mr.rag),
            }
        )

    df = pd.DataFrame(rows)

    # Display-friendly rounding
    percent_mask = df["Unit"] == "%"
    df.loc[percent_mask, ["Value", "Benchmark"]] = df.loc[percent_mask, ["Value", "Benchmark"]].round(2)

    ratio_mask = df["Unit"] == "ratio"
    df.loc[ratio_mask, ["Value", "Benchmark"]] = df.loc[ratio_mask, ["Value", "Benchmark"]].round(3)

    int_mask = df["Unit"].isin(["score", "count"])
    df.loc[int_mask, ["Value", "Benchmark"]] = df.loc[int_mask, ["Value", "Benchmark"]].round(0).astype(int)

    return df


def weighted_total_score(df: pd.DataFrame) -> float:
    num = df["Weighted Score"].sum()
    den = df["Weight"].sum()
    return round(float(num / den), 2) if den else 0.0


def top_risk_drivers(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    tmp = df.copy()
    tmp["Driver Strength"] = (3 - tmp["Score (1-3)"]) * tmp["Weight"]
    return tmp.sort_values(["Driver Strength", "Weight"], ascending=[False, False]).head(n)[
        ["Risk Area", "Metric", "Value", "Benchmark", "Rating", "RAG", "Priority", "Control Suggestion"]
    ]


def make_group_summary(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("Risk Area", as_index=False)
        .apply(
            lambda x: pd.Series(
                {
                    "Avg Score (1-3)": round((x["Weighted Score"].sum() / x["Weight"].sum()), 2),
                    "RAG Reporting": (
                        "Red"
                        if (x["RAG"] == "Red").any()
                        else ("Amber" if (x["RAG"] == "Amber").any() else "Green")
                    ),
                    "Metrics": len(x),
                }
            )
        )
    )
    if "Risk Area" not in g.columns:
        g = g.reset_index()
        g = g.rename(columns={"index": "Risk Area"})
    return g.sort_values("Avg Score (1-3)")

def rag_from_value_vs_benchmark(
    value: float,
    benchmark: float,
    *,
    better_is_higher: bool,
    tolerance: float = 0.10,
) -> str:
    # Use your existing rating logic so the chart matches the tables
    return rate_metric(value, benchmark, better_is_higher=better_is_higher, tolerance=tolerance).rag

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="MaRisk Risk Assessment – Corporate Banking Focus", layout="wide")
st.title("MaRisk Risk Assessment – Corporate Banking Focus")

st.write(
    "This tool simulates a firm's performance across MaRisk-aligned risk categories relevant to corporate banking "
    "and produces a governance-style assessment (RAG, priorities, control suggestions, exportable report)."
)

st.info(
    "Note: Benchmarks and firm performance data are simulated for demonstration. "
    "Benchmarks are loosely inspired by common regulatory expectations (Basel III/EBA-style), "
    "and do not represent actual figures for DZ BANK or any institution."
)

st.markdown(
    "**RAG meaning:** Red / Amber / Green is a standard risk-reporting scale. "
    "**Green** = within appetite, **Amber** = early warning / close to threshold, **Red** = breach / urgent action & escalation."
)

left, right = st.columns([1, 2], gap="large")

with left:
    firm_size = st.selectbox("Select Firm Size", ["Large", "Medium"])
    firm_list = DZ_LARGE_FIRMS if firm_size == "Large" else DZ_MEDIUM_FIRMS
    firm_name = st.selectbox("Select a Firm", firm_list)

    scenario_name = st.selectbox("Select Scenario", list(SCENARIOS.keys()))
    seed = st.number_input("Random Seed (optional)", value=42, step=1)
    use_seed = st.checkbox("Use seed (reproducible results)", value=True)
    seed_val = int(seed) if use_seed else None
    stress_mode = st.checkbox("Demonstration Mode (Higher Volatility)", value=False)

    if st.button("Run Risk Assessment", type="primary"):
        st.session_state["demo_mode"] = stress_mode
        st.session_state["assessment_df"] = build_assessment_df(
            firm_size=firm_size,
            firm_name=firm_name,
            scenario_name=scenario_name,
            seed=seed_val,
        )

df: pd.DataFrame | None = st.session_state.get("assessment_df")

with right:
    if df is None or df.empty:
        st.subheader(" Assessment Output")
        st.caption("Run the assessment to generate results.")
    else:
        st.subheader(f"Risk Assessment for {firm_name.upper()} ({firm_size}) — {scenario_name}")

        total = weighted_total_score(df)
        st.markdown("**Total Weighted Score (1–3)**")
        st.metric("", total)

        # --- Group summary (RENDER WITH st.dataframe, NOT to_html) ---
        group_summary = make_group_summary(df)
        styled_summary = style_rag_column(group_summary, rag_column_name="RAG Reporting")
        st.dataframe(styled_summary, use_container_width=True, hide_index=True)

        # --- Top risk drivers (RENDER WITH st.dataframe, NOT to_html) ---
        st.markdown(f"**Top Risk Drivers**")
        drivers = top_risk_drivers(df, n=6)
        drivers_styler = style_rag_column(drivers, rag_column_name="RAG")
        st.dataframe(drivers_styler, use_container_width=True, hide_index=True)

        # --- Detailed findings (RENDER WITH st.dataframe, NOT to_html) ---
        st.markdown("### Details by Risk Area")
        for risk_area in df["Risk Area"].unique():
            sub = df[df["Risk Area"] == risk_area].copy()
            worst_rag = (
                "Red"
                if (sub["RAG"] == "Red").any()
                else ("Amber" if (sub["RAG"] == "Amber").any() else "Green")
            )
            st.markdown(f"**{risk_area}** — Status: **{worst_rag}**")

            show_cols = [
                "Metric",
                "Value",
                "Benchmark",
                "Unit",
                "Direction",
                "Rating",
                "RAG",
                "Priority",
                "Control Suggestion",
            ]

            detail = sub[show_cols].copy()
            rag_order = {"Red": 0, "Amber": 1, "Green": 2}
            detail["RAG_sort"] = detail["RAG"].map(rag_order).fillna(99)
            detail = detail.sort_values(["RAG_sort", "Metric"]).drop(columns=["RAG_sort"])

            detail_styler = style_rag_column(detail, rag_column_name="RAG")
            st.dataframe(detail_styler, use_container_width=True, hide_index=True)

        # Export
        st.markdown("---")
        st.subheader("Export Report")
        csv_bytes = df.to_csv(index=False).encode("utf-8")  # keep numeric export clean
        st.download_button(
            label="Download assessment CSV",
            data=csv_bytes,
            file_name=f"marisk_assessment_{firm_name.replace(' ', '_')}_{firm_size}_{scenario_name[:10].replace(' ', '_')}.csv",
            mime="text/csv",
        )

        # Governance-style final recommendation
        st.markdown("---")
        st.subheader("🧠 Final Recommendation")
        red_areas = sorted(df.loc[df["RAG"] == "Red", "Risk Area"].unique().tolist())
        amber_areas = sorted(df.loc[df["RAG"] == "Amber", "Risk Area"].unique().tolist())

        if red_areas:
            st.error(f"High-priority remediation recommended in: **{', '.join(red_areas)}**")
        elif amber_areas:
            st.warning(f"Monitoring / targeted improvements recommended in: **{', '.join(amber_areas)}**")
        else:
            st.success("No material weaknesses detected across risk areas under the selected scenario.")


# ----------------------------
# Comparison Section (direction-aware)
# ----------------------------
st.markdown("---")
st.subheader("Compare Metric Across Medium-Sized Firms")

selected_metric = st.selectbox("Choose a Metric", list(METRICS_MAP.keys()))
meta = METRIC_INFO[selected_metric]
benchmark_val = BENCHMARKS["Medium"][selected_metric]

st.markdown(f"**Definition:** {meta.definition}")
st.markdown(f"**Typical range:** {meta.typical_range}")
st.caption(f"Direction: {'Higher is better' if meta.better_is_higher else 'Lower is better'}")

comparison_seed = 1234 + hash(selected_metric) % 1000
random.seed(comparison_seed)

scenario_for_comparison = "Base (Normal Conditions)"

values = {}
for firm in DZ_MEDIUM_FIRMS:
    shocked = _apply_scenario(selected_metric, benchmark_val, scenario_for_comparison)
    noise = random.gauss(1.0, 0.06)
    noise = max(0.75, min(1.35, noise))
    values[firm] = round(shocked * noise, 4 if meta.unit == "ratio" else 2)

df_metric = pd.DataFrame({"Firm": list(values.keys()), selected_metric: list(values.values())})

# Assign RAG per firm for this selected metric
df_metric["RAG"] = df_metric[selected_metric].apply(
    lambda v: rag_from_value_vs_benchmark(
        v, benchmark_val, better_is_higher=meta.better_is_higher, tolerance=0.10
    )
)

# Map to warm bar colors
benchmark_rule = alt.Chart(pd.DataFrame({selected_metric: [benchmark_val]})).mark_rule(
    color="#4A3F35", strokeDash=[4, 4]
).encode(y=selected_metric)

bar_chart = alt.Chart(df_metric).mark_bar().encode(
    x=alt.X("Firm:N", sort="-y"),
    y=alt.Y(f"{selected_metric}:Q"),
    color=alt.Color("RAG:N", scale=alt.Scale(domain=["Red", "Amber", "Green"],
                                            range=[RAG_COLORS["Red"]["bar"], RAG_COLORS["Amber"]["bar"], RAG_COLORS["Green"]["bar"]]),
                    legend=alt.Legend(title="RAG")),
    tooltip=["Firm", selected_metric, "RAG"],
).properties(
    height=380,
    title=f"{selected_metric} – Medium Firm Comparison (Benchmark: {benchmark_val})",
) + benchmark_rule

st.altair_chart(bar_chart, use_container_width=True)

if meta.better_is_higher:
    best_row = df_metric.loc[df_metric[selected_metric].idxmax()]
    worst_row = df_metric.loc[df_metric[selected_metric].idxmin()]
else:
    best_row = df_metric.loc[df_metric[selected_metric].idxmin()]
    worst_row = df_metric.loc[df_metric[selected_metric].idxmax()]

st.success(f"🏆 Best Performer: **{best_row['Firm']}** – {best_row[selected_metric]}")
st.error(f"🚨 Weakest Performer: **{worst_row['Firm']}** – {worst_row[selected_metric]}")

# conda activate myenvforweb
# cd "C:\Users\fanek\OneDrive\Document\ProjectFolderDocumentation+Code\MaRisk\MaRisk_app"
# python -m streamlit run updated_MaRisk_app.py
