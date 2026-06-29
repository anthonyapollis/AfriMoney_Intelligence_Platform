-- ============================================================
-- AfriMoney Intelligence Platform
-- Snowflake Account Setup — Warehouses, Databases, Roles
-- Step 1 of 6: Run as ACCOUNTADMIN
-- ============================================================

USE ROLE ACCOUNTADMIN;

-- ── Virtual Warehouses ────────────────────────────────────────
-- Ingestion warehouse (ETL loads)
CREATE WAREHOUSE IF NOT EXISTS AFRIMONEY_INGEST_WH
    WAREHOUSE_SIZE    = 'MEDIUM'
    AUTO_SUSPEND      = 120
    AUTO_RESUME       = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'AfriMoney: Bronze layer ingestion and COPY INTO operations';

-- Transformation warehouse (dbt runs)
CREATE WAREHOUSE IF NOT EXISTS AFRIMONEY_TRANSFORM_WH
    WAREHOUSE_SIZE    = 'LARGE'
    AUTO_SUSPEND      = 60
    AUTO_RESUME       = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'AfriMoney: dbt Silver and Gold transformations';

-- Analytics warehouse (Power BI / ad-hoc queries)
CREATE WAREHOUSE IF NOT EXISTS AFRIMONEY_ANALYTICS_WH
    WAREHOUSE_SIZE    = 'SMALL'
    AUTO_SUSPEND      = 300
    AUTO_RESUME       = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'AfriMoney: Power BI semantic model and ad-hoc analytics';

-- ML warehouse (Snowpark training jobs)
CREATE WAREHOUSE IF NOT EXISTS AFRIMONEY_ML_WH
    WAREHOUSE_SIZE    = 'X-LARGE'
    AUTO_SUSPEND      = 60
    AUTO_RESUME       = TRUE
    INITIALLY_SUSPENDED = TRUE
    MAX_CLUSTER_COUNT = 4
    MIN_CLUSTER_COUNT = 1
    SCALING_POLICY    = 'ECONOMY'
    COMMENT = 'AfriMoney: Snowpark ML training — multi-cluster for parallel model runs';

-- ── Databases ─────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS AFRIMONEY_DB
    COMMENT = 'AfriMoney Intelligence Platform — all layers (Bronze/Silver/Gold)';

CREATE DATABASE IF NOT EXISTS AFRIMONEY_ML_DB
    COMMENT = 'AfriMoney: Snowpark ML models, feature store, experiment tracking';

-- ── Schemas ───────────────────────────────────────────────────
USE DATABASE AFRIMONEY_DB;

CREATE SCHEMA IF NOT EXISTS BRONZE   COMMENT = 'Raw, immutable source-aligned data';
CREATE SCHEMA IF NOT EXISTS SILVER   COMMENT = 'Cleansed, canonical, SCD2, tokenised';
CREATE SCHEMA IF NOT EXISTS GOLD     COMMENT = 'Analytical marts — Power BI ready';
CREATE SCHEMA IF NOT EXISTS STAGING  COMMENT = 'Transient landing area for COPY INTO';
CREATE SCHEMA IF NOT EXISTS UTILS    COMMENT = 'Shared UDFs, macros, stored procedures';

USE DATABASE AFRIMONEY_ML_DB;
CREATE SCHEMA IF NOT EXISTS FEATURE_STORE   COMMENT = 'ML feature tables';
CREATE SCHEMA IF NOT EXISTS EXPERIMENTS     COMMENT = 'Model training runs and metrics';
CREATE SCHEMA IF NOT EXISTS MODEL_REGISTRY  COMMENT = 'Registered model versions';
CREATE SCHEMA IF NOT EXISTS PREDICTIONS     COMMENT = 'Model scoring output tables';

-- ── Roles & RBAC ──────────────────────────────────────────────
USE DATABASE AFRIMONEY_DB;

