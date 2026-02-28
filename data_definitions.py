# data_definitions.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


# -- Firm categories --
DZ_LARGE_FIRMS: List[str] = ["DZ BANK AG"]
DZ_MEDIUM_FIRMS: List[str] = [
    "Bausparkasse Schwäbisch Hall", "DZ Privatbank", "DZ Hyp", "VR Smart Finanz",
    "TeamBank", "DVB Bank", "DZ Compliance GmbH", "DG Nexolution", "DZ Service GmbH",
    "DZ Invest Consult", "DZ Equity Partners", "DZ Digital Lab", "VR Payment"
]


@dataclass(frozen=True)
class MetricMeta:
    definition: str
    typical_range: str
    better_is_higher: bool
    unit: str  # e.g. "%", "ratio", "count", etc.


METRIC_INFO: Dict[str, MetricMeta] = {
    "CET1_Ratio": MetricMeta(
        definition="Common Equity Tier 1 (CET1) Ratio measures a bank’s core capital relative to its risk-weighted assets. "
                   "It reflects the bank’s ability to absorb unexpected losses during financial stress.",
        typical_range="10% – 14%",
        better_is_higher=True,
        unit="%"
    ),
    "NPL_Ratio": MetricMeta(
        definition="The Non-Performing Loan (NPL) Ratio shows the percentage of loans that are in default or close to default. "
                   "Lower is better; it signals healthier credit quality.",
        typical_range="1% – 3%",
        better_is_higher=False,
        unit="%"
    ),
    "Cost_of_Risk": MetricMeta(
        definition="Cost of Risk represents loan loss provisions as a percentage of the loan book. Lower indicates fewer expected losses.",
        typical_range="0.3% – 0.7%",
        better_is_higher=False,
        unit="%"
    ),
    "LCR": MetricMeta(
        definition="Liquidity Coverage Ratio (LCR): high-quality liquid assets over 30-day net cash outflows under stress. >100% indicates a buffer.",
        typical_range="100% – 140%",
        better_is_higher=True,
        unit="%"
    ),
    "NSFR": MetricMeta(
        definition="Net Stable Funding Ratio (NSFR): stable funding relative to required stable funding over one year. Higher is better (typically ≥100%).",
        typical_range="100% – 110%",
        better_is_higher=True,
        unit="%"
    ),
    "OpRisk_Loss_Ratio": MetricMeta(
        definition="Operational risk losses relative to revenue/assets (e.g., fraud, outages, legal). Lower indicates stronger controls and resilience.",
        typical_range="0.01 – 0.04",
        better_is_higher=False,
        unit="ratio"
    ),
    "VaR_to_Assets": MetricMeta(
        definition="Value-at-Risk (VaR) to Assets: potential short-term market loss as a share of assets. Lower indicates less market exposure.",
        typical_range="0.02 – 0.05",
        better_is_higher=False,
        unit="ratio"
    ),
    "Single_Obligor_Usage": MetricMeta(
        definition="Exposure to a single obligor as % of internal limit. High values indicate concentration risk; lower is better.",
        typical_range="≤ 85% (large institutions)",
        better_is_higher=False,
        unit="ratio"
    ),
    "Sector_Concentration": MetricMeta(
        definition="Share of credit exposure concentrated in one sector. Higher concentration increases portfolio vulnerability; lower is better.",
        typical_range="≤ 40%",
        better_is_higher=False,
        unit="ratio"
    ),
    "Client_ROA": MetricMeta(
        definition="Client Return on Assets: operating profitability per unit of assets. Higher suggests stronger viability.",
        typical_range="1% – 2%",
        better_is_higher=True,
        unit="%"
    ),
    "ESG_Risk_Score": MetricMeta(
        definition="Internal ESG risk score. Lower is better (lower sustainability/reputational/regulatory risk).",
        typical_range="1 (low risk) – 5 (high risk)",
        better_is_higher=False,
        unit="score"
    ),
    "Watchlist_Status": MetricMeta(
        definition="Internal watchlist indicator reflecting early warning signals. Higher score implies lower risk.",
        typical_range="1 (high risk) – 5 (low risk)",
        better_is_higher=True,
        unit="score"
    ),
    "Overdraft_Frequency": MetricMeta(
        definition="How often a client exceeds overdraft limits. Higher frequency indicates liquidity stress; lower is better.",
        typical_range="0 – 3 per quarter",
        better_is_higher=False,
        unit="count"
    ),
    "Interest_Coverage_Ratio": MetricMeta(
        definition="EBIT / interest expense. Higher indicates stronger debt service capacity.",
        typical_range="3 – 8",
        better_is_higher=True,
        unit="ratio"
    ),
    "Debt_to_EBITDA": MetricMeta(
        definition="Debt / EBITDA. Lower indicates lower leverage and better creditworthiness.",
        typical_range="2.5 – 4.5",
        better_is_higher=False,
        unit="ratio"
    ),
    "Free_Cash_Flow_to_Debt": MetricMeta(
        definition="Free cash flow relative to total debt. Higher indicates stronger repayment capacity.",
        typical_range="10% – 25%",
        better_is_higher=True,
        unit="ratio"
    ),
    "Altman_Z_Score": MetricMeta(
        definition="Altman Z-score as bankruptcy risk proxy. Higher is healthier (safe zone typically above ~2.5).",
        typical_range="2.5 – 4 (safe zone)",
        better_is_higher=True,
        unit="score"
    ),
    "Debt_to_Equity_Ratio": MetricMeta(
        definition="Total debt relative to equity. Higher indicates more leverage; lower is better.",
        typical_range="1 – 2.5",
        better_is_higher=False,
        unit="ratio"
    ),
}

