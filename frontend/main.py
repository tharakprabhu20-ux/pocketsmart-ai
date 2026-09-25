"""
Enterprise Pitch-Ready FinTech Dashboard for PocketSmart AI.
Implements 50/30/20 Analytics, Multi-Currency Localization, Glassmorphism, and Gemini Pro Scenario Intelligence.
"""

import os
import sys
from datetime import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.db import (
    init_db,
    set_user_income,
    get_user_income,
    add_transactions,
    get_transactions,
    clear_all_transactions
)
from backend.budget_engine import calculate_50_30_20_budget
from backend.gemini_service import (
    parse_receipt_image,
    generate_budget_advice,
    answer_what_if_scenario
)
from frontend.styles import apply_custom_styles
from frontend.components import (
    render_hero_header,
    render_kpi_card,
    render_category_pill
)
from frontend.charts import (
    render_budget_donut,
    render_sankey_flow,
    render_burn_gauge
)

load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="PocketSmart AI | Intelligent FinTech Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Apply Global Modern Glassmorphic CSS ---
st.markdown(apply_custom_styles(), unsafe_allow_html=True)

# --- Global Multi-Currency Directory ---
CURRENCIES = {
    "₹ INR (Indian Rupee)": {"symbol": "₹", "code": "INR"},
    "$ USD (US Dollar)": {"symbol": "$", "code": "USD"},
    "€ EUR (Euro)": {"symbol": "€", "code": "EUR"},
    "£ GBP (British Pound)": {"symbol": "£", "code": "GBP"},
    "د.إ AED (UAE Dirham)": {"symbol": "AED ", "code": "AED"}
}

# Initialize database idempotently
init_db()

# --- Modernized Dashboard Sidebar ---
with st.sidebar:
    # Sidebar Header Brand Tile
    st.markdown(
        '<div class="sidebar-profile-card">'
        '<div class="sidebar-brand-icon">💳</div>'
        '<div>'
        '<div style="font-weight: 800; font-size: 15px; color: #F8FAFC; letter-spacing: -0.3px;">PocketSmart AI</div>'
        '<div style="font-size: 12px; color: #94A3B8; font-weight: 500;">Financial Intelligence</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("### 🌐 Localization & Profile")
    
    # Currency Selector (Defaults to INR ₹)
    selected_cur_label = st.selectbox(
        "Display Currency",
        options=list(CURRENCIES.keys()),
        index=0,
        help="Select display currency for math, charts, OCR extractions, and AI advice."
    )
    CUR_SYM = CURRENCIES[selected_cur_label]["symbol"]
    CUR_CODE = CURRENCIES[selected_cur_label]["code"]
    
    # API Key Input (Only if missing from environment)
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key or current_key == "your_gemini_api_key_here":
        st.warning("⚠️ `GEMINI_API_KEY` missing.")
        user_key = st.text_input("Enter Gemini API Key:", type="password", help="Enables Gemini Vision OCR & Advisory.")
        if user_key:
            os.environ["GEMINI_API_KEY"] = user_key
            st.success("API Key activated!")
            st.rerun()

    st.markdown("---")
    
    # Income Input (Defaults cleanly to 0.0 unless configured)
    st.markdown("### 💵 Income & Targets")
    current_income = get_user_income()
    income_input = st.number_input(
        f"Monthly Take-Home ({CUR_SYM})",
        min_value=0.0,
        value=float(current_income),
        step=1000.0 if CUR_SYM == "₹" else 100.0,
        help="Enter your take-home monthly salary / net cash flow. Leave 0.0 for a clean blank slate."
    )
    
    if income_input != current_income:
        set_user_income(income_input)
        if income_input > 0:
            st.toast("Updated Monthly Baseline Income!", icon="💰")
        
    st.markdown(
        '<div class="sidebar-target-card">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
        f'<span class="badge-base badge-needs" style="padding:2px 8px; font-size:11px;">Needs 50%</span>'
        f'<b style="color:#F8FAFC; font-size:13px;">{CUR_SYM}{income_input * 0.50:,.2f}</b>'
        f'</div>'
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
        f'<span class="badge-base badge-wants" style="padding:2px 8px; font-size:11px;">Wants 30%</span>'
        f'<b style="color:#F8FAFC; font-size:13px;">{CUR_SYM}{income_input * 0.30:,.2f}</b>'
        f'</div>'
        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
        f'<span class="badge-base badge-savings" style="padding:2px 8px; font-size:11px;">Savings 20%</span>'
        f'<b style="color:#F8FAFC; font-size:13px;">{CUR_SYM}{income_input * 0.20:,.2f}</b>'
        f'</div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown("### 🛠️ Utilities")
    if st.button("🗑️ Reset All Data to Zero", type="secondary", use_container_width=True):
        clear_all_transactions(reset_income=True)
        st.session_state.clear()
        st.success("All data & calculations reset to zero.")
        st.rerun()


# --- Load Real-Time Calculations ---
transactions = get_transactions()
metrics = calculate_50_30_20_budget(income_input, transactions)


# --- Top Hero Banner ---
st.markdown(render_hero_header(CUR_CODE, CUR_SYM), unsafe_allow_html=True)


# --- Top KPI Metric Ribbon ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(render_kpi_card(
        label="Monthly Net Inflow",
        value=f"{CUR_SYM}{metrics['income']:,.2f}",
        subtext="50/30/20 Benchmark Base" if metrics['income'] > 0 else "Enter income in sidebar",
        icon="💵",
        value_color="#F8FAFC",
        subtext_color="#38BDF8"
    ), unsafe_allow_html=True)

