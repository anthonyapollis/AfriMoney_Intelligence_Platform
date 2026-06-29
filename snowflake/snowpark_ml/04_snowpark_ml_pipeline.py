"""
AfriMoney Intelligence Platform
Snowpark ML Pipeline — runs entirely inside Snowflake
No data leaves Snowflake: features, training, scoring, and registry all on-platform.

Prerequisites:
    pip install snowflake-snowpark-python snowflake-ml-python

Run:
    python 04_snowpark_ml_pipeline.py
"""

from snowflake.snowpark import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import *
import snowflake.ml.modeling.preprocessing as snowml_prep
import snowflake.ml.modeling.ensemble as snowml_ensemble
import snowflake.ml.modeling.linear_model as snowml_linear
from snowflake.ml.registry import Registry
import os, json
from datetime import datetime

# ── Snowflake connection ──────────────────────────────────────
connection_params = {
    "account":   os.environ["SNOWFLAKE_ACCOUNT"],
    "user":      os.environ["SNOWFLAKE_USER"],
    "password":  os.environ["SNOWFLAKE_PASSWORD"],
    "role":      "AFRIMONEY_ML_ENG",
    "warehouse": "AFRIMONEY_ML_WH",
    "database":  "AFRIMONEY_ML_DB",
    "schema":    "FEATURE_STORE",
}

session = Session.builder.configs(connection_params).create()
print(f"Connected: {session.get_current_account()} | {session.get_current_warehouse()}")

# ── Feature engineering (all executed as Snowflake SQL pushdown) ──

def build_fraud_features(session: Session):
    """Build fraud detection feature table from Gold mart + Bronze facts."""
    print("\n[FEATURE STORE] Building fraud features...")

    # Pull from Snowflake Gold mart (all computation happens in Snowflake)
    df = session.table("AFRIMONEY_DB.BRONZE.FACT_REMITTANCE_TRANSFER")

    features = df.select(
        F.col("TRANSFER_ID"),
        F.col("BUSINESS_KEY"),
        F.col("IS_SUSPECTED_FRAUD").cast(IntegerType()).alias("LABEL_FRAUD"),
        F.log(F.greatest(F.col("SEND_AMOUNT_ZAR"), F.lit(1))).alias("SEND_AMOUNT_LOG"),
        F.col("SEND_AMOUNT_ZAR"),
        F.col("TRANSFER_FEE_ZAR"),
        (F.col("TRANSFER_FEE_ZAR") / F.greatest(F.col("SEND_AMOUNT_ZAR"), F.lit(1))).alias("FEE_PCT"),
        F.col("FX_MARGIN_ZAR"),
        F.col("FX_SPREAD_PCT"),
        F.col("PAYMENT_ATTEMPTS"),
        F.col("PAYOUT_ATTEMPTS"),
        F.hour(F.col("CREATED_DATETIME")).alias("HOUR_OF_DAY"),
        F.dayofweek(F.col("CREATED_DATETIME")).alias("DAY_OF_WEEK"),
        # Encode categoricals via hash (Snowpark-native)
        F.hash(F.col("BUSINESS_KEY")).alias("BUSINESS_KEY_HASH"),
        F.hash(F.col("CORRIDOR_CODE")).alias("CORRIDOR_HASH"),
        F.hash(F.col("CHANNEL")).alias("CHANNEL_HASH"),
        F.hash(F.col("PAYMENT_METHOD")).alias("PAY_METHOD_HASH"),
        F.hash(F.col("PAYOUT_METHOD")).alias("PAYOUT_METHOD_HASH"),
    ).filter(F.col("SEND_AMOUNT_ZAR") > 0)

    # Save to Feature Store (materialise as Snowflake table)
    features.write.mode("overwrite").save_as_table(
        "AFRIMONEY_ML_DB.FEATURE_STORE.FRAUD_FEATURES"
    )
    print(f"  Fraud features: {features.count():,} rows saved")
    return "AFRIMONEY_ML_DB.FEATURE_STORE.FRAUD_FEATURES"