# -- Grouping metrics under risk areas --
METRICS_MAP: Dict[str, str] = {
    "CET1_Ratio": "Capital Adequacy",
    "NPL_Ratio": "Credit Risk",
    "Cost_of_Risk": "Credit Risk",
    "LCR": "Liquidity Risk",
    "NSFR": "Liquidity Risk",
    "OpRisk_Loss_Ratio": "Operational Risk",
    "VaR_to_Assets": "Market Risk",
    "Single_Obligor_Usage": "Client Concentration Risk",
    "Sector_Concentration": "Portfolio Concentration",
    "Client_ROA": "Client Viability",
    "ESG_Risk_Score": "Sustainability Risk",
    "Watchlist_Status": "Early Warning Signals",
    "Overdraft_Frequency": "Early Warning Signals",
    "Interest_Coverage_Ratio": "Client Viability",
    "Debt_to_EBITDA": "Leverage Risk",
    "Free_Cash_Flow_to_Debt": "Liquidity/Repayment Risk",
    "Altman_Z_Score": "Early Warning Signals",
    "Debt_to_Equity_Ratio": "Leverage Risk",
}

# -- Benchmarks by firm size --
BENCHMARKS: Dict[str, Dict[str, float]] = {
    "Large": {
        "CET1_Ratio": 12.5, "NPL_Ratio": 1.5, "Cost_of_Risk": 0.4, "LCR": 130, "NSFR": 105,
        "OpRisk_Loss_Ratio": 0.02, "VaR_to_Assets": 0.03, "Single_Obligor_Usage": 0.85,
        "Sector_Concentration": 0.35, "Client_ROA": 1.5, "ESG_Risk_Score": 2.5,
        "Watchlist_Status": 4, "Overdraft_Frequency": 2,
        "Interest_Coverage_Ratio": 6, "Debt_to_EBITDA": 3.5, "Free_Cash_Flow_to_Debt": 0.20,
        "Altman_Z_Score": 3.2, "Debt_to_Equity_Ratio": 2.0,
    },
    "Medium": {
        "CET1_Ratio": 11.5, "NPL_Ratio": 2.0, "Cost_of_Risk": 0.6, "LCR": 115, "NSFR": 100,
        "OpRisk_Loss_Ratio": 0.03, "VaR_to_Assets": 0.04, "Single_Obligor_Usage": 0.9,
        "Sector_Concentration": 0.4, "Client_ROA": 1.3, "ESG_Risk_Score": 3,
        "Watchlist_Status": 3.5, "Overdraft_Frequency": 3,
        "Interest_Coverage_Ratio": 4.5, "Debt_to_EBITDA": 4.0, "Free_Cash_Flow_to_Debt": 0.15,
        "Altman_Z_Score": 2.8, "Debt_to_Equity_Ratio": 2.2,
    }
}

# -- Metric weights (simple, explainable) --
# You can tune these based on the role you target.
METRIC_WEIGHTS: Dict[str, float] = {
    # Capital / Liquidity typically high
    "CET1_Ratio": 1.3,
    "LCR": 1.3,
    "NSFR": 1.2,

    # Credit risk
    "NPL_Ratio": 1.2,
    "Cost_of_Risk": 1.1,

    # Operational / market
    "OpRisk_Loss_Ratio": 1.1,
    "VaR_to_Assets": 1.0,

    # Concentrations
    "Single_Obligor_Usage": 1.0,
    "Sector_Concentration": 1.0,

    # Client health
    "Client_ROA": 0.9,
    "Interest_Coverage_Ratio": 1.0,
    "Debt_to_EBITDA": 1.1,
    "Debt_to_Equity_Ratio": 1.0,
    "Free_Cash_Flow_to_Debt": 1.0,
    "Altman_Z_Score": 1.1,
    "Watchlist_Status": 1.1,
    "Overdraft_Frequency": 1.0,

    # ESG (keep, but usually not the primary driver unless role is ESG-focused)
    "ESG_Risk_Score": 0.8,
}

# -- Scenario shocks: simple multipliers (scenario-driven simulation) --
# Interpretation: value = base * shock_multiplier * noise
SCENARIOS: Dict[str, Dict[str, float]] = {
    "Base (Normal Conditions)": {},
    "Recession / Credit Stress": {
        "NPL_Ratio": 1.35,
        "Cost_of_Risk": 1.30,
        "Client_ROA": 0.85,
        "Interest_Coverage_Ratio": 0.85,
        "Debt_to_EBITDA": 1.15,
        "Watchlist_Status": 0.90,
        "Overdraft_Frequency": 1.20,
    },
    "Liquidity Squeeze": {
        "LCR": 0.88,
        "NSFR": 0.92,
        "Overdraft_Frequency": 1.25,
        "Single_Obligor_Usage": 1.10,
    },
    "Operational Incident (Fraud/Outage)": {
        "OpRisk_Loss_Ratio": 1.60,
        "ESG_Risk_Score": 1.10,
    },
    "Market Volatility Spike": {
        "VaR_to_Assets": 1.40,
        "CET1_Ratio": 0.95,
    },
}

# -- Control suggestions (governance-style output) --
CONTROL_LIBRARY: Dict[str, str] = {
    "CET1_Ratio": "Review capital planning; update ICAAP assumptions; consider RWA optimization and capital buffer targets.",
    "NPL_Ratio": "Strengthen early warning triggers; enhance collections strategy; recalibrate PD/LGD and sector limits.",
    "Cost_of_Risk": "Validate ECL staging rules; stress provisioning overlays; backtest impairment model performance.",
    "LCR": "Update contingency funding plan; improve HQLA composition; tighten intraday liquidity monitoring.",
    "NSFR": "Rebalance funding tenor; reduce reliance on short-term wholesale funding; enhance ALM governance.",
    "OpRisk_Loss_Ratio": "Run incident post-mortem; tighten key controls; enhance monitoring (KRIs) and segregation of duties.",
    "VaR_to_Assets": "Review market limits; increase hedging; validate VaR model and perform stress testing.",
    "Single_Obligor_Usage": "Enforce single-name limits; consider syndication/participation; strengthen approval escalation.",
    "Sector_Concentration": "Revisit sector limits; diversify exposures; implement sector stress scenarios and monitoring.",
    "Client_ROA": "Reassess client rating; tighten covenants; review pricing/margins and relationship strategy.",
    "ESG_Risk_Score": "Update ESG due diligence; define remediation plan; improve disclosures and monitoring of controversies.",
    "Watchlist_Status": "Increase review frequency; document action plan; strengthen covenant monitoring and triggers.",
    "Overdraft_Frequency": "Introduce cash-flow forecasting requirement; review overdraft limits; tighten monitoring cadence.",
    "Interest_Coverage_Ratio": "Tighten leverage covenants; adjust credit terms; increase monitoring and require mitigation plan.",
    "Debt_to_EBITDA": "Consider deleveraging plan; tighten covenant package; reassess facility structure and amortization.",
    "Free_Cash_Flow_to_Debt": "Focus on liquidity action plan; limit distributions; adjust repayment schedule and triggers.",
    "Altman_Z_Score": "Trigger enhanced review; update rating; require management meeting and formal mitigation plan.",
    "Debt_to_Equity_Ratio": "Reassess leverage tolerance; adjust capital structure expectations; tighten covenants and pricing.",
}