with kpi2:
    spent_color = "#EF4444" if (metrics['income'] > 0 and metrics['total_spent'] > metrics['income']) else "#F8FAFC"
    spend_subtext = f"{metrics['pct_income']['Total']}% of Monthly Inflow" if metrics['income'] > 0 else f"{len(transactions)} transaction{'s' if len(transactions) != 1 else ''} logged"
    st.markdown(render_kpi_card(
        label="Total Spend Logged",
        value=f"{CUR_SYM}{metrics['total_spent']:,.2f}",
        subtext=spend_subtext,
        icon="💳",
        value_color=spent_color,
        subtext_color="#94A3B8"
    ), unsafe_allow_html=True)

with kpi3:
    if metrics['income'] == 0 and metrics['total_spent'] == 0:
        cashflow_color = "#94A3B8"
        cashflow_status = "⚪ Clean Initial State"
    elif metrics['net_cash_flow'] >= 0:
        cashflow_color = "#10B981"
        cashflow_status = "🟢 Net Surplus Available"
    else:
        cashflow_color = "#EF4444"
        cashflow_status = "🔴 Budget Deficit"

    st.markdown(render_kpi_card(
        label="Remaining Cash Flow",
        value=f"{CUR_SYM}{metrics['net_cash_flow']:,.2f}",
        subtext=cashflow_status,
        icon="📈",
        value_color=cashflow_color,
        subtext_color=cashflow_color
    ), unsafe_allow_html=True)

with kpi4:
    wants_var = metrics['variances']['Wants']
    if metrics['income'] == 0 and metrics['actuals']['Wants'] == 0:
        wants_color = "#94A3B8"
        wants_status = "⚪ No Wants Spend Logged"
    elif wants_var >= 0:
        wants_color = "#10B981"
        wants_status = f"🟢 {CUR_SYM}{wants_var:,.2f} Buffer Headroom"
    else:
        wants_color = "#EF4444"
        wants_status = f"🔴 {CUR_SYM}{abs(wants_var):,.2f} Over Target"

    st.markdown(render_kpi_card(
        label="Wants (Lifestyle) Headroom",
        value=f"{CUR_SYM}{wants_var:,.2f}",
        subtext=wants_status,
        icon="🛍️",
        value_color=wants_color,
        subtext_color=wants_color
    ), unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)


# --- 4 Modular Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📸 Smart Receipt Ingestion",
    "📊 Budget Analytics & Cash Flow",
    "💡 Strategic Financial Advisor",
    "📑 Transaction Ledger"
])


