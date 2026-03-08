# Parts & Service Growth Strategy
## PTOS Performance Analysis · Business Intelligence Case Study

---

> **$103.2M in total addressable market. $54.1M converted. $49.1M left on the table — every year.**
>
> This project delivers a complete, executive-ready business intelligence analysis identifying where a Caterpillar equipment dealership is losing revenue and exactly what to do about it.

---

## Project Overview

A regional Caterpillar equipment dealership operates a parts and service division serving **7,859 customers** across **9 regions**. Revenue performance is tracked using the **POPS-C metric** (Parts and Service Opportunity Conversion):

```
POPS-C (%) = Realized Sales ÷ Total Opportunity × 100
```

Opportunity values are algorithmically modelled from each customer's equipment fleet — estimating annual parts and labor requirements. A POPS-C of 100% means every available dollar has been captured. The current rate of **52.5%** means nearly half of available revenue goes uncaptured annually.

**This analysis quantifies the gap, diagnoses its root causes across segments, categories, regions, and salespeople, and delivers a prioritised growth roadmap.**

---

## Business Problem

Leadership needed answers to four questions:

1. **What is the current situation?** — Baseline POPS-C, total market, realized revenue, and gap
2. **Where are the opportunities?** — Which segments, regions, and categories carry the most untapped potential?
3. **What actions should be taken?** — Ranked recommendations with estimated revenue impact
4. **What additional data is needed?** — Gaps and follow-on analysis to sharpen the findings

---

## Key Metrics

| Metric | Value |
|---|---|
| 📦 Total Market Opportunity | **$103.2M** |
| 💰 Realized Sales (POPS-C 52.5%) | **$54.1M** |
| 🔴 Revenue Gap | **$49.1M** |
| 👻 Zero-Sales Customers | **5,927 / 7,859 (75%)** |
| 🎯 Incremental Revenue to 75% Target | **+$23.3M** |
| 📍 Regions Analysed | **9** |
| 🏗️ Parts Categories | **8** |
| 👥 Unique Customers | **7,859** |

---

## Dataset Overview

