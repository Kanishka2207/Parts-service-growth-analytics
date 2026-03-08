"""
=============================================================================
02_etl_master_dataset.py
CAT Parts & Service Growth Analytics
=============================================================================
Stage 2: ETL — Build the Master Analytical Dataset

Joins the three cleaned tables (PTOS, Equipment Units, Sales Channel),
computes all derived KPIs used by the dashboard, and produces the single
master CSV that feeds both the Excel dashboard and the Tableau workbook.

Input:  data/processed/ptos_clean.csv
        data/processed/equipment_units_clean.csv
        data/processed/sales_channel_clean.csv
Output: data/processed/master_dataset.csv
        data/processed/kpi_summary.csv
        data/processed/segment_summary.csv
        data/processed/category_summary.csv
        data/processed/region_summary.csv
        data/processed/salesperson_summary.csv
        data/processed/channel_mix.csv
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────
PROC = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

# ── 1. LOAD CLEAN TABLES ──────────────────────────────────────────────────
print("=" * 60)
print("STAGE 1 — LOAD CLEAN DATA")
print("=" * 60)

ptos    = pd.read_csv(os.path.join(PROC, "ptos_clean.csv"))
equip   = pd.read_csv(os.path.join(PROC, "equipment_units_clean.csv"))
channel = pd.read_csv(os.path.join(PROC, "sales_channel_clean.csv"))

print(f"  PTOS    : {len(ptos):,} rows")
print(f"  Equip   : {len(equip):,} rows")
print(f"  Channel : {len(channel):,} rows")

# ── 2. JOIN ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 2 — JOIN & ENRICH")
print("=" * 60)

# Aggregate equipment per customer (some customers appear multiple times)
equip_agg = equip.groupby("customer_id")["equipment_units"].sum().reset_index()

# Aggregate channel per customer
channel_agg = channel.groupby("customer_id").agg(
    work_order_sales=("work_order_sales", "sum"),
    otc_sales=("otc_sales", "sum"),
    total_channel_sales=("total_channel_sales", "sum"),
).reset_index()

master = ptos.copy()
master = master.merge(equip_agg,   on="customer_id", how="left")
master = master.merge(channel_agg, on="customer_id", how="left")

# Fill join nulls
master["equipment_units"]     = master["equipment_units"].fillna(0).astype(int)
master["work_order_sales"]    = master["work_order_sales"].fillna(0)
master["otc_sales"]           = master["otc_sales"].fillna(0)
master["total_channel_sales"] = master["total_channel_sales"].fillna(0)

# ── 3. DERIVED FEATURES ───────────────────────────────────────────────────
# Revenue per unit
master["rev_per_unit"] = np.where(
    master["equipment_units"] > 0,
    master["total_sales"] / master["equipment_units"], 0
)
master["opp_per_unit"] = np.where(
    master["equipment_units"] > 0,
    master["total_opp"] / master["equipment_units"], 0
)

# POPS-C band for segmentation
def popsc_band(p):
    if p == 0:   return "No Sales"
    if p < 25:   return "Critical (<25%)"
    if p < 50:   return "Low (25–50%)"
    if p < 75:   return "Moderate (50–75%)"
    return "Strong (≥75%)"

master["popsc_band"] = master["popsc"].apply(popsc_band)

# Channel mix flags
master["wo_share"]  = np.where(master["total_channel_sales"] > 0,
                               master["work_order_sales"] / master["total_channel_sales"] * 100, 0)
master["otc_share"] = np.where(master["total_channel_sales"] > 0,
                               master["otc_sales"] / master["total_channel_sales"] * 100, 0)

print(f"  Master dataset shape : {master.shape}")
print(f"  Unique customers     : {master['customer_id'].nunique():,}")
master.to_csv(os.path.join(PROC, "master_dataset.csv"), index=False)
print(f"  ✓  Saved → data/processed/master_dataset.csv")

# ── 4. KPI SUMMARY ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 3 — KPI AGGREGATIONS")
print("=" * 60)

tot_opp   = master["total_opp"].sum()
tot_sales = master["total_sales"].sum()
tot_gap   = tot_opp - tot_sales
popsc_overall = tot_sales / tot_opp * 100
zero_sales_n  = (master["total_sales"] == 0).sum()
zero_sales_opp = master.loc[master["total_sales"] == 0, "total_opp"].sum()

kpi = pd.DataFrame([
    {"metric": "total_market_opportunity",  "value": tot_opp},
    {"metric": "total_realized_sales",      "value": tot_sales},
    {"metric": "revenue_gap",               "value": tot_gap},
    {"metric": "popsc_pct",                 "value": round(popsc_overall, 2)},
    {"metric": "total_customers",           "value": master["customer_id"].nunique()},
    {"metric": "zero_sales_customers",      "value": zero_sales_n},
    {"metric": "zero_sales_opportunity",    "value": zero_sales_opp},
    {"metric": "popsc_target_75_gap",       "value": tot_opp * 0.75 - tot_sales},
])

for _, row in kpi.iterrows():
    print(f"  {row['metric']:<36} : {row['value']:>15,.1f}")

kpi.to_csv(os.path.join(PROC, "kpi_summary.csv"), index=False)
print(f"\n  ✓  Saved → data/processed/kpi_summary.csv")

# ── 5. SEGMENT SUMMARY ───────────────────────────────────────────────────
seg = master[master["segment"].isin(["Do It Myself", "Do It For Me", "Work With Me"])]\
      .groupby("segment").agg(
    customers   =("customer_id", "nunique"),
    opportunity =("total_opp",   "sum"),
    sales       =("total_sales", "sum"),
    fleet_units =("equipment_units", "sum"),
).reset_index()
seg["gap"]   = seg["opportunity"] - seg["sales"]
seg["popsc"] = seg["sales"] / seg["opportunity"] * 100

seg.to_csv(os.path.join(PROC, "segment_summary.csv"), index=False)
print(f"  ✓  Saved → data/processed/segment_summary.csv")
print(seg.to_string(index=False))

# ── 6. CATEGORY SUMMARY ──────────────────────────────────────────────────
categories = {
    "Labor"            : ("labor_opp",  "labor_sales"),
    "Engine"           : ("eng_opp",    "eng_sales"),
    "Drive Train"      : ("dt_opp",     "dt_sales"),
    "Hydraulics"       : ("hyd_opp",    "hyd_sales"),
    "Filters & Fluids" : ("ff_opp",     "ff_sales"),
    "Undercarriage"    : ("uc_opp",     "uc_sales"),
    "Maintenance Parts": ("maint_opp",  "maint_sales"),
    "GET"              : ("get_opp",    "get_sales"),
}

cat_rows = []
for name, (opp_col, sales_col) in categories.items():
    if opp_col in master.columns:
        opp   = master[opp_col].sum()
        sales = master[sales_col].sum()
        gap   = opp - sales
        popsc = sales / opp * 100 if opp > 0 else 0
        status = "CRITICAL" if popsc < 40 else ("FOCUS" if popsc < 60 else "STRONG")
        cat_rows.append({"category": name, "opportunity": opp, "sales": sales,
                         "gap": gap, "popsc": round(popsc, 1), "status": status})

cat_df = pd.DataFrame(cat_rows).sort_values("gap", ascending=False)
cat_df.to_csv(os.path.join(PROC, "category_summary.csv"), index=False)
print(f"\n  ✓  Saved → data/processed/category_summary.csv")
print(cat_df.to_string(index=False))

# ── 7. REGION SUMMARY ────────────────────────────────────────────────────
reg = master[master["region"] != "OTHER"].groupby("region").agg(
    customers   =("customer_id", "nunique"),
    opportunity =("total_opp",   "sum"),
    sales       =("total_sales", "sum"),
).reset_index()
reg["gap"]   = reg["opportunity"] - reg["sales"]
reg["popsc"] = reg["sales"] / reg["opportunity"] * 100
reg["gap_share_pct"] = reg["gap"] / reg["gap"].sum() * 100
reg["priority"] = reg["gap"].apply(
    lambda g: "HIGH" if g > 10_000_000 else ("MEDIUM" if g > 5_000_000 else "MONITOR"))
reg = reg.sort_values("gap", ascending=False)

reg.to_csv(os.path.join(PROC, "region_summary.csv"), index=False)
print(f"\n  ✓  Saved → data/processed/region_summary.csv")
print(reg.to_string(index=False))

# ── 8. SALESPERSON SUMMARY ───────────────────────────────────────────────
sp = master.groupby("salesperson_name").agg(
    customers   =("customer_id", "nunique"),
    opportunity =("total_opp",   "sum"),
    sales       =("total_sales", "sum"),
).reset_index()
sp["gap"]   = sp["opportunity"] - sp["sales"]
sp["popsc"] = sp["sales"] / sp["opportunity"] * 100
sp["action"] = sp["popsc"].apply(
    lambda p: "Urgent Coaching" if p < 25 else
              ("Support Needed"   if p < 50 else
               ("Account Planning" if p < 75 else "Sustain")))
sp = sp.sort_values("gap", ascending=False).head(20)

sp.to_csv(os.path.join(PROC, "salesperson_summary.csv"), index=False)
print(f"\n  ✓  Saved → data/processed/salesperson_summary.csv  (top 20 by gap)")

# ── 9. CHANNEL MIX ───────────────────────────────────────────────────────
ch_mix = master[master["region"] != "OTHER"].groupby("region").agg(
    wo_sales  =("work_order_sales", "sum"),
    otc_sales =("otc_sales",        "sum"),
).reset_index()
ch_mix["total"] = ch_mix["wo_sales"] + ch_mix["otc_sales"]
ch_mix["wo_pct"]  = ch_mix["wo_sales"]  / ch_mix["total"] * 100
ch_mix["otc_pct"] = ch_mix["otc_sales"] / ch_mix["total"] * 100
ch_mix = ch_mix.sort_values("total", ascending=False)

ch_mix.to_csv(os.path.join(PROC, "channel_mix.csv"), index=False)
print(f"  ✓  Saved → data/processed/channel_mix.csv")

print("\n\nETL complete. All analytical tables ready.")
