"""
=============================================================================
01_data_cleaning.py
CAT Parts & Service Growth Analytics
=============================================================================
Stage 1: Raw Data Ingestion, Validation, and Cleaning

Reads the three source sheets from the raw XLSX business case file,
performs data quality checks, standardises columns, and outputs
clean CSV files ready for downstream ETL and analysis.

Input:  data/raw/business_case_raw_data.xlsx
Output: data/processed/ptos_clean.csv
        data/processed/equipment_units_clean.csv
        data/processed/sales_channel_clean.csv
        data/processed/data_quality_report.txt
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────
RAW_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "raw",
                         "business_case_raw_data.xlsx")
OUT_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT_PATH, exist_ok=True)

# ── 1. LOAD RAW SHEETS ────────────────────────────────────────────────────
print("=" * 60)
print("STAGE 1 — RAW DATA INGESTION")
print("=" * 60)

ptos_raw = pd.read_excel(RAW_PATH, sheet_name="PTOS_source")
equip_raw = pd.read_excel(RAW_PATH, sheet_name="Equipment units")
channel_raw = pd.read_excel(RAW_PATH, sheet_name="Sales channel")

print(f"  PTOS source     : {len(ptos_raw):,} rows × {ptos_raw.shape[1]} cols")
print(f"  Equipment units : {len(equip_raw):,} rows × {equip_raw.shape[1]} cols")
print(f"  Sales channel   : {len(channel_raw):,} rows × {channel_raw.shape[1]} cols")

# ── 2. CLEAN PTOS SOURCE ──────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 2 — CLEANING: PTOS SOURCE")
print("=" * 60)

df = ptos_raw.copy()

# Standardise column names
df.columns = [str(c).strip().lower().replace("  ", " ").replace(" ", "_")
              for c in df.columns]

rename_map = {
    "salesman"                                         : "salesperson",
    "customer_id"                                      : "customer_id",
    "segmentation"                                     : "segment",
    "city"                                             : "city_code",
    "undercarriage_opportunity"                        : "uc_opp",
    "undercarriage_sales"                              : "uc_sales",
    "engine_opportunity"                               : "eng_opp",
    "engine_sales"                                     : "eng_sales",
    "get_opportunity"                                  : "get_opp",
    "get_sales"                                        : "get_sales",
    "drive_train_opportunity"                          : "dt_opp",
    "drive_train_sales"                                : "dt_sales",
    "hydraulics_opportunity"                           : "hyd_opp",
    "hydraulics_sales"                                 : "hyd_sales",
    "filters_&_fluids_opportunity"                     : "ff_opp",
    "filters_&_fluids_sales"                           : "ff_sales",
    "maintenance_parts_and_supplies_opportunity"       : "maint_opp",
    "maintenance_parts_and_supplies_sales"             : "maint_sales",
    "structural,_appearance,_and_other_parts_opportunity": "struct_opp",
    "structural,_appearance,_and_other_parts_sales"    : "struct_sales",
    "labor_opportunity"                                : "labor_opp",
    "labor_sales"                                      : "labor_sales",
    "parts_sales"                                      : "parts_sales",
    "parts_opportunity"                                : "parts_opp",
}
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

# Convert customer_id to string
df["customer_id"] = df["customer_id"].astype(str).str.strip()

# Extract region from city_code (first 2 chars are region code)
region_map = {
    "00": "ISTANBUL", "01": "ANKARA",   "02": "IZMIR",
    "03": "ADANA",    "10": "TRAKYA",   "11": "BURSA",
    "31": "ANTALYA",  "43": "DIYARBAKIR","61": "TRABZON",
}
df["region_code"] = df["city_code"].astype(str).str[:2].str.strip()
df["region"]      = df["region_code"].map(region_map).fillna("OTHER")

# Extract salesperson name only (strip the " - NNN" ID suffix)
df["salesperson_name"] = df["salesperson"].str.extract(r"^(.*?)\s*-\s*\d+$")[0]\
                                          .fillna(df["salesperson"]).str.strip()

# Standardise segment labels
segment_clean = {
    "Do It Myself"              : "Do It Myself",
    "Do It For Me"              : "Do It For Me",
    "Work With Me"              : "Work With Me",
    "No Product Segment Assigned": "Unassigned",
}
df["segment"] = df["segment"].map(segment_clean).fillna("Unassigned")

# Fill numeric nulls with 0
num_cols = [c for c in df.columns if any(x in c for x in
            ["_opp", "_sales", "parts_opp", "parts_sales"])]
df[num_cols] = df[num_cols].fillna(0).clip(lower=0)

# Derived totals
part_opp_cols   = [c for c in df.columns if c.endswith("_opp")  and c != "parts_opp"  and c != "labor_opp"]
part_sales_cols = [c for c in df.columns if c.endswith("_sales") and c != "parts_sales" and c != "labor_sales"]

df["total_parts_opp"]   = df[part_opp_cols].sum(axis=1)
df["total_parts_sales"] = df[part_sales_cols].sum(axis=1)
df["total_opp"]         = df["total_parts_opp"] + df.get("labor_opp", 0)
df["total_sales"]       = df["total_parts_sales"] + df.get("labor_sales", 0)
df["revenue_gap"]       = df["total_opp"] - df["total_sales"]
df["popsc"]             = np.where(df["total_opp"] > 0,
                                   df["total_sales"] / df["total_opp"] * 100, 0)

print(f"  Rows after cleaning  : {len(df):,}")
print(f"  Unique customers     : {df['customer_id'].nunique():,}")
print(f"  Unique salespeople   : {df['salesperson_name'].nunique()}")
print(f"  Regions              : {sorted(df['region'].unique())}")
print(f"  Segments             : {sorted(df['segment'].unique())}")
null_check = df[num_cols].isnull().sum().sum()
print(f"  Null values in numerics: {null_check}")

df.to_csv(os.path.join(OUT_PATH, "ptos_clean.csv"), index=False)
print(f"\n  ✓  Saved → data/processed/ptos_clean.csv")

# ── 3. CLEAN EQUIPMENT UNITS ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 3 — CLEANING: EQUIPMENT UNITS")
print("=" * 60)

equip = equip_raw.copy()
equip.columns = ["customer_name_raw", "equipment_units"]
equip = equip.dropna(subset=["equipment_units"])
# Extract customer_id from the raw name (format: "NAME - ID")
equip["customer_id"] = equip["customer_name_raw"].astype(str)\
                            .str.extract(r"-\s*([A-Za-z0-9]+)\s*$")[0]\
                            .str.strip()
equip["equipment_units"] = pd.to_numeric(equip["equipment_units"], errors="coerce").fillna(0).astype(int)
equip = equip.drop(columns=["customer_name_raw"])

print(f"  Rows after cleaning  : {len(equip):,}")
equip.to_csv(os.path.join(OUT_PATH, "equipment_units_clean.csv"), index=False)
print(f"  ✓  Saved → data/processed/equipment_units_clean.csv")

# ── 4. CLEAN SALES CHANNEL ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 4 — CLEANING: SALES CHANNEL")
print("=" * 60)

ch = channel_raw.copy()
ch.columns = ch.columns.str.strip().str.lower().str.replace(" ", "_")
# Rename to standard
ch = ch.rename(columns={
    "customer_name"          : "customer_name_raw",
    "work_order_sales"       : "work_order_sales",
    "over_the_counter_sales" : "otc_sales",
})
ch["customer_id"] = ch["customer_name_raw"].astype(str)\
                        .str.extract(r"-\s*([A-Za-z0-9]+)\s*-")[0]\
                        .str.strip()
ch["work_order_sales"] = pd.to_numeric(ch["work_order_sales"], errors="coerce").fillna(0)
ch["otc_sales"]        = pd.to_numeric(ch["otc_sales"],        errors="coerce").fillna(0)
ch["total_channel_sales"] = ch["work_order_sales"] + ch["otc_sales"]
ch = ch.drop(columns=["customer_name_raw"])

print(f"  Rows after cleaning  : {len(ch):,}")
ch.to_csv(os.path.join(OUT_PATH, "sales_channel_clean.csv"), index=False)
print(f"  ✓  Saved → data/processed/sales_channel_clean.csv")

# ── 5. DATA QUALITY REPORT ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 5 — DATA QUALITY REPORT")
print("=" * 60)

report_lines = [
    "DATA QUALITY REPORT — CAT Parts & Service Analytics",
    "=" * 60,
    f"Generated from: business_case_raw_data.xlsx",
    "",
    "PTOS SOURCE",
    f"  Total records     : {len(df):,}",
    f"  Unique customers  : {df['customer_id'].nunique():,}",
    f"  Zero-sales records: {(df['total_sales'] == 0).sum():,}  "
    f"({(df['total_sales']==0).mean()*100:.1f}%)",
    f"  Segments          : {dict(df['segment'].value_counts())}",
    f"  Regions           : {dict(df['region'].value_counts())}",
    "",
    "EQUIPMENT UNITS",
    f"  Total records     : {len(equip):,}",
    f"  Total fleet units : {equip['equipment_units'].sum():,}",
    "",
    "SALES CHANNEL",
    f"  Total records     : {len(ch):,}",
    f"  Total WO sales ($): {ch['work_order_sales'].sum():,.0f}",
    f"  Total OTC sales ($): {ch['otc_sales'].sum():,.0f}",
    "",
    "GRAND KPIs",
    f"  Total Market Opportunity : ${df['total_opp'].sum():,.0f}",
    f"  Total Realized Sales     : ${df['total_sales'].sum():,.0f}",
    f"  Revenue Gap              : ${df['revenue_gap'].sum():,.0f}",
    f"  POPS-C Conversion Rate   : {df['total_sales'].sum()/df['total_opp'].sum()*100:.1f}%",
]

report_text = "\n".join(report_lines)
print("\n".join(report_lines[6:]))
with open(os.path.join(OUT_PATH, "data_quality_report.txt"), "w") as f:
    f.write(report_text)
print(f"\n  ✓  Saved → data/processed/data_quality_report.txt")
print("\nData cleaning complete.")
