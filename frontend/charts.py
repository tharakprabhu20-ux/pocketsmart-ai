"""
Dark-Native Interactive Plotly Visualization Engine for PocketSmart AI.
Standardized FinTech Color Palette:
  - Needs (Essentials): #10B981 (Emerald Green)
  - Wants (Lifestyle): #F59E0B (Amber Orange)
  - Savings (Future): #6366F1 (Indigo / Purple)
  - Text & Accents: Dark theme friendly with 100% transparent backgrounds.
  - Multi-Currency Dynamic Localization (₹, $, €, £, د.إ, etc.)
"""

import plotly.graph_objects as go
from typing import Dict, Any

COLOR_NEEDS = "#10B981"     # Emerald Green
COLOR_WANTS = "#F59E0B"     # Amber Orange
COLOR_SAVINGS = "#6366F1"   # Indigo
COLOR_TEXT = "#F8FAFC"      # Off-white / Light Slate
COLOR_SUBTEXT = "#94A3B8"   # Slate Gray
COLOR_BORDER = "#334155"    # Dark Border


def render_budget_donut(metrics: Dict[str, Any], currency_symbol: str = "₹") -> go.Figure:
    """
    Plotly donut chart showing actual spending distribution by category
    with total spend KPI centered in the hole. Dark-theme native with transparent background
    and dynamic currency localization.
    """
    actuals = metrics.get("actuals", {"Needs": 0.0, "Wants": 0.0, "Savings": 0.0})
    total_spent = metrics.get("total_spent", 0.0)

    categories = ["Needs (50%)", "Wants (30%)", "Savings (20%)"]
    values = [
        actuals.get("Needs", 0.0),
        actuals.get("Wants", 0.0),
        actuals.get("Savings", 0.0)
    ]
    colors = [COLOR_NEEDS, COLOR_WANTS, COLOR_SAVINGS]

    # Handle zero spending state gracefully
    if sum(values) <= 0:
        fig = go.Figure(data=[go.Pie(
            labels=["No Spending Recorded"],
            values=[1],
            hole=0.68,
            marker=dict(colors=['#1E293B'], line=dict(color='#0F172A', width=2)),
            textinfo='none',
            hoverinfo='none'
        )])
        fig.update_layout(
            annotations=[dict(
                text=f"<span style='font-size:12px;color:#94A3B8;'>Total Spend</span><br><b style='font-size:20px;color:#F8FAFC;'>{currency_symbol}0.00</b>",
                x=0.5, y=0.5,
                showarrow=False
            )],
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    fig = go.Figure(data=[
        go.Pie(
            labels=categories,
            values=values,
            hole=0.68,
            marker=dict(
                colors=colors,
                line=dict(color='#0F172A', width=2.5)
            ),
            textinfo='percent',
            textposition='inside',
            textfont=dict(size=13, color="#FFFFFF", family="Plus Jakarta Sans, sans-serif", weight="bold"),
            hovertemplate=f"<b>%{{label}}</b><br>Spent: {currency_symbol}%{{value:,.2f}}<br>Share: %{{percent}}<extra></extra>",
            pull=[0.02, 0.02, 0.02]
        )
    ])

    fig.update_layout(
        title=dict(
            text="<b>Actual Spending Breakdown</b>",
            font=dict(size=15, family="Plus Jakarta Sans, sans-serif", color=COLOR_TEXT),
            x=0.5,
            xanchor='center'
        ),
        annotations=[
            dict(
                text=f"<span style='font-size:12px;color:#94A3B8;'>Total Spend</span><br><b style='font-size:20px;color:#F8FAFC;'>{currency_symbol}{total_spent:,.2f}</b>",
                x=0.5,
                y=0.5,
                showarrow=False
            )
        ],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=COLOR_TEXT, family="Plus Jakarta Sans, sans-serif")
        ),
        margin=dict(t=35, b=25, l=15, r=15),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def render_sankey_flow(income: float, metrics: Dict[str, Any], currency_symbol: str = "₹") -> go.Figure:
    """
    Plotly Sankey diagram visualizing cash flow topology:
    Monthly Net Income -> Needs (50%), Wants (30%), Savings (20%) -> Actual Spend & Remaining Surplus Headroom.
    Consumes dynamic currency symbol.
    """
    safe_income = max(0.0, float(income))
    cur = currency_symbol

    # If income is 0, display clean empty state
    if safe_income <= 0:
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(
                text=f"<span style='font-size:14px;color:#94A3B8;'>No Monthly Income Specified</span><br><span style='font-size:12px;color:#64748B;'>Enter your monthly take-home in the sidebar</span>",
                x=0.5, y=0.5,
                showarrow=False
            )],
            margin=dict(t=35, b=20, l=15, r=15),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    targets = metrics.get("targets", {
        "Needs": safe_income * 0.50,
        "Wants": safe_income * 0.30,
        "Savings": safe_income * 0.20
    })
    actuals = metrics.get("actuals", {"Needs": 0.0, "Wants": 0.0, "Savings": 0.0})

    # Headroom remaining per bucket (non-negative for flow)
    rem_needs = max(0.0, targets.get("Needs", 0.0) - actuals.get("Needs", 0.0))
    rem_wants = max(0.0, targets.get("Wants", 0.0) - actuals.get("Wants", 0.0))
    rem_savings = max(0.0, targets.get("Savings", 0.0) - actuals.get("Savings", 0.0))

    node_labels = [
        f"Monthly Inflow<br><b>{cur}{safe_income:,.0f}</b>",
        f"Needs Target (50%)<br><b>{cur}{targets.get('Needs', 0.0):,.0f}</b>",
        f"Wants Target (30%)<br><b>{cur}{targets.get('Wants', 0.0):,.0f}</b>",
        f"Savings Target (20%)<br><b>{cur}{targets.get('Savings', 0.0):,.0f}</b>",
        f"Needs Spent<br><b>{cur}{actuals.get('Needs', 0.0):,.0f}</b>",
        f"Needs Headroom<br><b>{cur}{rem_needs:,.0f}</b>",
        f"Wants Spent<br><b>{cur}{actuals.get('Wants', 0.0):,.0f}</b>",
        f"Wants Headroom<br><b>{cur}{rem_wants:,.0f}</b>",
        f"Savings Logged<br><b>{cur}{actuals.get('Savings', 0.0):,.0f}</b>",
        f"Savings Headroom<br><b>{cur}{rem_savings:,.0f}</b>"
    ]

    node_colors = [
        "#38BDF8",       # Income (Sky Blue)
        COLOR_NEEDS,     # Needs Target
        COLOR_WANTS,     # Wants Target
        COLOR_SAVINGS,   # Savings Target
        "#059669",       # Needs Spent
        "#34D399",       # Needs Buffer
        "#D97706",       # Wants Spent
        "#FBBF24",       # Wants Buffer
        "#4F46E5",       # Savings Logged
        "#818CF8"        # Savings Buffer
    ]

    sources = [0, 0, 0, 1, 1, 2, 2, 3, 3]
    targets_idx = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    values = [
        targets.get("Needs", 0.01),
        targets.get("Wants", 0.01),
        targets.get("Savings", 0.01),
        max(0.01, actuals.get("Needs", 0.0)),
        max(0.01, rem_needs),
        max(0.01, actuals.get("Wants", 0.0)),
        max(0.01, rem_wants),
        max(0.01, actuals.get("Savings", 0.0)),
        max(0.01, rem_savings)
    ]

    link_colors = [
        "rgba(16, 185, 129, 0.4)",   # Income -> Needs
        "rgba(245, 158, 11, 0.4)",   # Income -> Wants
        "rgba(99, 102, 241, 0.4)",   # Income -> Savings
        "rgba(5, 150, 105, 0.6)",    # Needs -> Spent
        "rgba(52, 211, 153, 0.35)",  # Needs -> Buffer
        "rgba(217, 119, 6, 0.6)",    # Wants -> Spent
        "rgba(251, 191, 36, 0.35)",  # Wants -> Buffer
        "rgba(79, 70, 229, 0.6)",    # Savings -> Logged
        "rgba(129, 140, 248, 0.35)"  # Savings -> Buffer
    ]

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=18,
            thickness=20,
            line=dict(color="#1E293B", width=1.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets_idx,
            value=values,
            color=link_colors,
            hovertemplate=f"Flow: {cur}%{{value:,.2f}}<extra></extra>"
        )
    )])

    fig.update_layout(
        title=dict(
            text="<b>50/30/20 Cash Flow & Headroom Topology</b>",
            font=dict(size=15, family="Plus Jakarta Sans, sans-serif", color=COLOR_TEXT),
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=11, color=COLOR_TEXT, family="Plus Jakarta Sans, sans-serif"),
        margin=dict(t=35, b=20, l=15, r=15),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def render_burn_gauge(current: float, target: float, title: str, currency_symbol: str = "₹") -> go.Figure:
    """
    Plotly indicator gauge with color-coded safety and warning threshold zones:
    - Green (Safe): Under 80%
    - Amber (Warning): 80% to 100%
    - Red (Breach/Over Budget): Exceeding 100%
    Dark-mode native with transparent backgrounds and dynamic currency prefix.
    Handles target=0 gracefully.
    """
    safe_target = max(0.0, float(target))
    safe_current = max(0.0, float(current))
    utilization_pct = (safe_current / safe_target * 100.0) if safe_target > 0 else 0.0
    cur = currency_symbol

    if safe_target <= 0:
        max_range = max(100.0, safe_current * 1.25)
        bar_color = "#64748B" if safe_current == 0 else "#EF4444"
        steps = [dict(range=[0, max_range], color="rgba(30, 41, 59, 0.4)")]
    else:
        if utilization_pct <= 80:
            bar_color = "#10B981"
        elif utilization_pct <= 100:
            bar_color = "#F59E0B"
        else:
            bar_color = "#EF4444"
        max_range = max(safe_target * 1.25, safe_current * 1.1)
        steps = [
            dict(range=[0, safe_target * 0.80], color="rgba(16, 185, 129, 0.15)"),
            dict(range=[safe_target * 0.80, safe_target], color="rgba(245, 158, 11, 0.2)"),
            dict(range=[safe_target, max_range], color="rgba(239, 68, 68, 0.2)")
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=safe_current,
        number=dict(prefix=cur, valueformat=",.2f", font=dict(size=20, color=COLOR_TEXT, family="Plus Jakarta Sans, sans-serif", weight="bold")),
        delta=dict(
            reference=safe_target,
            increasing=dict(color="#EF4444"),
            decreasing=dict(color="#10B981"),
            prefix=f"vs Target: {cur}",
            valueformat=",.2f",
            font=dict(size=12)
        ),
        title=dict(
            text=f"<b>{title}</b><br><span style='font-size:12px;color:#94A3B8;'>Target: {cur}{safe_target:,.2f} ({utilization_pct:.1f}%)</span>",
            font=dict(size=13, color=COLOR_TEXT, family="Plus Jakarta Sans, sans-serif")
        ),
        gauge=dict(
            axis=dict(
                range=[0, max_range],
                tickwidth=1,
                tickcolor="#475569",
                tickformat=f"{cur},.0f",
                tickfont=dict(size=10, color=COLOR_SUBTEXT)
            ),
            bar=dict(color=bar_color, thickness=0.35),
            bgcolor="rgba(30, 41, 59, 0.7)",
            borderwidth=1,
            bordercolor="#334155",
            steps=steps,
            threshold=dict(
                line=dict(color="#EF4444", width=3),
                thickness=0.85,
                value=safe_target if safe_target > 0 else 0.01
            )
        )
    ))

    fig.update_layout(
        margin=dict(t=45, b=20, l=25, r=25),
        height=210,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig
