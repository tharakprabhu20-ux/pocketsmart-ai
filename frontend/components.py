"""
Reusable UI Components and Micro-Layouts for PocketSmart AI.
Provides clean HTML/CSS strings for KPI ribbons, hero headers, and status badges.
Ensures zero leading/trailing indentation so Streamlit does not render HTML as code blocks.
"""

from typing import Dict, Any


def render_hero_header(cur_code: str, cur_sym: str) -> str:
    """Renders the top enterprise hero banner with clean live badges."""
    html = (
        '<div class="hero-container">'
        '<div>'
        '<div class="hero-title">💳 PocketSmart AI <span class="hero-badge">Enterprise Edition</span></div>'
        '<div class="hero-subtitle">Deterministic 50/30/20 Analytics, Multimodal Receipt Vision &amp; Strategic Financial Advisory</div>'
        '</div>'
        '<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap; justify-content: flex-end;">'
        f'<span class="badge-base badge-currency">🌐 {cur_code} ({cur_sym})</span>'
        '<span class="badge-base badge-needs">🟢 Needs 50%</span>'
        '<span class="badge-base badge-wants">🟡 Wants 30%</span>'
        '<span class="badge-base badge-savings">🟣 Savings 20%</span>'
        '</div>'
        '</div>'
    )
    return html


def render_kpi_card(
    label: str,
    value: str,
    subtext: str,
    icon: str = "📊",
    value_color: str = "#F8FAFC",
    subtext_color: str = "#94A3B8"
) -> str:
    """Renders a polished dark-glass KPI metric card without markdown indentation bugs."""
    html = (
        '<div class="glass-card">'
        f'<div class="card-label"><span>{icon}</span> {label}</div>'
        f'<div class="card-value" style="color: {value_color};">{value}</div>'
        f'<div class="card-subtext" style="color: {subtext_color};">{subtext}</div>'
        '</div>'
    )
    return html


def render_category_pill(category: str) -> str:
    """Returns a styled HTML pill for a given 50/30/20 category."""
    cat = category.capitalize()
    if cat == "Needs":
        return "<span class='badge-base badge-needs'>🟢 Needs (50%)</span>"
    elif cat == "Wants":
        return "<span class='badge-base badge-wants'>🟡 Wants (30%)</span>"
    elif cat == "Savings":
        return "<span class='badge-base badge-savings'>🟣 Savings (20%)</span>"
    return f"<span class='badge-base'>{category}</span>"
