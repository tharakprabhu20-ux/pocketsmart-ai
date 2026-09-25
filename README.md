# 💳 PocketSmart AI: Your Smart Budget & Recommendation Assistant

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Visualizations](https://img.shields.io/badge/Visuals-Plotly-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![AI Engine](https://img.shields.io/badge/GenAI-Google%20Gemini%20API-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Track](https://img.shields.io/badge/Track-Generative%20AI%20with%20Google-EA4335?logo=googlecloud&logoColor=white)](https://ai.google.dev/)

> **An enterprise-grade personal financial intelligence platform combining deterministic 50/30/20 arithmetic, multimodal receipt vision extraction, dynamic multi-currency support, and strategic behavioral financial auditing with Google Gemini.**

---

## 📑 Table of Contents
- [Executive Overview](#-executive-overview)
- [Hybrid Architecture (Zero Math Hallucinations)](#-hybrid-architecture-zero-math-hallucinations)
- [Key Features](#-key-features)
- [Repository Scaffolding](#-repository-scaffolding)
- [Getting Started & Installation](#-getting-started--installation)
- [Automated Testing & Verification](#-automated-testing--verification)
- [Demo Walkthrough Video Script](#-demo-walkthrough-video-script-2-minute-pitch)
- [License & Acknowledgements](#-license--acknowledgements)

---

## 🌟 Executive Overview

Traditional personal finance apps require tedious manual expense logging or suffer from generative AI hallucinations when attempting to calculate balances and budget limits. 

**PocketSmart AI** solves this with a **Deterministic-Generative Hybrid Architecture**:
1. **Deterministic Core**: Pure Python strictly calculates all 50/30/20 framework metrics ($50\%$ Needs, $30\%$ Wants, $20\%$ Savings), category variances, burn rates, and net cash flows with mathematical precision.
2. **Generative Intelligence**: Google Gemini multimodal models process raw, unstructured visual receipt data and provide high-leverage strategic financial coaching and contextual "What-If" scenario evaluations.

---

## ⚡ Hybrid Architecture (Zero Math Hallucinations)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 POCKETSMART AI ARCHITECTURE                            │
└────────────────────────────────────────────────────────────────────────────────────────┘

    [ USER BROWSER INTERFACE ]  ───> http://localhost:8501
                 │
                 ▼
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │ 🎨 FRONTEND PRESENTATION & VISUALIZATION LAYER                                    │
    │  • frontend/main.py       : Streamlit 4-Tab Interface, Localization, UI Routing  │
    │  • frontend/charts.py     : Dark-Native Plotly (Donut, Sankey Flow, Burn Gauges) │
    │  • frontend/styles.py     : Glassmorphic Design System, Badges & Animations      │
    │  • frontend/components.py : Reusable KPI Metric Ribbons, Hero Banners & Pills    │
    └──────────────────┬──────────────────────────────────────────┬────────────────────┘
                       │                                          │
                       ▼                                          ▼
    ┌────────────────────────────────────────┐   ┌─────────────────────────────────────┐
    │ ⚙️ DETERMINISTIC LOGIC & PERSISTENCE   │   │ 🧠 MULTIMODAL GENAI SERVICE         │
    │  • backend/budget_engine.py:           │   │  • backend/gemini_service.py:       │
    │    Pure Python 50/30/20 arithmetic     │   │    Gemini Multimodal Vision OCR     │
    │  • backend/db.py:                      │   │    Gemini Strategic Advisory Audit  │
    │    Thread-Safe SQLite3 CRUD & Schemas  │   │    Pydantic v2 Schema Enforcement   │
    └──────────────────┬─────────────────────┘   └─────────────────┬───────────────────┘
                       │                                           │
                       ▼                                           ▼
             [ SQLite: pocketsmart.db ]                  [ Google Gemini API ]
```

---

## 🚀 Key Features

### 1. 📸 Multimodal Receipt Vision & Data Staging
- Drag-and-drop receipt image uploader (PNG, JPG, WEBP).
- **Gemini Vision OCR** extracts merchant name, date, total amount, and individual itemized lines.
- Enforces strict classification into `Needs` (groceries, rent, medical), `Wants` (dining, lifestyle, subscriptions), or `Savings` (investments, debt repayment).
- Interactive `st.data_editor` staging table allowing manual edits or category reassignments before committing to the SQLite database.

### 2. 🌐 Global Multi-Currency Support
- Persistent dynamic currency switcher:
  - 🇮🇳 **₹ INR** (Indian Rupee) — *Default*
  - 🇺🇸 **$ USD** (US Dollar)
  - 🇪🇺 **€ EUR** (Euro)
  - 🇬🇧 **£ GBP** (British Pound)
  - 🇦🇪 **د.إ AED** (UAE Dirham)
- Automatically propagates currency formatting across KPI tiles, Plotly charts, data staging grids, and Gemini system prompts.

### 3. 📊 Dark-Native Interactive Visualizations
- **Spending Allocation Donut**: High-contrast ring chart with category explode effects and centered total spend KPI badge.
- **Sankey Flow Topology**: Translucent gradient flow mapping Inflow $\to$ 50/30/20 Targets $\to$ Actual Spent + Surplus Headroom.
- **Category Burn-Rate Gauges**: Real-time indicator dials with safety zones ($<80\%$ Safe, $80\text{--}100\%$ Warning, $>100\%$ Breach).

### 4. 🤖 Gemini Strategic Advisor & "What-If" Assistant
- **1-Click Financial Audit**: Generates an executive 3-part Markdown spending diagnosis (Health Diagnosis, 3 High-Impact Spending Cuts with dollar figures, and a 30-Day Action Sprint).
- **Contextual Scenario Assistant**: Evaluates purchasing feasibility queries (e.g., *"Can I afford a ₹12,000 flight this weekend?"*) against live ledger headroom, delivering a clear **VERDICT** (✅ Affordable, ⚠️ Feasible with Trade-offs, or ❌ Deficit Risk).

### 5. 📑 Transaction Ledger & Data Governance
- Full SQLite persistence (`pocketsmart.db`).
- Filterable and searchable ledger table.
- 1-Click CSV statement export with localized currency tagging.

---

## 🏗️ Repository Scaffolding

```
pocketsmart-ai/
├── .env                       # Active production API key configuration
├── .env.example               # Configuration blueprint
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive documentation & pitch guide
├── seed_data.py               # Demonstration mock data generator
├── pocketsmart.db             # Auto-initialized thread-safe SQLite database
│
├── backend/                   # Core Business Logic & GenAI Layer
│   ├── __init__.py
│   ├── db.py                  # Idempotent SQLite persistence & CRUD operations
│   ├── budget_engine.py       # Pure Python 50/30/20 deterministic arithmetic
│   └── gemini_service.py      # Google Gemini multimodal OCR & advisory service
│
├── frontend/                  # User Interface & Visualizations
│   ├── __init__.py
│   ├── main.py                # Glassmorphic 4-Tab Streamlit dashboard
│   ├── charts.py              # Dark-native Plotly charts (Donut, Sankey, Gauges)
│   ├── styles.py              # CSS tokens, glassmorphism, glowing badges
│   └── components.py          # Modular UI cards & hero headers
│
└── tests/                     # Automated Test Suite
    ├── __init__.py
    └── test_budget.py         # Pytest test cases covering math, edge cases, and DB
```

---

## 💻 Getting Started & Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/pocketsmart-ai.git
cd pocketsmart-ai
```

### Step 2: Install Dependencies
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Step 4: Seed Sample Demonstration Data (Optional)
Populate the database with realistic sample transactions:
```bash
python seed_data.py
```

### Step 5: Launch the Streamlit Application
```bash
streamlit run frontend/main.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🧪 Automated Testing & Verification

Execute the complete automated test suite:
```bash
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- ✅ `test_standard_50_30_20_calculation`: Validates baseline target and actual allocations.
- ✅ `test_zero_income_edge_case`: Validates graceful degradation with 0 income.
- ✅ `test_zero_expenses_edge_case`: Validates calculations when no expenses are logged.
- ✅ `test_overage_budget_deficit`: Validates negative variance and >100% utilization handling.
- ✅ `test_user_income_crud`: Validates SQLite income updates and reads.
- ✅ `test_transactions_crud`: Validates bulk insertion, queries, and table clearing.

---

## 🎬 Demo Walkthrough Video Script (2-Minute Pitch)

> **Target Audience**: Hackathon Judges, FinTech Evaluators & Product Reviewers  
> **Total Duration**: 2 Minutes (120 Seconds)

```
========================================================================================
TIMELINE & VISUAL WALKTHROUGH
========================================================================================

[0:00 - 0:25] ACT I: HOOK & THE PROBLEM
----------------------------------------------------------------------------------------
[VISUAL]
Camera on presenter, transitioning to a split-screen showing a crumpled paper receipt and a cluttered spreadsheet.

[PRESENTER]
"We all know the 50/30/20 budget rule: 50% for Needs, 30% for Wants, and 20% for Savings. 
 But in real life, manual budgeting fails. Typing every receipt into a spreadsheet is exhausting, 
 and asking typical AI chatbots often leads to made-up math and arithmetic errors.
 
 Meet PocketSmart AI: Your Smart Budget & Recommendation Assistant—built on a strict 
 Deterministic-Generative Hybrid Architecture powered by Google Gemini."


[0:25 - 0:55] ACT II: MULTIMODAL VISION OCR & REAL-TIME ANALYTICS
----------------------------------------------------------------------------------------
[VISUAL]
Screen share of the PocketSmart AI dashboard in dark mode. Presenter switches currency to ₹ INR in the sidebar, drags and drops a grocery receipt (e.g. Akash Enterprises) into Tab 1, and clicks "Scan & Extract with Gemini".

[PRESENTER]
"Watch this. In Tab 1, I upload a raw store receipt. Google Gemini's multimodal vision model 
 instantly scans the receipt, extracts the merchant and date, and classifies every line item 
 into Needs, Wants, or Savings using strict Pydantic schemas.
 
 I can verify or edit prices right here in the staging table before committing them to our SQLite ledger.
 
 Over in Tab 2, our custom Plotly engine visualizes our cash flow topology in real time. 
 Notice the Sankey diagram: it maps our monthly inflow into 50/30/20 target ceilings, 
 showing exactly where money was spent versus remaining buffer headroom, accompanied by live 
 category burn-rate gauges."


[0:55 - 1:30] ACT III: STRATEGIC BEHAVIORAL ADVISOR & SCENARIO ENGINE
----------------------------------------------------------------------------------------
[VISUAL]
Presenter switches to Tab 3 ("Gemini AI Advisor & Scenarios"). Clicks "Generate Strategic Advisory Report", then clicks the quick chip: "✈️ Afford ₹12,000 flight?".

[PRESENTER]
"Now let's unlock generative intelligence without the risk of math errors.
 
 All ledger arithmetic is calculated deterministically in pure Python and passed to Gemini 
 as verified context. With one click, Gemini delivers an executive 3-part financial audit:
 A health diagnosis, 3 high-impact spending cuts with exact rupee estimates, and a 30-day action plan.
 
 Wondering if you can afford an impromptu purchase? Our What-If Scenario Assistant tests 
 contemplated expenses directly against your live category headroom. When I ask if I can 
 afford a ₹12,000 flight, it evaluates my remaining Wants buffer and gives an immediate, 
 data-backed verdict."


[1:30 - 2:00] ACT IV: DATA GOVERNANCE & CLOSING
----------------------------------------------------------------------------------------
[VISUAL]
Presenter switches to Tab 4 ("Transaction Ledger"), filters by category, clicks "Download CSV", and returns to the Hero Dashboard view.

[PRESENTER]
"Finally, in Tab 4, users maintain full data sovereignty with searchable transactions and 
 1-click CSV statement exports.
 
 Zero math hallucinations. Zero friction receipt ingestion. Real-time visual clarity.
 
 PocketSmart AI transforms personal financial management from a chore into an effortless, 
 intelligent daily superpower.
 
 Thank you!"
========================================================================================
```

---

## 📄 License & Acknowledgements

- Built for the **Generative AI with Google** hackathon track.
- Powered by Google Gemini API & Streamlit.
- Licensed under the [MIT License](LICENSE).