def build_churn_features(session: Session):
    """Customer-level churn features from Gold mart."""
    print("\n[FEATURE STORE] Building churn features...")

    df = session.table("AFRIMONEY_DB.GOLD.MART_CUSTOMER_360")

    features = df.select(
        F.col("CUSTOMER_ID"),
        F.col("BUSINESS_KEY"),
        F.col("IS_CHURNED").cast(IntegerType()).alias("LABEL_CHURN"),
        F.col("TOTAL_TRANSFERS"),
        F.col("COMPLETED_TRANSFERS"),
        F.col("TOTAL_SEND_ZAR"),
        F.col("AVG_SEND_ZAR"),
        F.coalesce(F.col("TOTAL_REVENUE_GENERATED_ZAR"), F.lit(0)).alias("LIFETIME_REVENUE_ZAR"),
        F.col("DAYS_SINCE_LAST_TRANSFER"),
        F.col("DAYS_SINCE_REGISTRATION"),
        F.col("TRANSFER_COMPLETION_RATE"),
        F.col("MONTHLY_TRANSFER_RATE"),
        F.col("DISTINCT_CORRIDORS"),
        F.col("DISTINCT_CHANNELS"),
        F.col("WALLET_BALANCE_ZAR"),
        F.col("TOTAL_CARD_SPEND_ZAR"),
        F.col("ENGAGEMENT_SCORE"),
        F.col("LTV_SCORE"),
        F.col("IS_FULLY_VERIFIED").cast(IntegerType()),
        F.col("HAS_SA_ID").cast(IntegerType()),
        F.hash(F.col("CUSTOMER_SEGMENT")).alias("SEGMENT_HASH"),
        F.hash(F.col("RISK_BAND")).alias("RISK_BAND_HASH"),
        F.hash(F.col("KYC_LEVEL")).alias("KYC_LEVEL_HASH"),
        F.hash(F.col("ACQUISITION_SOURCE")).alias("ACQUISITION_HASH"),
    )

    features.write.mode("overwrite").save_as_table(
        "AFRIMONEY_ML_DB.FEATURE_STORE.CHURN_FEATURES"
    )
    print(f"  Churn features: {features.count():,} rows saved")
    return "AFRIMONEY_ML_DB.FEATURE_STORE.CHURN_FEATURES"


def build_credit_features(session: Session):
    """Credit risk features for Mukuru loan PD model."""
    print("\n[FEATURE STORE] Building credit risk features...")

    df = session.table("AFRIMONEY_DB.BRONZE.FACT_LOAN_APPLICATION").filter(
        F.col("DECISION") == "APPROVED"
    )

    features = df.select(
        F.col("LOAN_ID"),
        F.col("CUSTOMER_ID"),
        (F.col("LOAN_STATUS").isin(["DEFAULTED","WRITTEN_OFF"]) |
         (F.col("DAYS_PAST_DUE") > 90)).cast(IntegerType()).alias("LABEL_DEFAULT"),
        F.col("PRINCIPAL_ZAR"),
        F.col("INTEREST_RATE_ANNUAL_PCT"),
        F.col("TERM_MONTHS"),
        F.col("MONTHLY_PAYMENT_ZAR"),
        (F.col("MONTHLY_PAYMENT_ZAR") / F.greatest(F.col("AVG_MONTHLY_CARD_SPEND_ZAR"), F.lit(100))).alias("PAYMENT_TO_INCOME_RATIO"),
        F.col("CARD_ACCOUNT_AGE_DAYS"),
        F.col("AVG_MONTHLY_CARD_SPEND_ZAR"),
        F.col("SALARY_INDICATOR").cast(IntegerType()),
        F.col("PREVIOUS_LOANS"),
        F.col("PREVIOUS_LOANS_REPAID"),
        (F.col("PREVIOUS_LOANS_REPAID") / F.greatest(F.col("PREVIOUS_LOANS"), F.lit(1))).alias("REPAYMENT_HISTORY_RATE"),
    )

    features.write.mode("overwrite").save_as_table(
        "AFRIMONEY_ML_DB.FEATURE_STORE.CREDIT_FEATURES"
    )
    print(f"  Credit features: {features.count():,} rows saved")
    return "AFRIMONEY_ML_DB.FEATURE_STORE.CREDIT_FEATURES"


# ── Model Training ────────────────────────────────────────────

