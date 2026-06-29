/*
  AfriMoney Intelligence Platform
  Gold Layer — Supplementary Views
  Run after dbt mart tables are created.
  These are Snowflake-native views that wrap the dbt marts for
  specific BI tool connection patterns (DirectQuery, Streamlit).
*/

USE ROLE AFRIMONEY_ADMIN;
USE DATABASE AFRIMONEY_DB;
USE SCHEMA GOLD;
USE WAREHOUSE AFRIMONEY_ANALYTICS_WH;

-- ══════════════════════════════════════════════════════
-- 1. EXECUTIVE SUMMARY — single-row rolling KPIs
-- ══════════════════════════════════════════════════════
CREATE OR REPLACE VIEW VW_EXECUTIVE_SUMMARY AS
WITH latest_month AS (
    SELECT MAX(created_month) AS latest_month FROM MART_REMITTANCE
),
curr AS (
    SELECT
        SUM(initiated_count)       AS total_transfers_initiated,
        SUM(completed_count)       AS total_transfers_completed,
        SUM(total_volume_zar)      AS total_volume_zar,
        SUM(total_net_revenue_zar) AS total_net_revenue_zar,
        SUM(unique_senders)        AS unique_senders,
        AVG(success_rate_pct)      AS avg_success_rate,
        AVG(avg_fx_spread_pct)     AS avg_fx_spread_pct,
        SUM(fraud_flagged_count)   AS fraud_flagged
    FROM MART_REMITTANCE
    WHERE created_month = (SELECT latest_month FROM latest_month)
),
prev AS (
    SELECT
        SUM(total_net_revenue_zar) AS prev_revenue_zar,
        SUM(completed_count)       AS prev_transfers
    FROM MART_REMITTANCE
    WHERE created_month = TO_VARCHAR(DATEADD('month', -1,
        TO_DATE((SELECT latest_month FROM latest_month) || '-01')), 'YYYY-MM')
)
SELECT
    c.*,
    p.prev_revenue_zar,
    p.prev_transfers,
    DIV0(c.total_net_revenue_zar - p.prev_revenue_zar, p.prev_revenue_zar) * 100 AS revenue_mom_pct,
    DIV0(c.total_transfers_completed - p.prev_transfers, p.prev_transfers) * 100  AS transfers_mom_pct,
    (SELECT latest_month FROM latest_month) AS as_of_month,
    CURRENT_TIMESTAMP() AS refreshed_at
FROM curr c, prev p;

-- ══════════════════════════════════════════════════════
-- 2. TOP CORRIDORS — by revenue, last 6 months
-- ══════════════════════════════════════════════════════
CREATE OR REPLACE VIEW VW_TOP_CORRIDORS_6M AS
SELECT
    business_key,
    corridor_code,
    SUM(initiated_count)       AS total_initiated,
    SUM(completed_count)       AS total_completed,
    SUM(total_volume_zar)      AS total_volume_zar,
    SUM(total_net_revenue_zar) AS total_net_revenue_zar,
    AVG(success_rate_pct)      AS avg_success_rate,
    AVG(avg_fx_spread_pct)     AS avg_fx_spread,
    RANK() OVER (PARTITION BY business_key ORDER BY SUM(total_net_revenue_zar) DESC) AS revenue_rank
FROM MART_REMITTANCE
WHERE created_month >= TO_VARCHAR(DATEADD('month', -6, CURRENT_DATE()), 'YYYY-MM')
GROUP BY 1, 2
ORDER BY total_net_revenue_zar DESC;

-- ══════════════════════════════════════════════════════
-- 3. CUSTOMER SEGMENTS — LTV distribution
-- ══════════════════════════════════════════════════════
CREATE OR REPLACE VIEW VW_CUSTOMER_SEGMENTS AS
SELECT
    business_key,
    ltv_band,
    customer_segment,
    kyc_level,
    COUNT(*)                    AS customer_count,
    AVG(ltv_score)              AS avg_ltv_score,
    AVG(engagement_score)       AS avg_engagement_score,
    AVG(lifetime_revenue_zar)   AS avg_lifetime_revenue_zar,
    AVG(total_transfers)        AS avg_total_transfers,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 AS churn_rate_pct
FROM MART_CUSTOMER_360
GROUP BY 1, 2, 3, 4
ORDER BY avg_ltv_score DESC;

-- ══════════════════════════════════════════════════════
-- 4. RISK DASHBOARD — latest month RAG status
-- ══════════════════════════════════════════════════════
CREATE OR REPLACE VIEW VW_RISK_DASHBOARD AS
SELECT
    business_key,
    risk_month,
    fraud_rate_bps,
    fraud_rag_status,
    kyc_completion_rate,
    kyc_rag_status,
    success_rate_pct,
    suspended_customers,
    high_risk_customers,
    CASE
        WHEN success_rate_pct >= 80 THEN 'green'
        WHEN success_rate_pct >= 70 THEN 'amber'
        ELSE 'red'
    END AS ops_rag_status
FROM MART_RISK_COMPLIANCE
WHERE risk_month = (SELECT MAX(risk_month) FROM MART_RISK_COMPLIANCE);

-- ══════════════════════════════════════════════════════
-- 5. MONTHLY TREND — all KPIs time series for Power BI
-- ══════════════════════════════════════════════════════
CREATE OR REPLACE VIEW VW_MONTHLY_TREND AS
SELECT
    business_key,
    created_month,
    SUM(initiated_count)       AS transfers_initiated,
    SUM(completed_count)       AS transfers_completed,
    SUM(total_volume_zar)      AS volume_zar,
    SUM(total_net_revenue_zar) AS net_revenue_zar,
    AVG(success_rate_pct)      AS success_rate_pct,
    SUM(unique_senders)        AS monthly_active_senders,
    AVG(avg_fx_spread_pct)     AS avg_fx_spread_pct,
    SUM(fraud_flagged_count)   AS fraud_flags,
    SUM(first_transfers)       AS new_senders
FROM MART_REMITTANCE
GROUP BY 1, 2
ORDER BY business_key, created_month;

-- Grant views to analyst role
GRANT SELECT ON ALL VIEWS IN SCHEMA GOLD TO ROLE AFRIMONEY_ANALYST;