| Source | Sheet | Records | Description |
|---|---|---|---|
| `business_case_raw_data.xlsx` | PTOS_source | 10,165 rows | Parts & labor opportunity vs sales by customer, category, and salesperson |
| `business_case_raw_data.xlsx` | Equipment units | 10,165 rows | Fleet size (# machines/engines) per customer |
| `business_case_raw_data.xlsx` | Sales channel | 6,660 rows | Work Order vs Over-the-Counter sales split by customer |

**Processed master dataset:** `data/processed/master_dataset.csv` — 10,165 rows × 42 fields including all derived KPIs, joins, and segmentation flags. Single source of truth for both the Excel dashboard and Tableau workbook.

---

## Tools Used

| Tool | Purpose |
|---|---|
| **Python** (pandas, matplotlib) | ETL pipeline, data cleaning, EDA, chart generation |
| **Microsoft Excel** | Dashboard, SUMIF analysis, KPI cards, pivot analysis |
| **Tableau** | Interactive dashboard, dynamic filtering, geographic views |
| **SQL** | Equivalent analytical queries (PostgreSQL / BigQuery compatible) |

---

## Methodology

### Stage 1 — Data Cleaning (`notebooks/01_data_cleaning.py`)
- Ingested 3 source sheets from raw XLSX
- Standardised column names, customer ID types, and segment labels
- Extracted 9-region lookup from 2-digit city code prefix
- Validated nulls, negatives, and type mismatches
- **Output:** `ptos_clean.csv`, `equipment_units_clean.csv`, `sales_channel_clean.csv`, `data_quality_report.txt`

### Stage 2 — ETL & Master Dataset (`notebooks/02_etl_master_dataset.py`)
- Left-joined Equipment Units and Sales Channel onto PTOS by `customer_id`
- Computed 15+ derived fields: `total_opp`, `total_sales`, `revenue_gap`, `popsc`, `popsc_band`, `rev_per_unit`, `wo_share`, `otc_share`
- Aggregated 6 analytical summary tables
- **Output:** `master_dataset.csv` + 6 summary CSVs

### Stage 3 — EDA & Visualisations (`notebooks/03_eda_and_visualizations.py`)
- Segment performance: DIM vs DIFM vs WWM opportunity, sales, and POPS-C
- Category analysis: POPS-C and gap for all 8 parts categories with status tiers
- Regional analysis: gap distribution and opportunity-vs-conversion scatter
- Zero-sales deep-dive: $49.8M dormant opportunity by segment and region
- Salesperson scorecard: top 15 revenue gaps with coaching action flags

---

## Key Findings

### Finding 1 — Customer Segmentation: The DIM Conversion Problem

| Segment | Customers | Opportunity | POPS-C | Gap |
|---|---|---|---|---|
| **Do It Myself (DIM)** | 6,016 (76%) | $78.4M | **13.5% 🔴** | $67.8M |
| **Do It For Me (DIFM)** | 296 (4%) | $12.7M | **113% 🟢** | — |
| **Work With Me (WWM)** | 151 (2%) | $12.2M | **79% 🟢** | $2.6M |

Three-quarters of all customers convert only 13.5% of their opportunity. The DIFM segment — same product, same market — converts at 113%. The capability exists. The engagement model does not reach DIM customers.

---

### Finding 2 — Labor is the Single Largest Revenue Lever ($19.2M Gap)

| Category | POPS-C | Status | Gap |
|---|---|---|---|
| Engine | 85.2% | 🟢 STRONG | $2.3M |
| Drive Train | 82.7% | 🟢 STRONG | $1.6M |
| GET | 56.7% | 🟡 FOCUS | $2.6M |
| Filters & Fluids | 41.0% | 🟡 FOCUS | $6.8M |
| Undercarriage | 44.7% | 🟡 FOCUS | $4.1M |
| Maintenance Parts | 33.5% | 🔴 CRITICAL | $4.1M |
| Hydraulics | 31.0% | 🔴 CRITICAL | $9.7M |
| **Labor** | **36.9%** | 🔴 **CRITICAL** | **$19.2M** |

Labor ($30.5M total opportunity) is the gateway to the full service relationship. A Work Order customer also purchases consumables, filters, and parts. Converting DIM customers to labor engagement is the highest-ROI action available.

---

### Finding 3 — Ankara Holds 37% of the Entire National Gap

| Region | Opportunity | POPS-C | Gap | Priority |
|---|---|---|---|---|
| **ANKARA** | $43.4M | 58.0% | **$18.2M** | 🔴 HIGH |
| IZMIR | $12.0M | 35.5% | $7.7M | 🟠 MEDIUM |
| ISTANBUL | $11.9M | 48.4% | $6.2M | 🟠 MEDIUM |
| ADANA | $12.6M | 51.7% | $6.1M | 🟠 MEDIUM |
| DIYARBAKIR | $7.3M | 63.3% | $2.7M | 🟡 MONITOR |

Izmir has the worst POPS-C of any mid-large market (35.5%) — indicating a structural penetration issue, not just a volume shortfall.

---

### Finding 4 — 5,927 Zero-Sales Customers Hold $49.8M in Dormant Opportunity

75% of the customer base generated zero revenue despite being registered accounts with modelled opportunity. These are not cold prospects — they are existing relationships with quantified need. The fastest revenue recovery path requires no new customer acquisition.

---

### Finding 5 — Three Salespeople Account for $16.6M in Combined Gap

One rep manages 564 customers at 6.6% POPS-C — structural under-coverage that can be directly addressed through portfolio redistribution and coaching.

---

## Business Recommendations

| Priority | Action | Est. Impact | Timeline |
|---|---|---|---|
| **P1** | Reactivate zero-sales accounts — rank by opportunity, assign top 500 to senior reps | $2–3M | 0–90 days |
| **P2** | Launch Preventive Maintenance Contracts (PMC) to convert DIM → labor engagement | $5–8M | 3–12 months |
| **P3** | Hydraulics Health Check + consumables bundling programme | $3–5M | 3–9 months |
| **P4** | Salesperson coaching + portfolio redistribution for bottom-quartile reps | $4–6M | 1–6 months |
| **P5** | Izmir intensive growth initiative — win/loss research + dedicated coverage | $2–4M | 6–12 months |
| **P6** | Convert OTC-dominant accounts to Work Order relationships | $2–4M | 6–18 months |

**Combined upside at 75% POPS-C target: ~$23.3M incremental annual revenue**

---

## Business Impact

| Scenario | Target POPS-C | Incremental Revenue |
|---|---|---|
| Conservative (P1 + P4 only) | 57% | ~$4.7M |
| Base Case (P1–P4) | 63% | ~$11.0M |
| Stretch (all 6 priorities) | **75%** | **~$23.3M** |

Projections apply expected POPS-C improvement rates to the existing $103.2M opportunity base. No new customer acquisition required.

---

## Dashboard Overview

### Excel Dashboard — `dashboards/CAT_Parts_Service_Dashboard.xlsx`

| Sheet | Content |
|---|---|
| **DASHBOARD** | Executive KPI cards + 4 chart views |
| **RAW_DATA** | Full 10,165-row cleaned PTOS dataset |
| **CALCULATIONS** | All SUMIF formulas and computed KPIs |
| **VIZ_DATA** | Aggregated tables powering each chart |

### Tableau Dashboard — `dashboards/dashboard.twbx`

---

## Repository Structure

```
parts-service-growth-analytics/
│
├── README.md                                    ← This file
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   └── business_case_raw_data.xlsx          ← Original 3-sheet PTOS dataset
│   └── processed/
│       ├── master_dataset.csv                   ← Full analytical table (10,165 × 42) — Tableau source
│       ├── ptos_clean.csv                       ← Cleaned PTOS records
│       ├── equipment_units_clean.csv            ← Fleet size per customer
│       ├── sales_channel_clean.csv              ← Work Order vs OTC channel data
│       ├── kpi_summary.csv                      ← Grand total KPIs
│       ├── segment_summary.csv                  ← DIM / DIFM / WWM aggregates
│       ├── category_summary.csv                 ← Parts category POPS-C + gaps
│       ├── region_summary.csv                   ← Regional revenue analysis
│       ├── salesperson_summary.csv              ← Top 20 salesperson gaps
│       ├── channel_mix.csv                      ← Work Order vs OTC by region
│       └── data_quality_report.txt              ← Automated validation output
│
├── notebooks/
│   ├── 01_data_cleaning.py                      ← Stage 1: ingest, validate, clean
│   ├── 02_etl_master_dataset.py                 ← Stage 2: join, derive KPIs, build summaries
│   └── 03_eda_and_visualizations.py             ← Stage 3: EDA + chart generation
│
├── dashboards/
│   ├── CAT_Parts_Service_Dashboard.xlsx         ← Excel dashboard (4 views)
│   ├── dashboard.twbx                           ← Tableau packaged workbook
│
├── sql/
│   └── analysis_queries.sql                    ← 10 analytical query sections
│
└── Recommendations/
    └── Parts_Service_Growth_Strategy.pptx      ← Executive presentation — final deliverable
```

---

## How to Run

### Python Pipeline
```bash
pip install -r requirements.txt

python notebooks/01_data_cleaning.py        # Stage 1: clean → data/processed/
python notebooks/02_etl_master_dataset.py   # Stage 2: ETL → master_dataset.csv + summaries
python notebooks/03_eda_and_visualizations.py  # Stage 3: EDA + charts
```

### Excel Dashboard
Open `dashboards/CAT_Parts_Service_Dashboard.xlsx` directly. All formulas reference the RAW_DATA sheet and recalculate automatically.

### Executive Presentation
Open `Recommendation/Parts_Service_Growth_Strategy.pptx` in PowerPoint — the final leadership deliverable.

---

## SQL Reference

`sql/analysis_queries.sql` covers all 10 analytical dimensions in PostgreSQL/BigQuery syntax:

| Section | Query |
|---|---|
| 1 | Grand Total KPIs |
| 2 | POPS-C by Customer Segment |
| 3 | Parts Category Analysis (unpivoted) |
| 4 | Revenue Gap by Region |
| 5 | Top 20 Salespeople by Revenue Gap |
| 6 | Sales Channel Mix by Region |
| 7 | Zero-Sales Account Priority List |
| 8 | POPS-C Band Distribution |
| 9 | Fleet Size vs POPS-C Correlation |
| 10 | Revenue Impact Scenario Modelling |

---

## Skills Demonstrated

| Competency | Evidence |
|---|---|
| Data Engineering | 3-stage Python pipeline: raw ingestion → ETL → master dataset |
| Business Intelligence | KPI design, dashboard architecture, live SUMIF logic |
| Exploratory Data Analysis | Segmentation, distribution, correlation, outlier analysis |
| Strategic Analysis | Gap prioritisation, scenario modelling, 90-day action roadmap |
| Data Storytelling | 10,165 rows → $23.3M executive recommendation |
| Multi-tool Delivery | Python + Excel + Tableau + SQL — consistent, reproducible outputs |

---

*Data anonymised for confidentiality. All customer and salesperson names have been masked in the source dataset.*