# =========================================================
# TAB 1: SMART RECEIPT INGESTION & AUTO-CATEGORIZATION
# =========================================================
with tab1:
    st.markdown("### 📸 **Instant Receipt Scanner & Smart Expense Ingestion**")
    st.markdown(
        f"Upload receipts or invoices to automatically digitize items in **{CUR_CODE} ({CUR_SYM})** "
        f"and allocate them into <span class='badge-base badge-needs'>Needs</span>, <span class='badge-base badge-wants'>Wants</span>, or <span class='badge-base badge-savings'>Savings</span>.",
        unsafe_allow_html=True
    )
    
    col_u, col_p = st.columns([1, 1], gap="medium")
    
    with col_u:
        with st.container(border=True):
            uploaded_file = st.file_uploader(
                "Upload Receipt Image",
                type=["png", "jpg", "jpeg", "webp"],
                help="High-resolution receipt photo or invoice."
            )
            
            if uploaded_file:
                st.image(uploaded_file, caption="Receipt Preview", use_container_width=True)
                
                if st.button("⚡ Scan & Digitize Receipt", type="primary", use_container_width=True):
                    with st.spinner("Digitizing and auto-categorizing receipt items..."):
                        img_bytes = uploaded_file.getvalue()
                        extracted_data = parse_receipt_image(img_bytes, currency_symbol=CUR_SYM)
                        
                        if "error" in extracted_data and extracted_data["error"] and not extracted_data.get("items"):
                            st.error(f"OCR Error: {extracted_data['error']}")
                        else:
                            st.session_state["staged_receipt"] = extracted_data
                            st.success(f"Extracted {len(extracted_data.get('items', []))} items from **{extracted_data.get('merchant', 'Store')}**!")

    with col_p:
        with st.container(border=True):
            st.markdown("#### 📝 **Data Staging & Validation**")
            
            if "staged_receipt" in st.session_state:
                receipt = st.session_state["staged_receipt"]
                items_list = receipt.get("items", [])
                
                st.write(f"**Merchant:** `{receipt.get('merchant', 'Merchant')}` | **Date:** `{receipt.get('date', 'N/A')}`")
                st.write(f"**Detected Total:** `{CUR_SYM}{receipt.get('total_amount', 0.0):,.2f}`")
                
                if items_list:
                    df_staged = pd.DataFrame(items_list)
                    df_staged["merchant"] = receipt.get("merchant", "Store")
                    df_staged["date"] = receipt.get("date", datetime.today().strftime('%Y-%m-%d'))
                    
                    edited_df = st.data_editor(
                        df_staged,
                        column_config={
                            "item_name": st.column_config.TextColumn("Item Description", required=True),
                            "amount": st.column_config.NumberColumn(f"Cost ({CUR_SYM})", format=f"{CUR_SYM}%.2f", min_value=0.01, required=True),
                            "category": st.column_config.SelectboxColumn("Category", options=["Needs", "Wants", "Savings"], required=True),
                            "merchant": st.column_config.TextColumn("Merchant"),
                            "date": st.column_config.TextColumn("Date")
                        },
                        use_container_width=True,
                        num_rows="dynamic"
                    )
                    
                    if st.button("💾 Commit Staged Entries to Database", type="primary", use_container_width=True):
                        records = edited_df.to_dict(orient="records")
                        add_transactions(records)
                        st.success(f"Committed {len(records)} transactions to your SQLite ledger!")
                        del st.session_state["staged_receipt"]
                        st.rerun()
                else:
                    st.info("No individual line items detected.")
            else:
                st.info("Upload and scan a receipt on the left to review items before committing.")

    # Expandable Manual Entry Form
    with st.expander("➕ Manual Expense Entry Fallback", expanded=False):
        with st.form("manual_entry_form"):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                in_merchant = st.text_input("Merchant / Vendor", "Grocery Store")
                in_item = st.text_input("Item Description", "Weekly Staples")
            with f_col2:
                default_amount = 450.0 if CUR_SYM == "₹" else 45.0
                in_amount = st.number_input(f"Amount ({CUR_SYM})", min_value=0.01, value=default_amount, step=10.0 if CUR_SYM == "₹" else 1.0)
                in_cat = st.selectbox("50/30/20 Category", ["Needs", "Wants", "Savings"])
            with f_col3:
                in_date = st.date_input("Transaction Date", datetime.today())
                st.write("")
                submit_manual = st.form_submit_button("Record Transaction", use_container_width=True)
                
            if submit_manual:
                add_transactions([{
                    "merchant": in_merchant,
                    "item_name": in_item,
                    "amount": in_amount,
                    "category": in_cat,
                    "date": in_date.strftime('%Y-%m-%d')
                }])
                st.success("Transaction recorded successfully!")
                st.rerun()


