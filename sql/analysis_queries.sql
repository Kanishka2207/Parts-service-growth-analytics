-- =============================================================================
-- analysis_queries.sql
-- CAT Parts & Service Growth Analytics
-- =============================================================================
-- Equivalent SQL logic for all analytical calculations performed in Python/Excel.
-- Assumes master_dataset is loaded into a table named: ptos_master
-- Compatible with: PostgreSQL, BigQuery, Snowflake (minor syntax adjustments)
-- =============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 1: GRAND TOTAL KPIs
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    SUM(total_opp)                                          AS total_market_opportunity,
    SUM(total_sales)                                        AS total_realized_sales,
    SUM(total_opp) - SUM(total_sales)                       AS revenue_gap,
    ROUND(SUM(total_sales) / NULLIF(SUM(total_opp),0) * 100, 2)
                                                            AS popsc_pct,
    COUNT(DISTINCT customer_id)                             AS unique_customers,
    COUNT(DISTINCT CASE WHEN total_sales = 0 THEN customer_id END)
                                                            AS zero_sales_customers,
    SUM(CASE WHEN total_sales = 0 THEN total_opp ELSE 0 END)
                                                            AS zero_sales_opportunity,
    (SUM(total_opp) * 0.75) - SUM(total_sales)             AS gap_to_75pct_target
FROM ptos_master;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 2: POPS-C BY CUSTOMER SEGMENT
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    segment,
    COUNT(DISTINCT customer_id)                             AS customers,
    SUM(total_opp)                                          AS opportunity,
    SUM(total_sales)                                        AS sales,
    SUM(total_opp) - SUM(total_sales)                       AS revenue_gap,
    ROUND(SUM(total_sales) / NULLIF(SUM(total_opp),0) * 100, 1)
                                                            AS popsc_pct,
    SUM(equipment_units)                                    AS fleet_units
FROM ptos_master
WHERE segment IN ('Do It Myself', 'Do It For Me', 'Work With Me')
GROUP BY segment
ORDER BY revenue_gap DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 3: POPS-C BY PARTS CATEGORY (UNPIVOTED)
-- ─────────────────────────────────────────────────────────────────────────────

WITH categories AS (
    SELECT 'Labor'             AS category, SUM(labor_opp)  AS opp, SUM(labor_sales)  AS sales FROM ptos_master
    UNION ALL
    SELECT 'Engine',                         SUM(eng_opp),            SUM(eng_sales)            FROM ptos_master
    UNION ALL
    SELECT 'Drive Train',                    SUM(dt_opp),             SUM(dt_sales)             FROM ptos_master
    UNION ALL
    SELECT 'Hydraulics',                     SUM(hyd_opp),            SUM(hyd_sales)            FROM ptos_master
    UNION ALL
    SELECT 'Filters & Fluids',               SUM(ff_opp),             SUM(ff_sales)             FROM ptos_master
    UNION ALL
    SELECT 'Undercarriage',                  SUM(uc_opp),             SUM(uc_sales)             FROM ptos_master
    UNION ALL
    SELECT 'Maintenance Parts',              SUM(maint_opp),          SUM(maint_sales)          FROM ptos_master
    UNION ALL
    SELECT 'GET',                            SUM(get_opp),            SUM(get_sales)            FROM ptos_master
)
SELECT
    category,
    opp                                                         AS opportunity,
    sales,
    opp - sales                                                 AS revenue_gap,
    ROUND(sales / NULLIF(opp, 0) * 100, 1)                     AS popsc_pct,
    CASE
        WHEN ROUND(sales / NULLIF(opp,0) * 100, 1) < 40 THEN 'CRITICAL'
        WHEN ROUND(sales / NULLIF(opp,0) * 100, 1) < 60 THEN 'FOCUS'
        ELSE 'STRONG'
    END                                                         AS status
FROM categories
ORDER BY revenue_gap DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 4: REVENUE GAP BY REGION
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    region,
    COUNT(DISTINCT customer_id)                             AS customers,
    SUM(total_opp)                                          AS opportunity,
    SUM(total_sales)                                        AS sales,
    SUM(total_opp) - SUM(total_sales)                       AS revenue_gap,
    ROUND(SUM(total_sales) / NULLIF(SUM(total_opp),0) * 100, 1)
                                                            AS popsc_pct,
    ROUND(
        (SUM(total_opp) - SUM(total_sales)) /
        SUM(SUM(total_opp) - SUM(total_sales)) OVER () * 100
    , 1)                                                    AS gap_share_pct,
    CASE
        WHEN SUM(total_opp) - SUM(total_sales) > 10000000 THEN 'HIGH'
        WHEN SUM(total_opp) - SUM(total_sales) > 5000000  THEN 'MEDIUM'
        ELSE 'MONITOR'
    END                                                     AS priority
