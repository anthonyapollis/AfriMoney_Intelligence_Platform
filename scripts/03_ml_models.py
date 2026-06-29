"""
African Fintech Intelligence Platform
Phase 3: Machine Learning Models
5 models covering fraud, churn, credit risk, FX, and transfer success
"""

import pandas as pd
import numpy as np
import json, pickle
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import (
    GradientBoostingClassifier, RandomForestClassifier,
    GradientBoostingRegressor, RandomForestRegressor
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, classification_report, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score,
    average_precision_score
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings("ignore")

BASE    = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
BRONZE  = BASE / "data" / "bronze"
GOLD    = BASE / "data" / "gold"
ML_DIR  = BASE / "ml_models"

results_log = []

def log_model(name, metrics, params):
    results_log.append({"model": name, "timestamp": datetime.now().isoformat(), **metrics, **params})
    print(f"\n  Model: {name}")
    for k,v in metrics.items():
        print(f"    {k}: {v}")

def save_model(model, name):
    with open(ML_DIR / f"{name}.pkl","wb") as f:
        pickle.dump(model, f)
    print(f"  [SAVED] {name}.pkl")

print("Loading data for ML...")
transfers  = pd.read_csv(BRONZE / "fact_remittance_transfer.csv", low_memory=False)
customers  = pd.read_csv(BRONZE / "dim_customer.csv", low_memory=False)
loans      = pd.read_csv(BRONZE / "fact_loan_application.csv", low_memory=False)
loan_repay = pd.read_csv(BRONZE / "fact_loan_repayment.csv", low_memory=False)
cards      = pd.read_csv(BRONZE / "fact_card_transaction.csv", low_memory=False)

print("  Data loaded.\n")

# ══════════════════════════════════════════════════════════════════════════════
# MODEL 1: FRAUD DETECTION
# Binary classifier: predict is_suspected_fraud
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("MODEL 1: FRAUD DETECTION (GBM)")
print("=" * 60)

# Feature engineering
tf = transfers.copy()
tf["hour"]        = pd.to_datetime(tf["created_datetime"]).dt.hour
tf["day_of_week"] = pd.to_datetime(tf["created_datetime"]).dt.dayofweek
tf["is_weekend"]  = tf["day_of_week"] >= 5
tf["amount_log"]  = np.log1p(tf["send_amount_zar"])
tf["fee_pct"]     = tf["transfer_fee_zar"] / tf["send_amount_zar"].clip(lower=1)

cat_cols = ["business_key","corridor_code","channel","payment_method","payout_method"]
for c in cat_cols:
    le = LabelEncoder()
    tf[f"{c}_enc"] = le.fit_transform(tf[c].fillna("UNKNOWN"))

fraud_features = [
    "send_amount_zar","amount_log","transfer_fee_zar","fee_pct",
    "fx_margin_zar","net_revenue_zar","fx_spread_pct","payment_attempts",
    "payout_attempts","hour","day_of_week","is_weekend",
    "business_key_enc","corridor_code_enc","channel_enc",
    "payment_method_enc","payout_method_enc"
]
fraud_features = [f for f in fraud_features if f in tf.columns]

X_fraud = tf[fraud_features].fillna(0)
y_fraud = tf["is_suspected_fraud"].astype(int)

X_tr, X_te, y_tr, y_te = train_test_split(X_fraud, y_fraud, test_size=0.2,
                                            random_state=42, stratify=y_fraud)

fraud_model = GradientBoostingClassifier(
    n_estimators=200, max_depth=5, learning_rate=0.05,
    subsample=0.8, min_samples_leaf=50, random_state=42)
fraud_model.fit(X_tr, y_tr)

y_prob = fraud_model.predict_proba(X_te)[:,1]
y_pred = (y_prob > 0.4).astype(int)
auc  = roc_auc_score(y_te, y_prob)
ap   = average_precision_score(y_te, y_prob)

log_model("fraud_detection", {
    "auc_roc": round(auc,4), "avg_precision": round(ap,4),
    "precision": round(y_te[y_pred==1].mean(),4) if y_pred.sum()>0 else 0,
    "recall": round(y_pred[y_te==1].mean(),4),
    "fraud_flag_rate_pct": round(y_pred.mean()*100,3),
}, {"algorithm":"GradientBoostingClassifier","n_estimators":200,"threshold":0.4})

# Feature importance
fi = pd.DataFrame({"feature":fraud_features,
                    "importance":fraud_model.feature_importances_}).sort_values("importance",ascending=False)
fi.to_csv(ML_DIR / "fraud_model_feature_importance.csv", index=False)
save_model(fraud_model, "fraud_detection_model")

# Scored output (sample 200K)
sample_tf = tf.sample(min(200_000, len(tf)), random_state=42)
sample_tf["fraud_score"] = fraud_model.predict_proba(sample_tf[fraud_features].fillna(0))[:,1].round(4)
sample_tf["fraud_flag"]  = (sample_tf["fraud_score"] > 0.4)
sample_tf[["transfer_id","business_key","fraud_score","fraud_flag","send_amount_zar","corridor_code"]].to_csv(
    ML_DIR / "fraud_scored_transfers.csv", index=False)
print(f"  Fraud scored output: {len(sample_tf):,} rows")

# ══════════════════════════════════════════════════════════════════════════════
# MODEL 2: CUSTOMER CHURN PREDICTION
# Binary: will the customer NOT transact in the next 90 days?
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MODEL 2: CUSTOMER CHURN PREDICTION (Random Forest)")
print("=" * 60)

cust_agg = transfers.groupby("sender_customer_id").agg(
    total_transfers=("transfer_id","count"),
    completed_transfers=("is_completed","sum"),
    total_volume_zar=("send_amount_zar","sum"),
    avg_volume_zar=("send_amount_zar","mean"),
    std_volume_zar=("send_amount_zar","std"),
    total_revenue_zar=("net_revenue_zar","sum"),
    distinct_corridors=("corridor_code","nunique"),
    distinct_channels=("channel","nunique"),
    days_since_last=("created_datetime", lambda x: (
        pd.Timestamp("2026-06-28") - pd.to_datetime(x).max()).days),
    days_since_first=("created_datetime", lambda x: (
        pd.Timestamp("2026-06-28") - pd.to_datetime(x).min()).days),
    failed_count=("is_failed","sum"),
    cancelled_count=("is_cancelled","sum"),
).reset_index()
cust_agg.columns = ["customer_id"] + list(cust_agg.columns[1:])
cust_agg["success_rate"] = (cust_agg["completed_transfers"]/cust_agg["total_transfers"].clip(lower=1))
cust_agg["failure_rate"] = (cust_agg["failed_count"]/cust_agg["total_transfers"].clip(lower=1))
cust_agg["transfer_freq"] = (cust_agg["total_transfers"]/cust_agg["days_since_first"].clip(lower=1)*30)
cust_agg["is_churned"]   = (cust_agg["days_since_last"] > 90).astype(int)

# Merge customer demographics
cust_ml = cust_agg.merge(
    customers[["customer_id","business_key","kyc_level","risk_band","customer_segment",
               "monthly_income_band","acquisition_source","has_sa_id"]],
    on="customer_id", how="left")

cat_c = ["business_key","kyc_level","risk_band","customer_segment","monthly_income_band","acquisition_source"]
for c in cat_c:
    le = LabelEncoder()
    cust_ml[f"{c}_enc"] = le.fit_transform(cust_ml[c].fillna("UNK"))

churn_features = [
    "total_transfers","completed_transfers","total_volume_zar","avg_volume_zar",
    "std_volume_zar","total_revenue_zar","distinct_corridors","distinct_channels",
    "days_since_last","days_since_first","failed_count","cancelled_count",
    "success_rate","failure_rate","transfer_freq","has_sa_id",
    "business_key_enc","kyc_level_enc","risk_band_enc","customer_segment_enc",
    "monthly_income_band_enc","acquisition_source_enc",
]
churn_features = [f for f in churn_features if f in cust_ml.columns]

X_ch = cust_ml[churn_features].fillna(0)
y_ch = cust_ml["is_churned"]

X_tr, X_te, y_tr, y_te = train_test_split(X_ch, y_ch, test_size=0.2, random_state=42, stratify=y_ch)

churn_model = RandomForestClassifier(
    n_estimators=300, max_depth=12, min_samples_leaf=20,
    class_weight="balanced", n_jobs=-1, random_state=42)
churn_model.fit(X_tr, y_tr)

y_prob = churn_model.predict_proba(X_te)[:,1]
y_pred = (y_prob > 0.5).astype(int)
auc = roc_auc_score(y_te, y_prob)
ap  = average_precision_score(y_te, y_prob)

log_model("churn_prediction", {
    "auc_roc": round(auc,4), "avg_precision": round(ap,4),
    "churn_pct_predicted": round(y_pred.mean()*100,2),
    "actual_churn_pct": round(y_ch.mean()*100,2),
}, {"algorithm":"RandomForestClassifier","n_estimators":300,"threshold":0.5})

fi2 = pd.DataFrame({"feature":churn_features,
                     "importance":churn_model.feature_importances_}).sort_values("importance",ascending=False)
fi2.to_csv(ML_DIR / "churn_model_feature_importance.csv", index=False)
save_model(churn_model, "churn_prediction_model")

cust_ml["churn_probability"] = churn_model.predict_proba(X_ch)[:,1].round(4)
cust_ml["churn_segment"] = pd.cut(
    cust_ml["churn_probability"],
    bins=[-0.01,0.20,0.40,0.60,0.80,1.01],
    labels=["very_low","low","medium","high","very_high"])
cust_ml[["customer_id","business_key","churn_probability","churn_segment",
          "days_since_last","total_transfers","total_volume_zar"]].to_csv(
    ML_DIR / "churn_scored_customers.csv", index=False)
print(f"  Churn scored: {len(cust_ml):,} customers")

# ══════════════════════════════════════════════════════════════════════════════
# MODEL 3: CREDIT RISK — Mukuru Loans
# PD (Probability of Default) model
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MODEL 3: CREDIT RISK / PD MODEL (GBM)")
print("=" * 60)

loan_data = loans[loans["decision"]=="APPROVED"].copy()
# Repayment aggregation
repay_agg = loan_repay.groupby("loan_id").agg(
    total_instalments=("repayment_id","count"),
    missed_instalments=("payment_status", lambda x: (x=="MISSED").sum()),
    collection_rate=("amount_paid_zar","sum"),
    total_due=("amount_due_zar","sum"),
    max_dpd=("days_past_due","max"),
).reset_index()
repay_agg["collection_rate"] = repay_agg["collection_rate"]/repay_agg["total_due"].clip(lower=1)
repay_agg["miss_rate"] = repay_agg["missed_instalments"]/repay_agg["total_instalments"].clip(lower=1)

loan_ml = loan_data.merge(repay_agg, on="loan_id", how="left")
loan_ml["actual_default"] = ((loan_ml["loan_status"].isin(["DEFAULTED","WRITTEN_OFF"])) |
                              (loan_ml.get("max_dpd",0) > 90)).astype(int)

credit_features = [
    "principal_zar","term_months","interest_rate_annual_pct","monthly_payment_zar",
    "card_account_age_days","avg_monthly_card_spend_zar","salary_indicator",
    "previous_loans","previous_loans_repaid",
]
credit_features = [f for f in credit_features if f in loan_ml.columns]

X_cr = loan_ml[credit_features].fillna(0)
y_cr = loan_ml["actual_default"]

if y_cr.sum() > 10:
    X_tr, X_te, y_tr, y_te = train_test_split(X_cr, y_cr, test_size=0.2, random_state=42, stratify=y_cr)

    credit_model = GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.05,
        subsample=0.8, min_samples_leaf=20, random_state=42)
    credit_model.fit(X_tr, y_tr)

    y_prob = credit_model.predict_proba(X_te)[:,1]
    auc = roc_auc_score(y_te, y_prob)
    ap  = average_precision_score(y_te, y_prob)

    log_model("credit_risk_pd", {
        "auc_roc": round(auc,4), "avg_precision": round(ap,4),
        "default_rate_actual_pct": round(y_cr.mean()*100,2),
    }, {"algorithm":"GradientBoostingClassifier","target":"probability_of_default"})

    save_model(credit_model, "credit_risk_pd_model")

    fi3 = pd.DataFrame({"feature":credit_features,
                         "importance":credit_model.feature_importances_}).sort_values("importance",ascending=False)
    fi3.to_csv(ML_DIR / "credit_model_feature_importance.csv", index=False)

    loan_ml["pd_score_model"] = credit_model.predict_proba(X_cr)[:,1].round(4)
    loan_ml["ecl_model_zar"]  = (loan_ml["pd_score_model"] * loan_ml["principal_zar"] * 0.45).round(2)
    loan_ml["risk_grade"] = pd.cut(
        loan_ml["pd_score_model"],
        bins=[-0.01,0.05,0.10,0.20,0.35,1.01],
        labels=["A","B","C","D","E"])
    loan_ml[["loan_id","customer_id","principal_zar","pd_score_model","ecl_model_zar","risk_grade",
              "loan_status","actual_default"]].to_csv(ML_DIR / "credit_scored_loans.csv", index=False)
    print(f"  Credit scored: {len(loan_ml):,} loans")