# =========================================================
# TAB 2: DEEP ANALYTICS & CASH FLOW TOPOLOGY
# =========================================================
with tab2:
    st.markdown("### 📊 **Interactive Cash Flow & Budget Analytics**")
    
    # Side-by-Side Donut & Sankey Flow
    chart_row_c1, chart_row_c2 = st.columns([1, 1], gap="medium")
    with chart_row_c1:
        with st.container(border=True):
            st.plotly_chart(render_budget_donut(metrics, currency_symbol=CUR_SYM), use_container_width=True)
        
    with chart_row_c2:
        with st.container(border=True):
            st.plotly_chart(render_sankey_flow(income_input, metrics, currency_symbol=CUR_SYM), use_container_width=True)

    # Real-Time Category Burn-Rate Gauges
    st.markdown("#### ⚡ **Category Burn-Rate Indicators**")
    gauge_c1, gauge_c2, gauge_c3 = st.columns(3)
    
    with gauge_c1:
        with st.container(border=True):
            st.plotly_chart(
                render_burn_gauge(
                    current=metrics['actuals']['Needs'],
                    target=metrics['targets']['Needs'],
                    title="Needs Burn Gauge",
                    currency_symbol=CUR_SYM
                ),
                use_container_width=True
            )
        
    with gauge_c2:
        with st.container(border=True):
            st.plotly_chart(
                render_burn_gauge(
                    current=metrics['actuals']['Wants'],
                    target=metrics['targets']['Wants'],
                    title="Wants Burn Gauge",
                    currency_symbol=CUR_SYM
                ),
                use_container_width=True
            )
        
    with gauge_c3:
        with st.container(border=True):
            st.plotly_chart(
                render_burn_gauge(
                    current=metrics['actuals']['Savings'],
                    target=metrics['targets']['Savings'],
                    title="Savings Target Gauge",
                    currency_symbol=CUR_SYM
                ),
                use_container_width=True
            )