CREATE ROLE IF NOT EXISTS AFRIMONEY_ADMIN   COMMENT = 'Full platform admin';
CREATE ROLE IF NOT EXISTS AFRIMONEY_ENG     COMMENT = 'Data engineering — Bronze/Silver write';
CREATE ROLE IF NOT EXISTS AFRIMONEY_ANALYST COMMENT = 'Read Gold marts + ML predictions';
CREATE ROLE IF NOT EXISTS AFRIMONEY_ML_ENG  COMMENT = 'ML engineers — feature store + Snowpark';
CREATE ROLE IF NOT EXISTS AFRIMONEY_VIEWER  COMMENT = 'Read-only Power BI service account';

-- Role hierarchy
GRANT ROLE AFRIMONEY_ENG     TO ROLE AFRIMONEY_ADMIN;
GRANT ROLE AFRIMONEY_ANALYST TO ROLE AFRIMONEY_ADMIN;
GRANT ROLE AFRIMONEY_ML_ENG  TO ROLE AFRIMONEY_ADMIN;
GRANT ROLE AFRIMONEY_VIEWER  TO ROLE AFRIMONEY_ANALYST;
GRANT ROLE AFRIMONEY_ADMIN   TO ROLE SYSADMIN;

-- Warehouse grants
GRANT USAGE ON WAREHOUSE AFRIMONEY_INGEST_WH    TO ROLE AFRIMONEY_ENG;
GRANT USAGE ON WAREHOUSE AFRIMONEY_TRANSFORM_WH TO ROLE AFRIMONEY_ENG;
GRANT USAGE ON WAREHOUSE AFRIMONEY_ANALYTICS_WH TO ROLE AFRIMONEY_ANALYST;
GRANT USAGE ON WAREHOUSE AFRIMONEY_ANALYTICS_WH TO ROLE AFRIMONEY_VIEWER;
GRANT USAGE ON WAREHOUSE AFRIMONEY_ML_WH        TO ROLE AFRIMONEY_ML_ENG;

-- Database grants
GRANT USAGE ON DATABASE AFRIMONEY_DB    TO ROLE AFRIMONEY_ENG;
GRANT USAGE ON DATABASE AFRIMONEY_DB    TO ROLE AFRIMONEY_ANALYST;
GRANT USAGE ON DATABASE AFRIMONEY_ML_DB TO ROLE AFRIMONEY_ML_ENG;

-- Schema grants — engineering gets WRITE on Bronze/Silver, READ on Gold
GRANT ALL PRIVILEGES ON SCHEMA AFRIMONEY_DB.BRONZE  TO ROLE AFRIMONEY_ENG;
GRANT ALL PRIVILEGES ON SCHEMA AFRIMONEY_DB.SILVER  TO ROLE AFRIMONEY_ENG;
GRANT ALL PRIVILEGES ON SCHEMA AFRIMONEY_DB.GOLD    TO ROLE AFRIMONEY_ENG;
GRANT USAGE ON SCHEMA AFRIMONEY_DB.GOLD             TO ROLE AFRIMONEY_ANALYST;
GRANT USAGE ON SCHEMA AFRIMONEY_DB.GOLD             TO ROLE AFRIMONEY_VIEWER;
GRANT SELECT ON ALL TABLES IN SCHEMA AFRIMONEY_DB.GOLD TO ROLE AFRIMONEY_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA AFRIMONEY_DB.GOLD TO ROLE AFRIMONEY_VIEWER;

-- ── Internal Stage (for CSV uploads) ─────────────────────────
USE SCHEMA AFRIMONEY_DB.STAGING;

CREATE STAGE IF NOT EXISTS AFRIMONEY_STAGE
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
        NULL_IF = ('NULL','null','','N/A')
        EMPTY_FIELD_AS_NULL = TRUE
        DATE_FORMAT = 'AUTO'
        TIMESTAMP_FORMAT = 'AUTO'
    )
    COMMENT = 'AfriMoney: internal stage for CSV data loads';

-- ── Network Policy (best practice) ───────────────────────────
-- CREATE NETWORK POLICY AFRIMONEY_OFFICE_POLICY
--     ALLOWED_IP_LIST = ('197.x.x.x/24')  -- replace with office CIDR
--     COMMENT = 'Restrict Snowflake access to office IPs';

SELECT 'AfriMoney Snowflake account setup complete.' AS STATUS;