# ══════════════════════════════════════════════════════════════════════════════
# MODEL 4: TRANSFER SUCCESS PREDICTION
# Predict if a transfer will complete successfully
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MODEL 4: TRANSFER SUCCESS PREDICTION (Random Forest)")
print("=" * 60)

success_df = tf.copy()
success_df["is_completed_int"] = success_df["is_completed"].astype(int)

success_features = [
    "send_amount_zar","amount_log","transfer_fee_zar","fee_pct",
    "hour","day_of_week","is_weekend",
    "business_key_enc","corridor_code_enc","channel_enc",
    "payment_method_enc","payout_method_enc"
]
success_features = [f for f in success_features if f in success_df.columns]

X_su = success_df[success_features].fillna(0)
y_su = success_df["is_completed_int"]

X_tr, X_te, y_tr, y_te = train_test_split(X_su, y_su, test_size=0.2, random_state=42, stratify=y_su)

# Sample for speed
sample_idx = np.random.choice(len(X_tr), min(500_000, len(X_tr)), replace=False)
success_model = RandomForestClassifier(
    n_estimators=200, max_depth=10, min_samples_leaf=50,
    n_jobs=-1, random_state=42)
success_model.fit(X_tr.iloc[sample_idx], y_tr.iloc[sample_idx])