# =========================================================
# TAB 3: STRATEGIC FINANCIAL ADVISOR & SCENARIOS
# =========================================================
with tab3:
    st.markdown("### 💡 **Smart Budget Recommendations & Scenario Assistant**")
    
    adv_col, chat_col = st.columns([1, 1], gap="medium")
    
    # Left Column: Strategic Behavioral Spending Audit
    with adv_col:
        with st.container(border=True):
            st.markdown("#### 📋 **Strategic Financial Audit**")
            st.caption(f"Generate an executive 3-part spending audit based on verified ledger math in {CUR_CODE} ({CUR_SYM}).")
            
            if st.button("🚀 Generate Strategic Advisory Report", type="primary", use_container_width=True):
                with st.spinner("Analyzing ledger dynamics and generating spending recommendations..."):
                    advice_report = generate_budget_advice(income_input, metrics, currency_symbol=CUR_SYM)
                    st.session_state["ai_advisory_text"] = advice_report

            if "ai_advisory_text" in st.session_state:
                st.markdown("---")
                st.markdown(st.session_state["ai_advisory_text"])

    # Right Column: Interactive What-If Scenario Chat
    with chat_col:
        with st.container(border=True):
            st.markdown("#### 💡 **What-If Scenario Assistant**")
            st.caption(f"Test prospective purchases against your active category ceilings in {CUR_SYM}:")
            
            # Quick-Action Query Chips with Dynamic Currency
            flight_cost = "₹12,000" if CUR_SYM == "₹" else f"{CUR_SYM}400"
            dine_cost = "₹3,000" if CUR_SYM == "₹" else f"{CUR_SYM}150"
            
            chip_col1, chip_col2, chip_col3 = st.columns(3)
            with chip_col1:
                if st.button(f"✈️ Afford {flight_cost}?", use_container_width=True):
                    st.session_state["quick_prompt"] = f"Can I afford a {flight_cost} flight this weekend without breaching my Wants budget?"
            with chip_col2:
                if st.button(f"🍽️ Cut {dine_cost} dining?", use_container_width=True):
                    st.session_state["quick_prompt"] = f"What happens if I cut {dine_cost} from dining out next month?"
            with chip_col3:
                if st.button("📈 Emergency fund?", use_container_width=True):
                    st.session_state["quick_prompt"] = "How is my 20% savings target pacing for an emergency fund?"

            # Chat history state
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = [
                    {"role": "assistant", "content": f"I have real-time visibility into your live budget in {CUR_CODE} ({CUR_SYM}). Ask me any 'What-If' purchase or trade-off scenario!"}
                ]

            # Display conversation messages
            chat_container = st.container(height=360)
            with chat_container:
                for message in st.session_state["chat_history"]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Input handling
            input_prompt = st.chat_input(f"E.g., Can I buy a {CUR_SYM}5,000 watch today?" if CUR_SYM == "₹" else f"E.g., Can I buy a {CUR_SYM}220 jacket today?")
            if "quick_prompt" in st.session_state and st.session_state["quick_prompt"]:
                input_prompt = st.session_state.pop("quick_prompt")

            if input_prompt:
                st.session_state["chat_history"].append({"role": "user", "content": input_prompt})
                
                with st.spinner("Evaluating scenario against headroom..."):
                    ai_answer = answer_what_if_scenario(
                        query=input_prompt,
                        chat_history=st.session_state["chat_history"],
                        context=metrics,
                        currency_symbol=CUR_SYM
                    )
                    st.session_state["chat_history"].append({"role": "assistant", "content": ai_answer})
                st.rerun()


# =========================================================
# TAB 4: TRANSACTION LEDGER & EXPORT
# =========================================================
with tab4:
    st.markdown("### 📑 **Transaction Ledger & Statement Export**")
    
    with st.container(border=True):
        if transactions:
            df_all = pd.DataFrame(transactions)
            
            filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
            with filter_col1:
                search_query = st.text_input("🔍 Search Merchant or Item", "")
            with filter_col2:
                cat_filters = st.multiselect(
                    "Filter Category",
                    options=["Needs", "Wants", "Savings"],
                    default=["Needs", "Wants", "Savings"]
                )
            with filter_col3:
                st.write("")
                csv_data = df_all.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Export CSV ({CUR_CODE})",
                    data=csv_data,
                    file_name=f"pocketsmart_statement_{CUR_CODE}_{datetime.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            df_filtered = df_all[df_all["category"].isin(cat_filters)]
            if search_query:
                df_filtered = df_filtered[
                    df_filtered["merchant"].str.contains(search_query, case=False, na=False) |
                    df_filtered["item_name"].str.contains(search_query, case=False, na=False)
                ]
                
            st.dataframe(
                df_filtered[["id", "date", "merchant", "item_name", "category", "amount"]],
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "merchant": st.column_config.TextColumn("Merchant"),
                    "item_name": st.column_config.TextColumn("Item Description"),
                    "category": st.column_config.TextColumn("Category"),
                    "amount": st.column_config.NumberColumn(f"Amount ({CUR_SYM})", format=f"{CUR_SYM}%.2f")
                },
                use_container_width=True,
                hide_index=True
            )
            
            st.caption(f"Displaying {len(df_filtered)} of {len(df_all)} ledger transactions.")
        else:
            st.info("No transactions logged in the SQLite database yet. Upload a receipt in Tab 1 to start!")
