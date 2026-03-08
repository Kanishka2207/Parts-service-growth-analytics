"""
=============================================================================
03_eda_and_visualizations.py
CAT Parts & Service Growth Analytics
=============================================================================
Stage 3: Exploratory Data Analysis + Chart Generation

Produces all chart images saved to /images/.
Charts are also used inside the Excel dashboard and Tableau workbook.

Input:  data/processed/master_dataset.csv  (+ summary CSVs)
Output: images/*.png  (8 publication-quality charts)
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import os, warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────
PROC  = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
IMG   = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(IMG, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────
BG      = "#0F1117"
CARD    = "#1A1D27"
BORDER  = "#2A2D3A"
WHITE   = "#F0F2F8"
MUTED   = "#8890A8"
YELLOW  = "#FFCD11"   # CAT yellow
CYAN    = "#00D4FF"
ORANGE  = "#FF6B35"
RED     = "#EF4444"
GREEN   = "#22C55E"
BLUE    = "#3B82F6"
PURPLE  = "#A855F7"
TEAL    = "#14B8A6"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   CARD,
    "axes.edgecolor":   BORDER,
    "axes.labelcolor":  WHITE,
    "xtick.color":      MUTED,
    "ytick.color":      MUTED,
    "text.color":       WHITE,
    "grid.color":       BORDER,
    "grid.linestyle":   "--",
    "grid.linewidth":   0.5,
    "font.family":      "monospace",
    "figure.dpi":       150,
})

def fmt_m(x, _=None):
    return f"${x/1e6:.1f}M" if abs(x) >= 1e6 else f"${x/1e3:.0f}K"

def save(fig, name):
    path = os.path.join(IMG, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓  {name}")

# ── Load data ─────────────────────────────────────────────────────────────
master   = pd.read_csv(os.path.join(PROC, "master_dataset.csv"))
seg      = pd.read_csv(os.path.join(PROC, "segment_summary.csv"))
cat      = pd.read_csv(os.path.join(PROC, "category_summary.csv"))
reg      = pd.read_csv(os.path.join(PROC, "region_summary.csv"))
sp       = pd.read_csv(os.path.join(PROC, "salesperson_summary.csv"))
ch_mix   = pd.read_csv(os.path.join(PROC, "channel_mix.csv"))

print("Generating charts...\n")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 1: KPI DASHBOARD OVERVIEW CARD
# ═══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(18, 4), facecolor=BG)
kpis = [
    ("$103.2M",  "Total Market\nOpportunity", YELLOW),
    ("$54.1M",   "Realized Sales\n(PTOS)",    CYAN),
    ("52.5%",    "POPS-C\nConversion Rate",   BLUE),
    ("$49.1M",   "Revenue Gap\n(Untapped)",   RED),
    ("5,927",    "Zero-Sales\nCustomers",     ORANGE),
    ("9",        "Regions\nAnalysed",         TEAL),
    ("7,859",    "Unique\nCustomers",         PURPLE),
]
for i, (val, label, color) in enumerate(kpis):
    ax = fig.add_axes([0.01 + i * 0.142, 0.05, 0.13, 0.88])
    ax.set_facecolor(CARD)
    for spine in ax.spines.values():
        spine.set_edgecolor(color); spine.set_linewidth(2.5)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.62, val, ha="center", va="center", fontsize=19, fontweight="bold",
            color=color, transform=ax.transAxes)
    ax.text(0.5, 0.26, label, ha="center", va="center", fontsize=9.5,
            color=MUTED, transform=ax.transAxes)
fig.suptitle("CAT PARTS & SERVICE — PTOS PERFORMANCE OVERVIEW",
             color=WHITE, fontsize=14, fontweight="bold", y=1.03)
save(fig, "01_kpi_overview.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 2: CUSTOMER SEGMENT — OPPORTUNITY vs SALES vs GAP
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)
seg_f = seg[seg["segment"].isin(["Do It Myself", "Do It For Me", "Work With Me"])]
seg_labels = ["Do It\nMyself", "Do It\nFor Me", "Work\nWith Me"]
x = np.arange(len(seg_f))
w = 0.28

ax = axes[0]
ax.bar(x - w, seg_f["opportunity"]/1e6, w, color=BLUE,   alpha=0.85, label="Opportunity")
ax.bar(x,     seg_f["sales"]/1e6,       w, color=YELLOW, alpha=0.85, label="Sales")
ax.bar(x + w, seg_f["gap"]/1e6,         w, color=RED,    alpha=0.75, label="Gap")
ax.set_xticks(x); ax.set_xticklabels(seg_labels)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax.set_title("Opportunity vs Sales vs Gap\nby Customer Segment", fontweight="bold", color=WHITE)
ax.legend(facecolor=CARD, labelcolor=WHITE, fontsize=9)
ax.grid(axis="y", alpha=0.3)

ax2 = axes[1]
colors_seg = [RED if p < 25 else ORANGE if p < 75 else GREEN for p in seg_f["popsc"]]
bars = ax2.barh(seg_f["segment"], seg_f["popsc"], color=colors_seg, height=0.5)
ax2.axvline(75, color=YELLOW, linestyle="--", linewidth=1.5, label="75% Target")
ax2.axvline(100, color=WHITE, linestyle=":", linewidth=1, alpha=0.4)
for bar, val in zip(bars, seg_f["popsc"]):
    ax2.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", color=WHITE, fontsize=10)
ax2.set_xlabel("POPS-C Conversion Rate (%)")
ax2.set_title("POPS-C Conversion Rate\nby Segment (vs 75% Target)", fontweight="bold", color=WHITE)
ax2.legend(facecolor=CARD, labelcolor=WHITE, fontsize=9)
ax2.grid(axis="x", alpha=0.3)
fig.suptitle("Customer Segment Analysis", color=WHITE, fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save(fig, "02_segment_analysis.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 3: PARTS CATEGORY POPS-C + GAP
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(15, 6), facecolor=BG)
cat_s = cat.sort_values("gap", ascending=True)
status_color = {"CRITICAL": RED, "FOCUS": ORANGE, "STRONG": GREEN}
bar_colors = [status_color[s] for s in cat_s["status"]]

ax1 = axes[0]
ax1.barh(cat_s["category"], cat_s["gap"]/1e6, color=bar_colors, height=0.6)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax1.set_title("Revenue Gap by Parts Category", fontweight="bold", color=WHITE)
ax1.set_xlabel("Revenue Gap ($)")
ax1.grid(axis="x", alpha=0.3)
legend_patches = [mpatches.Patch(color=RED, label="Critical (<40% POPS-C)"),
                  mpatches.Patch(color=ORANGE, label="Focus (40–60%)"),
                  mpatches.Patch(color=GREEN, label="Strong (>60%)")]
ax1.legend(handles=legend_patches, facecolor=CARD, labelcolor=WHITE, fontsize=8)

ax2 = axes[1]
cat_s2 = cat.sort_values("popsc")
bar_col2 = [status_color[s] for s in cat_s2["status"]]
bars = ax2.barh(cat_s2["category"], cat_s2["popsc"], color=bar_col2, height=0.6)
ax2.axvline(75, color=YELLOW, linestyle="--", linewidth=1.5, label="75% Target")
for bar, val in zip(bars, cat_s2["popsc"]):
    ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f"{val:.1f}%", va="center", color=WHITE, fontsize=9)
ax2.set_title("POPS-C Rate by Parts Category", fontweight="bold", color=WHITE)
ax2.set_xlabel("POPS-C (%)")
ax2.legend(facecolor=CARD, labelcolor=WHITE, fontsize=9)
ax2.grid(axis="x", alpha=0.3)
fig.suptitle("Parts Category Performance Analysis", color=WHITE, fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save(fig, "03_category_analysis.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 4: REGIONAL REVENUE GAP MAP
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(15, 6), facecolor=BG)
reg_s = reg.sort_values("gap", ascending=False)
priority_col = {"HIGH": RED, "MEDIUM": ORANGE, "MONITOR": TEAL}
rcols = [priority_col.get(p, TEAL) for p in reg_s["priority"]]

ax1 = axes[0]
bars = ax1.bar(reg_s["region"], reg_s["gap"]/1e6, color=rcols)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax1.set_title("Revenue Gap by Region", fontweight="bold", color=WHITE)
ax1.set_ylabel("Revenue Gap ($)")
ax1.tick_params(axis="x", rotation=35)
ax1.grid(axis="y", alpha=0.3)
legend_patches = [mpatches.Patch(color=RED, label="HIGH (>$10M)"),
                  mpatches.Patch(color=ORANGE, label="MEDIUM ($5–10M)"),
                  mpatches.Patch(color=TEAL, label="MONITOR (<$5M)")]
ax1.legend(handles=legend_patches, facecolor=CARD, labelcolor=WHITE, fontsize=8)

ax2 = axes[1]
sc = ax2.scatter(reg_s["opportunity"]/1e6, reg_s["popsc"],
                  s=reg_s["customers"]*3, c=reg_s["gap"]/1e6,
                  cmap="RdYlGn_r", alpha=0.85, edgecolors=WHITE, linewidths=0.7)
plt.colorbar(sc, ax=ax2, label="Revenue Gap ($M)")
ax2.axhline(75, color=YELLOW, linestyle="--", linewidth=1.5, label="75% POPS-C Target")
for _, row in reg_s.iterrows():
    ax2.annotate(row["region"], (row["opportunity"]/1e6, row["popsc"]),
                 textcoords="offset points", xytext=(6, 3), fontsize=8, color=WHITE)
ax2.set_xlabel("Total Opportunity ($M)"); ax2.set_ylabel("POPS-C (%)")
ax2.set_title("Opportunity vs Conversion\n(bubble = # customers)", fontweight="bold", color=WHITE)
ax2.legend(facecolor=CARD, labelcolor=WHITE, fontsize=9)
ax2.grid(alpha=0.3)
fig.suptitle("Regional Revenue Analysis", color=WHITE, fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save(fig, "04_regional_analysis.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 5: SALES CHANNEL MIX (STACKED BAR)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 5), facecolor=BG)
ch_s = ch_mix[ch_mix["total"] > 0].sort_values("total", ascending=False)
x = np.arange(len(ch_s))
ax.bar(x, ch_s["wo_sales"]/1e6,  color=CYAN,   label="Work Order (Labor + Service)", alpha=0.9)
ax.bar(x, ch_s["otc_sales"]/1e6, color=YELLOW, bottom=ch_s["wo_sales"]/1e6,
       label="Over the Counter (Parts)", alpha=0.9)
ax.set_xticks(x); ax.set_xticklabels(ch_s["region"], rotation=30)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax.set_title("Sales Channel Mix by Region — Work Order vs OTC",
             fontweight="bold", color=WHITE, fontsize=12)
ax.set_ylabel("Sales Volume ($)")
ax.legend(facecolor=CARD, labelcolor=WHITE, fontsize=9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
save(fig, "05_channel_mix.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 6: TOP 15 SALESPEOPLE BY REVENUE GAP
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=BG)
sp15 = sp.head(15).sort_values("gap")
action_col = {
    "Urgent Coaching": RED,
    "Support Needed":  ORANGE,
    "Account Planning": BLUE,
    "Sustain":         GREEN,
}
sp_colors = [action_col.get(a, MUTED) for a in sp15["action"]]

ax1 = axes[0]
ax1.barh(sp15["salesperson_name"], sp15["gap"]/1e6, color=sp_colors, height=0.65)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax1.set_title("Top 15 Revenue Gaps\nby Salesperson", fontweight="bold", color=WHITE)
ax1.set_xlabel("Revenue Gap ($)")
ax1.grid(axis="x", alpha=0.3)
legend_patches = [mpatches.Patch(color=v, label=k) for k, v in action_col.items()]
ax1.legend(handles=legend_patches, facecolor=CARD, labelcolor=WHITE, fontsize=8)

ax2 = axes[1]
ax2.scatter(sp15["opportunity"]/1e6, sp15["popsc"],
             s=sp15["customers"]*5, c=sp_colors, alpha=0.85, edgecolors=WHITE, linewidths=0.6)
ax2.axhline(75, color=YELLOW, linestyle="--", linewidth=1.5, label="75% Target")
for _, row in sp15.iterrows():
    ax2.annotate(row["salesperson_name"].split()[0],
                 (row["opportunity"]/1e6, row["popsc"]),
                 textcoords="offset points", xytext=(4, 3), fontsize=7, color=MUTED)
ax2.set_xlabel("Opportunity ($M)"); ax2.set_ylabel("POPS-C (%)")
ax2.set_title("Opportunity vs POPS-C\nby Salesperson", fontweight="bold", color=WHITE)
ax2.legend(facecolor=CARD, labelcolor=WHITE, fontsize=9)
ax2.grid(alpha=0.3)
fig.suptitle("Salesperson Performance Scorecard", color=WHITE, fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
save(fig, "06_salesperson_scorecard.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 7: ZERO-SALES CUSTOMER DEEP DIVE
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG)
zero = master[master["total_sales"] == 0]
active = master[master["total_sales"] > 0]

# By segment
zero_seg = zero.groupby("segment").agg(
    count=("customer_id", "nunique"), opportunity=("total_opp", "sum")).reset_index()
zero_seg = zero_seg[zero_seg["segment"] != "Unassigned"]

ax1 = axes[0]
ax1.bar(zero_seg["segment"], zero_seg["opportunity"]/1e6, color=RED, alpha=0.85)
ax1.bar(zero_seg["segment"], zero_seg["opportunity"]/1e6, color="none",
        edgecolor=ORANGE, linewidth=2)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax1.set_title("Zero-Sales Customer Opportunity\nby Segment", fontweight="bold", color=WHITE)
ax1.set_ylabel("Untapped Opportunity ($)")
ax1.grid(axis="y", alpha=0.3)
for i, (_, row) in enumerate(zero_seg.iterrows()):
    ax1.text(i, row["opportunity"]/1e6 + 0.3, f"n={row['count']:,}",
             ha="center", fontsize=9, color=MUTED)

# By region (top 6)
zero_reg = zero.groupby("region")["total_opp"].sum().sort_values(ascending=False).head(6)
ax2 = axes[1]
ax2.barh(zero_reg.index, zero_reg.values/1e6, color=ORANGE, height=0.6)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax2.set_title("Zero-Sales Opportunity\nby Region (Top 6)", fontweight="bold", color=WHITE)
ax2.set_xlabel("Untapped Opportunity ($)")
ax2.grid(axis="x", alpha=0.3)
fig.suptitle("Zero-Sales Customer Analysis — Priority Re-engagement Targets",
             color=WHITE, fontsize=12, fontweight="bold", y=1.01)
plt.tight_layout()
save(fig, "07_zero_sales_analysis.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 8: COMPREHENSIVE DASHBOARD OVERVIEW (POSTER)
# ═══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 12), facecolor=BG)
fig.text(0.5, 0.97, "CAT PARTS & SERVICE — GROWTH STRATEGY DASHBOARD",
         ha="center", color=WHITE, fontsize=17, fontweight="bold")
fig.text(0.5, 0.945, "10,165 PTOS Records  ·  7,859 Customers  ·  9 Regions  ·  POPS-C Analytics",
         ha="center", color=MUTED, fontsize=10)

# KPI strip
kpi_strip = [("$103.2M", "Market Opp.", YELLOW), ("$54.1M", "Realized Sales", CYAN),
             ("52.5%", "POPS-C", BLUE), ("$49.1M", "Rev. Gap", RED), ("5,927", "Zero-Sales", ORANGE)]
for i, (v, l, c) in enumerate(kpi_strip):
    ax = fig.add_axes([0.01 + i*0.198, 0.875, 0.188, 0.055])
    ax.set_facecolor(CARD)
    for s in ax.spines.values(): s.set_edgecolor(c); s.set_linewidth(2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.65, v,  ha="center", va="center", fontsize=16, fontweight="bold", color=c, transform=ax.transAxes)
    ax.text(0.5, 0.2,  l,  ha="center", va="center", fontsize=8.5, color=MUTED, transform=ax.transAxes)

# Panel A: Segment bars
ax_a = fig.add_axes([0.01, 0.48, 0.29, 0.36])
ax_a.set_facecolor(CARD)
x = np.arange(3); w = 0.28
ax_a.bar(x - w, seg_f["opportunity"]/1e6, w, color=BLUE,   alpha=0.85, label="Opportunity")
ax_a.bar(x,     seg_f["sales"]/1e6,       w, color=YELLOW, alpha=0.85, label="Sales")
ax_a.bar(x + w, seg_f["gap"]/1e6,         w, color=RED,    alpha=0.75, label="Gap")
ax_a.set_xticks(x); ax_a.set_xticklabels(["DIM", "DIFM", "WWM"], color=MUTED)
ax_a.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax_a.set_title("Customer Segment", color=WHITE, fontsize=10, fontweight="bold")
ax_a.legend(facecolor=CARD, labelcolor=WHITE, fontsize=7)
ax_a.grid(axis="y", alpha=0.3)

# Panel B: Category POPS-C
ax_b = fig.add_axes([0.34, 0.48, 0.30, 0.36])
ax_b.set_facecolor(CARD)
cat_s3 = cat.sort_values("popsc")
bcols3 = [status_color[s] for s in cat_s3["status"]]
ax_b.barh(cat_s3["category"], cat_s3["popsc"], color=bcols3, height=0.65)
ax_b.axvline(75, color=YELLOW, linestyle="--", linewidth=1.2)
ax_b.set_title("Parts Category POPS-C (%)", color=WHITE, fontsize=10, fontweight="bold")
ax_b.set_xlabel("POPS-C %", color=MUTED)
ax_b.grid(axis="x", alpha=0.3)

# Panel C: Regional gap
ax_c = fig.add_axes([0.68, 0.48, 0.30, 0.36])
ax_c.set_facecolor(CARD)
reg_s2 = reg.sort_values("gap", ascending=False)
rcols2 = [priority_col.get(p, TEAL) for p in reg_s2["priority"]]
ax_c.bar(reg_s2["region"], reg_s2["gap"]/1e6, color=rcols2)
ax_c.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax_c.set_title("Revenue Gap by Region", color=WHITE, fontsize=10, fontweight="bold")
ax_c.tick_params(axis="x", rotation=35, labelsize=7)
ax_c.grid(axis="y", alpha=0.3)

# Panel D: Channel mix
ax_d = fig.add_axes([0.01, 0.06, 0.44, 0.36])
ax_d.set_facecolor(CARD)
ch_s2 = ch_mix[ch_mix["total"] > 0].sort_values("total", ascending=False)
xc = np.arange(len(ch_s2))
ax_d.bar(xc, ch_s2["wo_sales"]/1e6,  color=CYAN,   alpha=0.9, label="Work Order")
ax_d.bar(xc, ch_s2["otc_sales"]/1e6, color=YELLOW, alpha=0.9,
          bottom=ch_s2["wo_sales"]/1e6, label="OTC")
ax_d.set_xticks(xc); ax_d.set_xticklabels(ch_s2["region"], rotation=30, fontsize=8)
ax_d.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax_d.set_title("Sales Channel Mix (WO vs OTC)", color=WHITE, fontsize=10, fontweight="bold")
ax_d.legend(facecolor=CARD, labelcolor=WHITE, fontsize=8)
ax_d.grid(axis="y", alpha=0.3)

# Panel E: Top salesperson gaps
ax_e = fig.add_axes([0.50, 0.06, 0.48, 0.36])
ax_e.set_facecolor(CARD)
sp10 = sp.head(10).sort_values("gap")
spe_colors = [action_col.get(a, MUTED) for a in sp10["action"]]
ax_e.barh(sp10["salesperson_name"], sp10["gap"]/1e6, color=spe_colors, height=0.65)
ax_e.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_m))
ax_e.set_title("Top 10 Salesperson Revenue Gaps", color=WHITE, fontsize=10, fontweight="bold")
ax_e.grid(axis="x", alpha=0.3)
legend_e = [mpatches.Patch(color=v, label=k) for k, v in action_col.items()]
ax_e.legend(handles=legend_e, facecolor=CARD, labelcolor=WHITE, fontsize=7, loc="lower right")

save(fig, "08_dashboard_overview.png")

print(f"\nAll 8 charts saved to /images/")
