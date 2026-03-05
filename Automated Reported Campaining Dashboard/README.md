# 📊 Automated Campaign Reporting Pipeline

> End-to-end data workflow that automates constituent campaign data intake from Google Sheets (simulated locally), runs 21 validation checks, calculates performance metrics, stores everything in SQLite, and displays a Streamlit monitoring dashboard — replacing a **6-hour-per-month** manual reporting process across 3 university advancement departments.

---

## 🏗️ Project Architecture

```
Automated Reported Campaining Dashboard/
│
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
│
├── data/
│   ├── inputs/                        # Generated CSV source files
│   │   ├── annual_giving_campaigns.csv    (120 rows)
│   │   ├── alumni_relations_events.csv    (80 rows)
│   │   └── major_gifts_outreach.csv       (50 rows)
│   └── campaign_reports.db            # SQLite database (auto-created)
│
├── pipeline/
│   ├── __init__.py
│   ├── orchestrator.py                # End-to-end pipeline runner
│   │
│   ├── generator/
│   │   ├── __init__.py
│   │   └── generator.py              # Synthetic data generation (faker)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_utils.py               # SQLite connection helpers
│   │   ├── schema.py                  # Table definitions (5 tables)
│   │   └── loader.py                  # CSV → SQLite loader
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── rules.py                   # 21 validation rule definitions
│   │   └── validator.py              # Validation engine + logging
│   │
│   └── metrics/
│       ├── __init__.py
│       └── calculator.py             # KPI calculator (16 metric types)
│
└── dashboard/
    └── app.py                         # 5-page Streamlit dashboard
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.12** | Core language |
| **Faker** | Synthetic data generation |
| **Pandas** | Data manipulation & transformation |
| **SQLite** | Local database storage |
| **Streamlit** | Interactive web dashboard |
| **Plotly** | Data visualizations (charts, graphs, heatmaps) |

---

## 🚀 Complete Execution Guide

### Prerequisites

- Python 3.9+ installed
- pip package manager

### Step 1: Clone & Navigate

```bash
cd "Automated Reported Campaining Dashboard"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: `faker`, `pandas`, `streamlit`, `plotly`

### Step 3: Generate Synthetic Data

```bash
python pipeline/generator/generator.py
```

**What it does:**
- Uses the `faker` library with a fixed seed (42) for reproducibility
- Generates **3 CSV files** into `data/inputs/`:

| Output File | Rows | Department | Description |
|------------|------|------------|-------------|
| `annual_giving_campaigns.csv` | 120 | Annual Giving | Email campaigns with delivery, open, click, and gift metrics |
| `alumni_relations_events.csv` | 80 | Alumni Relations | Events with RSVP, attendance, donation, and satisfaction data |
| `major_gifts_outreach.csv` | 50 | Major Gifts | Prospect outreach with touch, meeting, proposal, and commitment data |

**Expected output:**
```
============================================================
  Automated Campaign Reporting — Data Generator
============================================================
✅  annual_giving_campaigns.csv  → 120 rows
✅  alumni_relations_events.csv   → 80 rows
✅  major_gifts_outreach.csv      → 50 rows

All files saved to: data/inputs
============================================================
```

### Step 4: Run the Full Pipeline

```bash
python -m pipeline.orchestrator
```

**What it does — 4 sequential stages:**

#### Stage 1/4 — Create Database Schema
- Creates SQLite database at `data/campaign_reports.db`
- Defines **5 tables**:
  - `annual_giving_campaigns` — raw campaign data
  - `alumni_relations_events` — raw event data
  - `major_gifts_outreach` — raw prospect data
  - `validation_log` — audit trail of all checks
  - `campaign_metrics` — computed KPIs

#### Stage 2/4 — Load CSV Data
- Reads all 3 CSV files from `data/inputs/`
- Inserts **250 total rows** into the corresponding SQLite tables

#### Stage 3/4 — Run Validation Checks
- Executes **21 validation rules** across all 3 tables:

| # | Rule | Table |
|---|------|-------|
| 1 | Null check on required columns | Annual Giving |
| 2 | Date logic (end > start) | Annual Giving |
| 3 | Email delivery ≤ sent | Annual Giving |
| 4 | Open rate bounds (0–100%) | Annual Giving |
| 5 | Click-through ≤ opens | Annual Giving |
| 6 | Gift count ≤ sent | Annual Giving |
| 7 | Financial sanity (raised ≥ 0) | Annual Giving |
| 8 | Cost sanity (cost ≥ 0) | Annual Giving |
| 9 | Duplicate campaign_id check | Annual Giving |
| 10 | Department consistency | Annual Giving |
| 11 | Null check on required columns | Alumni Relations |
| 12 | RSVPs ≤ invitations | Alumni Relations |
| 13 | Attendees ≤ RSVPs | Alumni Relations |
| 14 | Financial sanity (donations ≥ 0) | Alumni Relations |
| 15 | Duplicate event_id check | Alumni Relations |
| 16 | Department consistency | Alumni Relations |
| 17 | Null check on required columns | Major Gifts |
| 18 | Meetings ≤ touches | Major Gifts |
| 19 | Financial sanity (committed ≥ 0) | Major Gifts |
| 20 | Duplicate prospect_id check | Major Gifts |
| 21 | Department consistency | Major Gifts |

- Logs every result (rule name, table, PASS/FAIL, fail count, timestamp) to `validation_log`

#### Stage 4/4 — Compute Campaign Metrics
- Calculates **16 KPI types** across all 3 departments:

| Department | Metrics Computed | Rows |
|-----------|-----------------|------|
| Annual Giving | open_rate, ctr, conversion_rate, avg_gift, cost_per_dollar_raised, roi | 720 |
| Alumni Relations | rsvp_rate, attendance_rate, donation_per_attendee, satisfaction_avg, new_contacts_per_event | 400 |
| Major Gifts | meetings_per_touch, proposal_rate, close_rate, avg_gift_size, cultivation_efficiency | 250 |

- Stores all **1,370 metric rows** in `campaign_metrics` table

**Expected output:**
```
============================================================
  🚀  Automated Campaign Reporting Pipeline
============================================================

[1/4] Creating database schema...
✅  Database schema created (5 tables)

[2/4] Loading CSV data into SQLite...
✅  Loaded annual_giving_campaigns.csv → annual_giving_campaigns (120 rows)
✅  Loaded alumni_relations_events.csv → alumni_relations_events (80 rows)
✅  Loaded major_gifts_outreach.csv → major_gifts_outreach (50 rows)
✅  All data loaded into SQLite

[3/4] Running validation checks...
  ✅  Null Check — Annual Giving: PASS
  ✅  Date Logic — end_date > launch_date: PASS
  ✅  Email Delivery — delivered ≤ sent: PASS
  ... (21 total checks)
  Total: 21 passed, 0 failed out of 21 checks

[4/4] Computing campaign metrics...
  ✅  Annual Giving: 120 campaigns × 6 metrics = 720 rows
  ✅  Alumni Relations: 80 events × 5 metrics = 400 rows
  ✅  Major Gifts: 50 prospects × 5 metrics = 250 rows
  Total: 1370 metric rows computed

============================================================
  ✅  Pipeline Complete!
  • Validation: 21/21 checks passed
  • Metrics: 1370 metric rows computed
============================================================
```

### Step 5: Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

Opens at **http://localhost:8501** with 5 interactive pages:

---

## 📊 Dashboard Pages

### Page 1: 🏠 Executive Summary
Top-line KPIs at a glance — total campaigns (250), total raised ($9.57M), avg ROI (12.6x), and 100% validation pass rate. Includes revenue-by-department bar chart and campaign distribution donut chart.

### Page 2: 🏢 Department Comparison
Side-by-side analysis across all 3 departments with three sub-tabs:
- **Performance** — Grouped bar chart of average metrics
- **Radar View** — Radar/spider charts per department
- **Detailed Stats** — Metric cards with department-specific KPIs

### Page 3: 🎯 Campaign Performance Deep Dive
Filterable drill-down into individual campaigns/events/prospects. Includes:
- Department selector (Annual Giving / Alumni Relations / Major Gifts)
- Segment/type/officer filters
- Scatter plots, bar charts, and funnel visualizations
- Full data tables