y_prob = success_model.predict_proba(X_te)[:,1]
auc = roc_auc_score(y_te, y_prob)

log_model("transfer_success", {
    "auc_roc": round(auc,4),
    "completion_rate_actual_pct": round(y_su.mean()*100,2),
}, {"algorithm":"RandomForestClassifier","n_estimators":200})

save_model(success_model, "transfer_success_model")

fi4 = pd.DataFrame({"feature":success_features,
                     "importance":success_model.feature_importances_}).sort_values("importance",ascending=False)
fi4.to_csv(ML_DIR / "success_model_feature_importance.csv", index=False)

# ══════════════════════════════════════════════════════════════════════════════
# MODEL 5: FX SPREAD / REVENUE REGRESSION
# Predict net revenue per transfer
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("MODEL 5: REVENUE / FX MARGIN REGRESSION (GBM)")
print("=" * 60)

rev_df = tf[tf["is_completed"]==True].copy()
rev_features = [
    "send_amount_zar","amount_log","fx_spread_pct","market_fx_rate","customer_fx_rate",
    "hour","day_of_week","is_weekend",
    "business_key_enc","corridor_code_enc","channel_enc",
    "payment_method_enc","payout_method_enc"
]
rev_features = [f for f in rev_features if f in rev_df.columns]