FROM ptos_master
WHERE region != 'OTHER'
GROUP BY region
ORDER BY revenue_gap DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 5: TOP 20 SALESPEOPLE BY REVENUE GAP
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    salesperson_name,
    COUNT(DISTINCT customer_id)                             AS customers,
    SUM(total_opp)                                          AS opportunity,
    SUM(total_sales)                                        AS sales,
    SUM(total_opp) - SUM(total_sales)                       AS revenue_gap,
    ROUND(SUM(total_sales) / NULLIF(SUM(total_opp),0) * 100, 1)
                                                            AS popsc_pct,
    CASE
        WHEN ROUND(SUM(total_sales)/NULLIF(SUM(total_opp),0)*100,1) < 25 THEN 'Urgent Coaching'
        WHEN ROUND(SUM(total_sales)/NULLIF(SUM(total_opp),0)*100,1) < 50 THEN 'Support Needed'
        WHEN ROUND(SUM(total_sales)/NULLIF(SUM(total_opp),0)*100,1) < 75 THEN 'Account Planning'
        ELSE 'Sustain'
    END                                                     AS action_required
FROM ptos_master
GROUP BY salesperson_name
ORDER BY revenue_gap DESC
LIMIT 20;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 6: SALES CHANNEL MIX BY REGION
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    region,
    SUM(work_order_sales)                                   AS work_order_sales,
    SUM(otc_sales)                                          AS otc_sales,
    SUM(work_order_sales) + SUM(otc_sales)                  AS total_channel_sales,
    ROUND(SUM(work_order_sales) /
          NULLIF(SUM(work_order_sales) + SUM(otc_sales), 0) * 100, 1)
                                                            AS wo_share_pct,
    ROUND(SUM(otc_sales) /
          NULLIF(SUM(work_order_sales) + SUM(otc_sales), 0) * 100, 1)
                                                            AS otc_share_pct
FROM ptos_master
WHERE region != 'OTHER'
  AND (work_order_sales + otc_sales) > 0
GROUP BY region
ORDER BY total_channel_sales DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 7: ZERO-SALES ACCOUNT PRIORITY LIST
-- (Use for targeted re-engagement outreach)
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    customer_id,
    salesperson_name,
    segment,
    region,
    total_opp                                               AS untapped_opportunity,
    equipment_units,
    ROUND(total_opp / NULLIF(equipment_units, 0), 0)        AS opp_per_unit,
    RANK() OVER (ORDER BY total_opp DESC)                   AS priority_rank
FROM ptos_master
WHERE total_sales = 0
  AND total_opp > 0
  AND segment IN ('Do It Myself', 'Work With Me')
ORDER BY total_opp DESC
LIMIT 100;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 8: POPS-C BAND DISTRIBUTION
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    popsc_band,
    COUNT(DISTINCT customer_id)                             AS customers,
    SUM(total_opp)                                          AS opportunity,
    SUM(total_sales)                                        AS sales,
    SUM(total_opp) - SUM(total_sales)                       AS revenue_gap
FROM ptos_master
GROUP BY popsc_band
ORDER BY
    CASE popsc_band
        WHEN 'No Sales'        THEN 1
        WHEN 'Critical (<25%)' THEN 2
        WHEN 'Low (25–50%)'    THEN 3
        WHEN 'Moderate (50–75%)' THEN 4
        WHEN 'Strong (≥75%)'   THEN 5
        ELSE 6
    END;


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 9: FLEET SIZE vs POPS-C CORRELATION (BUCKETED)
-- Identifies whether larger fleets convert better
-- ─────────────────────────────────────────────────────────────────────────────

SELECT
    CASE
        WHEN equipment_units = 0  THEN '0 units'
        WHEN equipment_units <= 2 THEN '1–2 units'
        WHEN equipment_units <= 5 THEN '3–5 units'
        WHEN equipment_units <= 10 THEN '6–10 units'
        ELSE '11+ units'
    END                                                     AS fleet_bucket,
    COUNT(DISTINCT customer_id)                             AS customers,
    ROUND(AVG(popsc), 1)                                    AS avg_popsc,
    SUM(total_opp)                                          AS total_opportunity,
    SUM(total_sales)                                        AS total_sales
FROM ptos_master
GROUP BY 1
ORDER BY MIN(equipment_units);


-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 10: REVENUE IMPACT SCENARIO MODELLING
-- Estimate incremental revenue at various POPS-C target improvements
-- ─────────────────────────────────────────────────────────────────────────────

WITH base AS (
    SELECT
        SUM(total_opp)   AS total_opp,
        SUM(total_sales) AS total_sales
    FROM ptos_master
)
SELECT
    target_popsc_pct,
    ROUND(total_opp * (target_popsc_pct / 100.0), 0)       AS revenue_at_target,
    ROUND(total_opp * (target_popsc_pct / 100.0)
          - total_sales, 0)                                 AS incremental_revenue
FROM base
CROSS JOIN (VALUES (55),(60),(65),(70),(75),(80)) AS targets(target_popsc_pct)
ORDER BY target_popsc_pct;