### Page 4: ✅ Validation & Data Quality
Complete audit trail showing:
- Pass/fail summary with donut chart
- Checks-per-table bar chart
- Validation heatmap (rule × table)
- Full validation log table

### Page 5: 📈 Trend Analysis
Time-series patterns with three sub-tabs:
- **Annual Giving Trends** — Revenue over time + rolling open rate average
- **Event Trends** — Attendance vs donations dual-axis chart + satisfaction trend
- **Gift Pipeline** — Quarterly proposals vs commitments + gift officer performance

---

## 📋 Database Schema

### Raw Data Tables

**annual_giving_campaigns**
| Column | Type | Description |
|--------|------|-------------|
| campaign_id | TEXT (PK) | AG-2023-001 through AG-2024-120 |
| campaign_name | TEXT | e.g., "Spring Annual Fund 2024" |
| department | TEXT | "Annual Giving" |
| launch_date | TEXT | ISO date (Jan 2023 – Dec 2024) |
| end_date | TEXT | launch_date + 14–60 days |
| segment_name | TEXT | All Alumni, Lapsed Donors, etc. |
| records_sent | INTEGER | 500–5,000 |
| emails_delivered | INTEGER | 90–99% of sent |
| emails_opened | INTEGER | 15–35% of delivered |
| links_clicked | INTEGER | 20–50% of opened |
| gifts_received | INTEGER | 1–6% of sent |
| total_raised | REAL | $500–$50,000 |
| campaign_cost | REAL | $200–$5,000 |

**alumni_relations_events**
| Column | Type | Description |
|--------|------|-------------|
| event_id | TEXT (PK) | AR-EVT-001 through AR-EVT-080 |
| event_name | TEXT | e.g., "Homecoming Weekend Gala" |
| department | TEXT | "Alumni Relations" |
| event_type | TEXT | Reunion / Networking / Homecoming / Fundraiser / Volunteer |
| event_date | TEXT | ISO date |
| invitations_sent | INTEGER | 200–3,000 |
| rsvps_received | INTEGER | 15–45% of invitations |
| attendees | INTEGER | 75–95% of RSVPs |
| donations_collected | REAL | $0–$25,000 |
| new_contacts | INTEGER | 5–50 |
| follow_ups_sent | INTEGER | 80–100% of attendees |
| satisfaction_score | REAL | 3.0–5.0 |

**major_gifts_outreach**
| Column | Type | Description |
|--------|------|-------------|
| prospect_id | TEXT (PK) | MG-PR-001 through MG-PR-050 |
| prospect_name | TEXT | Faker-generated name |
| department | TEXT | "Major Gifts" |
| gift_officer | TEXT | One of 8 officers |
| outreach_date | TEXT | ISO date |
| total_touches | INTEGER | 3–20 |
| meetings_held | INTEGER | 1–8 |
| proposals_sent | INTEGER | 0–3 |
| proposal_amount | REAL | $10k–$500k (if proposals > 0) |
| gift_committed | REAL | 50–100% of proposal or $0 |
| commitment_date | TEXT | 30–180 days after outreach |
| cultivation_days | INTEGER | 30–365 |

### Pipeline Tables

**validation_log** — Audit trail of every validation check run  
**campaign_metrics** — Computed KPIs (1,370 rows across 16 metric types)

---

## 🔧 Running Individual Components

```bash
# Run only the data generator
python pipeline/generator/generator.py

# Run only schema creation
python -m pipeline.database.schema

# Run only data loading
python -m pipeline.database.loader

# Run only validation
python -m pipeline.validation.validator

# Run only metrics computation
python -m pipeline.metrics.calculator

# Run the complete pipeline (all 4 stages)
python -m pipeline.orchestrator

# Launch dashboard
streamlit run dashboard/app.py
```

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| Total Records | 250 (120 + 80 + 50) |
| Validation Checks | 21/21 passed |
| KPI Metrics Computed | 1,370 rows |
| Total Raised | ~$9.57M |
| Avg ROI (Annual Giving) | 12.6x |
| Validation Pass Rate | 100% |
| Dashboard Pages | 5 |

---

*Built with Python · SQLite · Streamlit · Plotly · Faker*