X_rv = rev_df[rev_features].fillna(0)
y_rv = rev_df["net_revenue_zar"]

X_tr, X_te, y_tr, y_te = train_test_split(X_rv, y_rv, test_size=0.2, random_state=42)

sample_idx = np.random.choice(len(X_tr), min(500_000, len(X_tr)), replace=False)
rev_model = GradientBoostingRegressor(
    n_estimators=200, max_depth=5, learning_rate=0.05,
    subsample=0.8, min_samples_leaf=50, random_state=42)
rev_model.fit(X_tr.iloc[sample_idx], y_tr.iloc[sample_idx])

y_pred = rev_model.predict(X_te)
mae  = mean_absolute_error(y_te, y_pred)
rmse = np.sqrt(mean_squared_error(y_te, y_pred))
r2   = r2_score(y_te, y_pred)

log_model("revenue_regression", {
    "mae_zar": round(mae,2), "rmse_zar": round(rmse,2), "r2_score": round(r2,4),
    "avg_actual_revenue_zar": round(y_rv.mean(),2),
}, {"algorithm":"GradientBoostingRegressor","target":"net_revenue_zar"})

save_model(rev_model, "revenue_regression_model")

fi5 = pd.DataFrame({"feature":rev_features,
                     "importance":rev_model.feature_importances_}).sort_values("importance",ascending=False)
fi5.to_csv(ML_DIR / "revenue_model_feature_importance.csv", index=False)

# Save full results log
results_df = pd.DataFrame(results_log)
results_df.to_csv(ML_DIR / "ml_model_results_summary.csv", index=False)
print(f"\n  [SAVED] ml_model_results_summary.csv")

# ML Summary for reporting
print("\n" + "=" * 60)
print("ML MODEL SUMMARY")
print("=" * 60)
print(results_df[["model","auc_roc","avg_precision","mae_zar","r2_score","algorithm"]].to_string())
print("\nAll 5 ML models complete.")
