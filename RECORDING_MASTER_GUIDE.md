# 🎬 PocketSmart AI: Video Recording Master Guide & Rehearsal Roadmap

> **Companion Guide to**: `PITCH_DEMO_SCRIPT.md`  
> **Target Target**: 2 Minutes (120 Seconds)  
> **Track**: Generative AI with Google

---

## 🧭 STEP 1: Structured Rehearsal Roadmap

Mastering a 2-minute high-stakes pitch requires synchronizing speech with precise on-screen clicks. Follow this 3-phase rapid drill:

### 1. The 3-Step Rapid Practice Drill

| Drill Phase | Focus Area | Goal | Time Target |
| :--- | :--- | :--- | :--- |
| **Drill A: Audio & Script Dry Run** | Speak without touching the mouse | Achieve steady rhythm (~140 wpm), natural breathing, and clear pronunciation of key terms (*Deterministic-Generative Hybrid Architecture*, *50/30/20*, *Pydantic*). | Exactly **1:50 – 1:55** |
| **Drill B: Silent Click-Through** | Navigate UI without speaking | Rehearse mouse paths: Tab 1 upload $\to$ Tab 2 scroll $\to$ Tab 3 audit & query chip $\to$ Tab 4 filter & CSV download. Ensure smooth, intentional cursor movements with zero hunting. | Exactly **45 – 50s** |
| **Drill C: Full Synchronized Run** | Simultaneous speech + screen action | Match spoken keywords to visible button clicks and page transitions. Verify you finish Act IV under 2:00. | Exactly **1:58 – 2:00** |

---

### 2. Smooth Tab-to-Tab Verbal Transitions

Avoid awkward silences while clicking tabs by bridging your spoken sentences across page changes:

```
[Tab 1 ──> Tab 2 Transition]
"Once we commit these verified line items to SQLite...
 ↳ [CLICK TAB 2]
 ...our Plotly visualization engine instantly maps our cash flow topology in real time."

[Tab 2 ──> Tab 3 Transition]
"While deterministic charts give us mathematical certainty...
 ↳ [CLICK TAB 3]
 ...we can unlock generative intelligence with Google Gemini to coach our spending behavior."

[Tab 3 ──> Tab 4 Transition]
"Beyond proactive advisory and what-if simulations...
 ↳ [CLICK TAB 4]
 ...users retain full data governance with searchable ledgers and one-click statement exports."
```

---

## 🎥 STEP 2: Camera-Ready Shot List & Recording Checklist

---

### 1. Pre-Recording Staging & Environment Setup

- [ ] **Run Mock Data Seeding**:
  ```bash
  python seed_data.py
  ```
  *(Ensures Tab 2 and Tab 3 start with rich, visually stunning sample data).*
- [ ] **Launch Clean Server**:
  ```bash
  streamlit run frontend/main.py
  ```
- [ ] **Browser Window Preparation**:
  - Open `http://localhost:8501` in a dedicated, full-screen Chrome or Edge window.
  - Set Browser Zoom to **100%** or **110%** for optimal readability.
  - Close all other browser tabs, bookmarks bar (`Ctrl + Shift + B`), and extensions.
  - Verify currency is set to **`₹ INR (Indian Rupee)`** (or your chosen presentation currency).
- [ ] **Receipt Sample Asset**:
  - Place a clear receipt image (e.g. `receipt_sample.png` or `grocery_bill.jpg`) directly on your Desktop or in an easily accessible folder for a 1-click drag-and-drop.
- [ ] **Desktop & Audio Hygiene**:
  - Hide desktop icons and close background apps (Slack, Discord, Email, WhatsApp).
  - Set screen recording resolution to **1080p (1920x1080) at 60 FPS**.
  - Microphone test: Place mic 6–8 inches away with noise suppression enabled; speak with energetic, authoritative projection.

---

### 2. Synchronized Timeline & Mouse Cue Shot List

```
========================================================================================================================
ACT I: HOOK & THE PROBLEM [0:00 - 0:25]
========================================================================================================================
• Screen: Hero banner & Top KPI Ribbon visible on http://localhost:8501.
• Cursor Action:
  - [0:00 - 0:10]: Mouse rests naturally or gently highlights the Top Hero Title ("PocketSmart AI: Pro Edition").
  - [0:10 - 0:20]: Hover briefly over the 50/30/20 target breakdown pills in the sidebar (Needs 50%, Wants 30%, Savings 20%).
  - [0:20 - 0:25]: Move cursor toward Tab 1 ("📸 Receipt Ingestion & OCR").

========================================================================================================================
ACT II: MULTIMODAL VISION OCR & CASH FLOW TOPOLOGY [0:25 - 0:55]
========================================================================================================================
• Screen: Tab 1 ──> Tab 2
• Cursor Action:
  - [0:25]: Click Tab 1.
  - [0:28]: Drag and drop receipt image onto file uploader (or click 'Browse files' and select immediately).
  - [0:33]: Click "⚡ Scan & Extract with Gemini".
  - [0:38]: As the staging table appears, gently hover over the editable `Category` column showing 'Needs' / 'Wants'.
  - [0:44]: Click "💾 Commit Staged Entries to Database".
  - [0:46]: Click Tab 2 ("📊 Deep Analytics & Cash Flow").
  - [0:48 - 0:54]: Smoothly scroll down to showcase the side-by-side Donut chart, Sankey Flow diagram, and the 3 Burn-Rate Gauges.

========================================================================================================================
ACT III: STRATEGIC BEHAVIORAL ADVISOR & WHAT-IF SCENARIOS [0:55 - 1:30]
========================================================================================================================
• Screen: Tab 3 ("🤖 Gemini AI Advisor & Scenarios")
• Cursor Action:
  - [0:55]: Click Tab 3.
  - [0:58]: Click "🚀 Generate Strategic Advisory Report" on the left card.
  - [1:05]: Highlight the generated 3-part Markdown audit (Health Diagnosis, Spending Cuts, 30-Day Sprint).
  - [1:15]: Move cursor to the right column and click the quick chip: "✈️ Afford ₹12,000 flight?".
  - [1:22]: Highlight the Assistant's response showing the live headroom calculation and instant **VERDICT**.

========================================================================================================================
ACT IV: DATA GOVERNANCE & CLOSING [1:30 - 2:00]
========================================================================================================================
• Screen: Tab 4 ──> Full View
• Cursor Action:
  - [1:30]: Click Tab 4 ("📑 Transaction Ledger").
  - [1:34]: Type "Grocery" or "Rent" into the search bar, then click "📥 Download CSV".
  - [1:45]: Scroll back to top or switch back to Tab 2 / Top KPI Ribbon for a clean, visually striking closing frame.
  - [1:58]: Conclude speech and pause for 2 seconds before stopping the recording.
========================================================================================================================
```

---

## 🌟 Pro-Recording Tip Checklist
1. **Never rush speech**: If an API call takes 2 extra seconds, continue speaking your scripted narration seamlessly—the UI will catch up.
2. **Smooth Clicks**: Avoid erratic double-clicking; single, deliberate clicks look crisp and professional on video.
3. **No Dead Air**: Use the transition phrases whenever switching tabs.