def train_fraud_model(session: Session, feature_table: str):
    """Train GBM fraud detection model using Snowpark ML."""
    print("\n[ML TRAINING] Fraud Detection Model...")

    df = session.table(feature_table)

    FEATURE_COLS = [
        "SEND_AMOUNT_LOG","SEND_AMOUNT_ZAR","TRANSFER_FEE_ZAR","FEE_PCT",
        "FX_MARGIN_ZAR","FX_SPREAD_PCT","PAYMENT_ATTEMPTS","PAYOUT_ATTEMPTS",
        "HOUR_OF_DAY","DAY_OF_WEEK","BUSINESS_KEY_HASH","CORRIDOR_HASH",
        "CHANNEL_HASH","PAY_METHOD_HASH","PAYOUT_METHOD_HASH"
    ]
    LABEL_COL = "LABEL_FRAUD"

    # Train/test split (80/20 using Snowpark)
    train_df, test_df = df.random_split([0.8, 0.2], seed=42)

    # Gradient Boosting Classifier (Snowpark ML wrapper over XGBoost)
    model = snowml_ensemble.GradientBoostingClassifier(
        input_cols  = FEATURE_COLS,
        label_cols  = [LABEL_COL],
        output_cols = ["FRAUD_SCORE_RAW"],
        n_estimators= 200,
        max_depth   = 5,
        learning_rate= 0.05,
        subsample   = 0.8,
        random_state= 42,
    )
    model.fit(train_df)

    # Evaluate
    predictions = model.predict_proba(test_df)
    # AUC calculation via Snowflake ML metrics
    from snowflake.ml.modeling.metrics import roc_auc_score
    auc = roc_auc_score(
        df         = predictions,
        y_true_col_names   = LABEL_COL,
        y_score_col_names  = "PREDICT_PROBA_1",
    )
    print(f"  Fraud Model AUC-ROC: {auc:.4f}")

    return model, {"auc_roc": auc, "n_features": len(FEATURE_COLS)}


def train_churn_model(session: Session, feature_table: str):
    """Train Random Forest churn model."""
    print("\n[ML TRAINING] Customer Churn Model...")

    df = session.table(feature_table)

    FEATURE_COLS = [
        "TOTAL_TRANSFERS","COMPLETED_TRANSFERS","TOTAL_SEND_ZAR","AVG_SEND_ZAR",
        "LIFETIME_REVENUE_ZAR","DAYS_SINCE_LAST_TRANSFER","DAYS_SINCE_REGISTRATION",
        "TRANSFER_COMPLETION_RATE","MONTHLY_TRANSFER_RATE","DISTINCT_CORRIDORS",
        "DISTINCT_CHANNELS","WALLET_BALANCE_ZAR","TOTAL_CARD_SPEND_ZAR",
        "ENGAGEMENT_SCORE","LTV_SCORE","IS_FULLY_VERIFIED","HAS_SA_ID",
        "SEGMENT_HASH","RISK_BAND_HASH","KYC_LEVEL_HASH","ACQUISITION_HASH"
    ]
    LABEL_COL = "LABEL_CHURN"

    train_df, test_df = df.random_split([0.8, 0.2], seed=42)

    model = snowml_ensemble.RandomForestClassifier(
        input_cols  = FEATURE_COLS,
        label_cols  = [LABEL_COL],
        output_cols = ["CHURN_SCORE_RAW"],
        n_estimators= 300,
        max_depth   = 12,
        class_weight= "balanced",
        random_state= 42,
    )
    model.fit(train_df)

    predictions = model.predict_proba(test_df)
    from snowflake.ml.modeling.metrics import roc_auc_score
    auc = roc_auc_score(
        df=predictions,
        y_true_col_names="LABEL_CHURN",
        y_score_col_names="PREDICT_PROBA_1",
    )
    print(f"  Churn Model AUC-ROC: {auc:.4f}")
    return model, {"auc_roc": auc}


def train_credit_model(session: Session, feature_table: str):
    """Train credit PD model for Mukuru loans."""
    print("\n[ML TRAINING] Credit Risk PD Model...")

    df = session.table(feature_table)

    FEATURE_COLS = [
        "PRINCIPAL_ZAR","INTEREST_RATE_ANNUAL_PCT","TERM_MONTHS",
        "MONTHLY_PAYMENT_ZAR","PAYMENT_TO_INCOME_RATIO","CARD_ACCOUNT_AGE_DAYS",
        "AVG_MONTHLY_CARD_SPEND_ZAR","SALARY_INDICATOR","PREVIOUS_LOANS",
        "PREVIOUS_LOANS_REPAID","REPAYMENT_HISTORY_RATE"
    ]
    LABEL_COL = "LABEL_DEFAULT"

    train_df, test_df = df.random_split([0.8, 0.2], seed=42)

    model = snowml_ensemble.GradientBoostingClassifier(
        input_cols  = FEATURE_COLS,
        label_cols  = [LABEL_COL],
        output_cols = ["PD_SCORE_RAW"],
        n_estimators= 200,
        max_depth   = 4,
        learning_rate= 0.05,
        random_state= 42,
    )
    model.fit(train_df)

    predictions = model.predict_proba(test_df)
    from snowflake.ml.modeling.metrics import roc_auc_score
    auc = roc_auc_score(
        df=predictions,
        y_true_col_names="LABEL_DEFAULT",
        y_score_col_names="PREDICT_PROBA_1",
    )
    print(f"  Credit PD AUC-ROC: {auc:.4f}")
    return model, {"auc_roc": auc}


