"""
Dark-Native Glassmorphic Design System & Global CSS Tokens for PocketSmart AI.
Provides rich typography, sleek status badges, frosted glass cards, and glowing accent states.
All CSS is clean and minified without raw Markdown indentation issues.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Premium pleasant dark palette: deep obsidian slate with calm oceanic indigo glow */
.stApp {
    background: radial-gradient(circle at 15% 15%, rgba(30, 41, 59, 0.45) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(15, 23, 42, 0.6) 0%, transparent 50%),
                #090D16 !important;
    color: #F1F5F9;
}

/* Modern dashboard sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1322 0%, #090D16 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.35);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.07) !important;
    margin: 16px 0 !important;
}

[data-testid="stSidebar"] h3 {
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #94A3B8 !important;
    margin-bottom: 12px !important;
}

[data-testid="stSidebar"] h4 {
    font-size: 12px !important;
    font-weight: 800 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: #64748B !important;
    margin-bottom: 8px !important;
}

/* Sidebar profile card */
.sidebar-profile-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.sidebar-brand-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}

.sidebar-target-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 8px;
    backdrop-filter: blur(8px);
}

/* Top Hero Header Container */
.hero-container {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.88) 50%, rgba(30, 27, 75, 0.85) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 22px 28px;
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 16px 32px -10px rgba(0, 0, 0, 0.5), 0 0 24px rgba(99, 102, 241, 0.12);
}

.hero-title {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #F8FAFC;
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0;
}

.hero-badge {
    font-size: 11px;
    font-weight: 700;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    color: #FFFFFF;
    padding: 4px 12px;
    border-radius: 9999px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.35);
}

.hero-subtitle {
    font-size: 13.5px;
    color: #94A3B8;
    margin: 6px 0 0 0;
    font-weight: 500;
    line-height: 1.4;
}

/* Polished Glass Card Container */
.glass-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 16px;
    padding: 18px 20px;
    min-height: 125px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.25s ease, box-shadow 0.25s ease;
    box-shadow: 0 10px 20px -3px rgba(0, 0, 0, 0.3);
    margin-bottom: 12px;
}

.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.45);
    transform: translateY(-2px);
    box-shadow: 0 14px 24px -3px rgba(0, 0, 0, 0.4), 0 0 20px rgba(99, 102, 241, 0.18);
}

.card-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.card-value {
    font-size: 24px;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.5px;
    margin: 2px 0;
}

.card-subtext {
    font-size: 12px;
    font-weight: 600;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Modern Status Badges & Pills */
.badge-base {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 13px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
}

.badge-needs {
    background: rgba(16, 185, 129, 0.14);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.badge-wants {
    background: rgba(245, 158, 11, 0.14);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

.badge-savings {
    background: rgba(99, 102, 241, 0.14);
    color: #A5B4FC;
    border: 1px solid rgba(99, 102, 241, 0.4);
}

.badge-currency {
    background: rgba(56, 189, 248, 0.14);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.4);
}

/* Tab Customization */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    margin-bottom: 22px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 8px;
}

.stTabs [data-baseweb="tab"] {
    height: 46px;
    border-radius: 12px;
    padding: 8px 20px;
    font-weight: 700;
    font-size: 13.5px;
    color: #94A3B8;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.07);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC;
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(30, 41, 59, 0.7);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.35) 0%, rgba(124, 58, 237, 0.3) 100%) !important;
    color: #F8FAFC !important;
    border-color: rgba(99, 102, 241, 0.75) !important;
    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.32);
}

/* Enhanced Streamlit Buttons */
div.stButton > button:first-child {
    border-radius: 12px;
    font-weight: 700;
    font-size: 13.5px;
    letter-spacing: 0.02em;
    padding: 8px 18px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

div.stButton > button[kind="primary"]:first-child {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.45);
    color: #FFFFFF;
}

div.stButton > button[kind="primary"]:hover:first-child {
    background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%);
    box-shadow: 0 6px 22px rgba(79, 70, 229, 0.65);
    transform: translateY(-1px);
}

div.stButton > button[kind="secondary"]:first-child {
    background: rgba(30, 41, 59, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #E2E8F0;
}

div.stButton > button[kind="secondary"]:hover:first-child {
    background: rgba(51, 65, 85, 0.85);
    border-color: rgba(255, 255, 255, 0.25);
    color: #FFFFFF;
    transform: translateY(-1px);
}

/* Streamlit Containers with clean border */
[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(10px);
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background: rgba(30, 41, 59, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
</style>
"""


def apply_custom_styles() -> str:
    """Returns the CSS styling string to inject into Streamlit."""
    return CUSTOM_CSS.strip()