# ── Model Registry ────────────────────────────────────────────

def register_and_score(session, model_name, model, metrics, score_table, score_cols, label_col, output_col):
    """Register model in Snowflake Model Registry and write scored predictions."""
    print(f"\n[REGISTRY] Registering {model_name}...")

    reg = Registry(session=session, database_name="AFRIMONEY_ML_DB", schema_name="MODEL_REGISTRY")

    mv = reg.log_model(
        model,
        model_name    = model_name,
        version_name  = f"v1_{datetime.now().strftime('%Y%m%d')}",
        comment       = f"AfriMoney {model_name} | AUC={metrics.get('auc_roc',0):.4f}",
        metrics       = metrics,
        tags          = {"project": "afrimoney", "env": "prod"},
    )
    print(f"  Registered: {mv.model_name} @ {mv.version_name}")

    # Score full dataset and write predictions
    score_df = session.table(score_table)
    predictions = mv.run(score_df, function_name="PREDICT_PROBA")
    predictions = predictions.with_column(
        output_col,
        F.col("PREDICT_PROBA_1")
    )
    predictions.select(label_col, output_col, *score_cols[:5]).write.mode("overwrite").save_as_table(
        f"AFRIMONEY_ML_DB.PREDICTIONS.{model_name.upper()}_SCORES"
    )
    print(f"  Scores written to PREDICTIONS.{model_name.upper()}_SCORES")
    return mv


# ── Snowflake UDF: Fraud Score ────────────────────────────────
FRAUD_UDF_SQL = """
CREATE OR REPLACE FUNCTION AFRIMONEY_DB.UTILS.GET_FRAUD_SCORE(
    SEND_AMOUNT_ZAR     FLOAT,
    FX_SPREAD_PCT       FLOAT,
    PAYMENT_ATTEMPTS    INT,
    HOUR_OF_DAY         INT,
    CHANNEL_HASH        INT
)
RETURNS FLOAT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
PACKAGES = ('snowflake-snowpark-python','scikit-learn')
HANDLER = 'compute_fraud_score'
AS $$
# Lightweight rule-based fallback (replace with pickled model in production)
def compute_fraud_score(amount, spread, attempts, hour, channel):
    score = 0.0
    if amount > 20000:   score += 0.3
    if spread > 7.0:     score += 0.2
    if attempts > 2:     score += 0.25
    if hour < 5:         score += 0.15   # late-night transfer
    if channel == 0:     score += 0.1    # unknown channel
    return min(score, 1.0)
$$;
""".strip()


# ── Stored Procedure: Daily ML Refresh ───────────────────────
DAILY_REFRESH_PROC = """
CREATE OR REPLACE PROCEDURE AFRIMONEY_ML_DB.EXPERIMENTS.DAILY_ML_REFRESH()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    -- Step 1: Refresh feature tables
    CREATE OR REPLACE TABLE AFRIMONEY_ML_DB.FEATURE_STORE.FRAUD_FEATURES AS
    SELECT
        TRANSFER_ID,
        IS_SUSPECTED_FRAUD::INT                             AS LABEL_FRAUD,
        LN(GREATEST(SEND_AMOUNT_ZAR,1))                    AS SEND_AMOUNT_LOG,
        SEND_AMOUNT_ZAR,
        TRANSFER_FEE_ZAR,
        TRANSFER_FEE_ZAR / GREATEST(SEND_AMOUNT_ZAR,1)    AS FEE_PCT,
        FX_SPREAD_PCT,
        PAYMENT_ATTEMPTS,
        HOUR(CREATED_DATETIME)                             AS HOUR_OF_DAY,
        DAYOFWEEK(CREATED_DATETIME)                        AS DAY_OF_WEEK,
        HASH(BUSINESS_KEY)                                 AS BUSINESS_KEY_HASH,
        HASH(CORRIDOR_CODE)                                AS CORRIDOR_HASH,
        HASH(CHANNEL)                                      AS CHANNEL_HASH
    FROM AFRIMONEY_DB.BRONZE.FACT_REMITTANCE_TRANSFER
    WHERE CREATED_DATETIME >= DATEADD('day', -90, CURRENT_TIMESTAMP());

    -- Step 2: Refresh churn features from Gold mart
    CREATE OR REPLACE TABLE AFRIMONEY_ML_DB.FEATURE_STORE.CHURN_FEATURES AS
    SELECT
        CUSTOMER_ID, BUSINESS_KEY,
        IS_CHURNED::INT                 AS LABEL_CHURN,
        TOTAL_TRANSFERS,
        DAYS_SINCE_LAST_TRANSFER,
        TRANSFER_COMPLETION_RATE,
        MONTHLY_TRANSFER_RATE,
        LTV_SCORE,
        ENGAGEMENT_SCORE,
        HASH(CUSTOMER_SEGMENT)          AS SEGMENT_HASH,
        HASH(RISK_BAND)                 AS RISK_BAND_HASH
    FROM AFRIMONEY_DB.GOLD.MART_CUSTOMER_360;

    RETURN 'Daily ML feature refresh complete at ' || CURRENT_TIMESTAMP();
END;
$$;
""".strip()


# ── Main Pipeline ─────────────────────────────────────────────
if __name__ == "__main__":
    try:
        # 1. Build feature tables
        fraud_ft  = build_fraud_features(session)
        churn_ft  = build_churn_features(session)
        credit_ft = build_credit_features(session)

        # 2. Train models
        fraud_model,  fraud_metrics  = train_fraud_model(session, fraud_ft)
        churn_model,  churn_metrics  = train_churn_model(session, churn_ft)
        credit_model, credit_metrics = train_credit_model(session, credit_ft)

        # 3. Register in Snowflake Model Registry
        register_and_score(session, "FRAUD_DETECTION",    fraud_model,  fraud_metrics,
                           fraud_ft, ["TRANSFER_ID","BUSINESS_KEY"], "LABEL_FRAUD", "FRAUD_PROBABILITY")
        register_and_score(session, "CUSTOMER_CHURN",     churn_model,  churn_metrics,
                           churn_ft, ["CUSTOMER_ID","BUSINESS_KEY"], "LABEL_CHURN", "CHURN_PROBABILITY")
        register_and_score(session, "CREDIT_RISK_PD",     credit_model, credit_metrics,
                           credit_ft, ["LOAN_ID","CUSTOMER_ID"], "LABEL_DEFAULT", "PD_PROBABILITY")

        # 4. Deploy UDF & stored procedure
        session.sql(FRAUD_UDF_SQL).collect()
        session.sql(DAILY_REFRESH_PROC).collect()
        print("\n[DEPLOY] Fraud score UDF and daily refresh procedure deployed.")

        # 5. Log experiment results
        results = {
            "run_timestamp": datetime.now().isoformat(),
            "models": {
                "fraud_detection": fraud_metrics,
                "customer_churn":  churn_metrics,
                "credit_risk_pd":  credit_metrics,
            }
        }
        session.sql(f"""
            INSERT INTO AFRIMONEY_ML_DB.EXPERIMENTS.RUN_LOG (RUN_TIMESTAMP, MODEL_NAME, METRICS_JSON)
            SELECT
                '{results['run_timestamp']}' AS RUN_TIMESTAMP,
                m.MODEL_NAME,
                m.METRICS_JSON
            FROM VALUES
                ('fraud_detection', '{json.dumps(fraud_metrics)}'),
                ('customer_churn',  '{json.dumps(churn_metrics)}'),
                ('credit_risk_pd',  '{json.dumps(credit_metrics)}')
            AS m(MODEL_NAME, METRICS_JSON)
        """).collect()

        print("\n" + "="*60)
        print("SNOWPARK ML PIPELINE COMPLETE")
        print("="*60)
        print(f"  Fraud Detection  AUC: {fraud_metrics['auc_roc']:.4f}")
        print(f"  Customer Churn   AUC: {churn_metrics['auc_roc']:.4f}")
        print(f"  Credit Risk PD   AUC: {credit_metrics['auc_roc']:.4f}")
        print("\nAll models registered in Snowflake Model Registry.")
        print("Scores written to AFRIMONEY_ML_DB.PREDICTIONS.*")

    finally:
        session.close()
