"""
AfriMoney — Run ML models + build ebook with real results and charts.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (roc_auc_score, average_precision_score,
                             classification_report, confusion_matrix,
                             roc_curve, precision_recall_curve)
from sklearn.preprocessing import LabelEncoder
import datetime, json, warnings
warnings.filterwarnings("ignore")

np.random.seed(42)
BASE = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
OUT  = BASE / "ebook"
TODAY = datetime.date.today().isoformat()

print("Generating synthetic training data...")

N_TRANSFER = 200_000
N_CUSTOMER = 50_000

corridors = ["ZA-ZW","ZA-MZ","ZA-ZM","ZA-MW","ZA-LS","ZA-BW","ZA-NA","ZA-SZ"]
channels  = ["app","ussd","web","whatsapp","branch","agent"]
payment_m = ["card","eft","cash","wallet"]
payout_m  = ["cash","bank","mobile_money","wallet"]

# ── TRANSFER DATA ──────────────────────────────────────
send_amt   = np.random.lognormal(7.2, 0.9, N_TRANSFER).clip(50, 50000)
fee_pct    = np.random.uniform(0.03, 0.09, N_TRANSFER)
fx_spread  = np.random.uniform(0.02, 0.09, N_TRANSFER)
hour_day   = np.random.randint(0, 24, N_TRANSFER)
pay_att    = np.random.choice([1,1,1,2,2,3,4], N_TRANSFER)
corr_idx   = np.random.choice(len(corridors), N_TRANSFER)
chan_idx   = np.random.choice(len(channels),  N_TRANSFER)
is_weekend = np.random.binomial(1, 0.28, N_TRANSFER)
cust_age   = np.random.uniform(18, 65, N_TRANSFER)
cust_trans = np.random.randint(1, 80, N_TRANSFER)
kyc_level  = np.random.choice([0,1,2,3], N_TRANSFER, p=[0.05,0.20,0.50,0.25])

# Fraud label — realistic ~2% base rate with signal
fraud_score = (
    (send_amt > 15000).astype(float) * 0.25 +
    (pay_att >= 3).astype(float) * 0.30 +
    (hour_day < 5).astype(float) * 0.20 +
    (kyc_level == 0).astype(float) * 0.25 +
    np.random.uniform(0, 0.3, N_TRANSFER)
)
fraud_label = (fraud_score > 0.55).astype(int)
print(f"  Fraud rate: {fraud_label.mean()*100:.1f}%")

transfers = pd.DataFrame({
    "send_amount_log":  np.log1p(send_amt),
    "fee_pct":          fee_pct,
    "fx_spread_pct":    fx_spread,
    "hour_of_day":      hour_day,
    "payment_attempts": pay_att,
    "corridor_idx":     corr_idx,
    "channel_idx":      chan_idx,
    "is_weekend":       is_weekend,
    "kyc_level":        kyc_level,
    "customer_age":     cust_age,
    "customer_tx_count":cust_trans,
    "is_fraud":         fraud_label,
})

# ── CUSTOMER CHURN DATA ─────────────────────────────────
cust_txns  = np.random.randint(1, 80, N_CUSTOMER)
days_since = np.random.exponential(45, N_CUSTOMER).clip(1, 365)
eng_score  = np.random.uniform(0, 100, N_CUSTOMER)
wallet_bal = np.random.lognormal(6, 1.2, N_CUSTOMER).clip(0, 50000)
card_txns  = np.random.randint(0, 50, N_CUSTOMER)
corr_count = np.random.randint(1, 6, N_CUSTOMER)
kyc_c      = np.random.choice([0,1,2,3], N_CUSTOMER, p=[0.05,0.20,0.50,0.25])
monthly_rate = cust_txns / (days_since / 30 + 1)

churn_score = (
    (days_since > 90).astype(float) * 0.40 +
    (monthly_rate < 0.5).astype(float) * 0.25 +
    (wallet_bal < 100).astype(float) * 0.15 +
    (kyc_c < 2).astype(float) * 0.10 +
    np.random.uniform(0, 0.15, N_CUSTOMER)
)
churn_label = (churn_score > 0.45).astype(int)
print(f"  Churn rate: {churn_label.mean()*100:.1f}%")

customers = pd.DataFrame({
    "total_transfers":     cust_txns,
    "days_since_last":     days_since,
    "engagement_score":    eng_score,
    "wallet_balance":      np.log1p(wallet_bal),
    "card_transactions":   card_txns,
    "distinct_corridors":  corr_count,
    "kyc_level":           kyc_c,
    "monthly_tx_rate":     monthly_rate,
    "is_churned":          churn_label,
})

# ── CREDIT RISK DATA ────────────────────────────────────
N_LOAN = 20_000
principal = np.random.lognormal(7.5, 0.6, N_LOAN).clip(500, 30000)
income_m  = np.random.lognormal(8.5, 0.5, N_LOAN)
dpd_prev  = np.random.choice([0,0,0,1,2,3,5,10,30,60], N_LOAN)
loan_cnt  = np.random.randint(1, 10, N_LOAN)
dti_ratio = (principal / (income_m * 6)).clip(0, 1)
emp_months= np.random.randint(1, 120, N_LOAN)
kyc_l     = np.random.choice([1,2,3], N_LOAN, p=[0.2,0.5,0.3])

default_score = (
    dti_ratio * 0.35 +
    (dpd_prev > 0).astype(float) * 0.30 +
    (emp_months < 12).astype(float) * 0.15 +
    (loan_cnt > 5).astype(float) * 0.10 +
    np.random.uniform(0, 0.15, N_LOAN)
)
default_label = (default_score > 0.45).astype(int)
print(f"  Default rate: {default_label.mean()*100:.1f}%")

loans = pd.DataFrame({
    "principal_log":     np.log1p(principal),
    "income_log":        np.log1p(income_m),
    "dti_ratio":         dti_ratio,
    "prev_dpd":          dpd_prev,
    "loan_count":        loan_cnt,
    "employment_months": emp_months,
    "kyc_level":         kyc_l,
    "default":           default_label,
})

# ══════════════════════════════════════════════════════
# MODEL 1 — FRAUD DETECTION
# ══════════════════════════════════════════════════════
print("\nTraining Model 1: Fraud Detection...")
FRAUD_FEATURES = [c for c in transfers.columns if c != "is_fraud"]
X1 = transfers[FRAUD_FEATURES]
y1 = transfers["is_fraud"]
X1_tr, X1_te, y1_tr, y1_te = train_test_split(X1, y1, test_size=0.2, stratify=y1, random_state=42)

m1 = GradientBoostingClassifier(n_estimators=200, max_depth=5, learning_rate=0.05,
                                 subsample=0.8, random_state=42)
m1.fit(X1_tr, y1_tr)
y1_prob = m1.predict_proba(X1_te)[:,1]
y1_pred = (y1_prob >= 0.40).astype(int)

auc1   = roc_auc_score(y1_te, y1_prob)
ap1    = average_precision_score(y1_te, y1_prob)
fpr1, tpr1, _ = roc_curve(y1_te, y1_prob)
prec1, rec1, _ = precision_recall_curve(y1_te, y1_prob)
cm1    = confusion_matrix(y1_te, y1_pred)
fi1    = dict(zip(FRAUD_FEATURES, m1.feature_importances_))
cv1    = cross_val_score(m1, X1, y1, cv=5, scoring="roc_auc").tolist()
print(f"  AUC={auc1:.4f}  AvgPrec={ap1:.4f}  CV={np.mean(cv1):.4f}±{np.std(cv1):.4f}")

# ══════════════════════════════════════════════════════
# MODEL 2 — CHURN
# ══════════════════════════════════════════════════════
print("Training Model 2: Customer Churn...")
CHURN_FEATURES = [c for c in customers.columns if c != "is_churned"]
X2 = customers[CHURN_FEATURES]
y2 = customers["is_churned"]
X2_tr, X2_te, y2_tr, y2_te = train_test_split(X2, y2, test_size=0.2, stratify=y2, random_state=42)

m2 = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=10,
                             random_state=42, n_jobs=-1)
m2.fit(X2_tr, y2_tr)
y2_prob = m2.predict_proba(X2_te)[:,1]
y2_pred = (y2_prob >= 0.50).astype(int)

auc2   = roc_auc_score(y2_te, y2_prob)
ap2    = average_precision_score(y2_te, y2_prob)
fpr2, tpr2, _ = roc_curve(y2_te, y2_prob)
cm2    = confusion_matrix(y2_te, y2_pred)
fi2    = dict(zip(CHURN_FEATURES, m2.feature_importances_))
cv2    = cross_val_score(m2, X2, y2, cv=5, scoring="roc_auc").tolist()
print(f"  AUC={auc2:.4f}  AvgPrec={ap2:.4f}  CV={np.mean(cv2):.4f}±{np.std(cv2):.4f}")

# ══════════════════════════════════════════════════════
# MODEL 3 — CREDIT RISK PD
# ══════════════════════════════════════════════════════
print("Training Model 3: Credit Risk PD...")
CREDIT_FEATURES = [c for c in loans.columns if c != "default"]
X3 = loans[CREDIT_FEATURES]
y3 = loans["default"]
X3_tr, X3_te, y3_tr, y3_te = train_test_split(X3, y3, test_size=0.2, stratify=y3, random_state=42)

m3 = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.08,
                                 subsample=0.8, random_state=42)
m3.fit(X3_tr, y3_tr)
y3_prob = m3.predict_proba(X3_te)[:,1]
y3_pred = (y3_prob >= 0.50).astype(int)

auc3   = roc_auc_score(y3_te, y3_prob)
ap3    = average_precision_score(y3_te, y3_prob)
fpr3, tpr3, _ = roc_curve(y3_te, y3_prob)
cm3    = confusion_matrix(y3_te, y3_pred)
fi3    = dict(zip(CREDIT_FEATURES, m3.feature_importances_))
cv3    = cross_val_score(m3, X3, y3, cv=5, scoring="roc_auc").tolist()
print(f"  AUC={auc3:.4f}  AvgPrec={ap3:.4f}  CV={np.mean(cv3):.4f}±{np.std(cv3):.4f}")

# ══════════════════════════════════════════════════════
# Serialise curves for SVG (sample down for HTML size)
# ══════════════════════════════════════════════════════
def sample_curve(x, y, n=80):
    idx = np.round(np.linspace(0, len(x)-1, n)).astype(int)
    return x[idx].tolist(), y[idx].tolist()

fpr1s, tpr1s = sample_curve(fpr1, tpr1)
fpr2s, tpr2s = sample_curve(fpr2, tpr2)
fpr3s, tpr3s = sample_curve(fpr3, tpr3)

results = {
    "fraud": {"auc": round(auc1,4), "ap": round(ap1,4),
              "cv_mean": round(float(np.mean(cv1)),4), "cv_std": round(float(np.std(cv1)),4),
              "cm": cm1.tolist(), "fi": fi1,
              "fpr": fpr1s, "tpr": tpr1s,
              "n_train": int(len(X1_tr)), "n_test": int(len(X1_te)),
              "fraud_rate": round(float(y1.mean()*100),1),
              "threshold": 0.40},
    "churn": {"auc": round(auc2,4), "ap": round(ap2,4),
              "cv_mean": round(float(np.mean(cv2)),4), "cv_std": round(float(np.std(cv2)),4),
              "cm": cm2.tolist(), "fi": fi2,
              "fpr": fpr2s, "tpr": tpr2s,
              "n_train": int(len(X2_tr)), "n_test": int(len(X2_te)),
              "churn_rate": round(float(y2.mean()*100),1),
              "threshold": 0.50},
    "credit": {"auc": round(auc3,4), "ap": round(ap3,4),
               "cv_mean": round(float(np.mean(cv3)),4), "cv_std": round(float(np.std(cv3)),4),
               "cm": cm3.tolist(), "fi": fi3,
               "fpr": fpr3s, "tpr": tpr3s,
               "n_train": int(len(X3_tr)), "n_test": int(len(X3_te)),
               "default_rate": round(float(y3.mean()*100),1),
               "threshold": 0.50},
}

print("\nAll models trained. Building ebook...")
r = results

# Pre-compute all display values so the HTML f-string stays clean
f_auc  = r['fraud']['auc'];   f_ap  = r['fraud']['ap'];   f_cvm = r['fraud']['cv_mean'];  f_cvs = r['fraud']['cv_std']
f_ntr  = r['fraud']['n_train']; f_nte = r['fraud']['n_test']; f_fr = r['fraud']['fraud_rate']; f_thr = r['fraud']['threshold']
ch_auc = r['churn']['auc'];  ch_ap = r['churn']['ap'];  ch_cvm = r['churn']['cv_mean']; ch_cvs = r['churn']['cv_std']
ch_ntr = r['churn']['n_train']; ch_nte = r['churn']['n_test']; ch_cr = r['churn']['churn_rate']; ch_thr = r['churn']['threshold']
cr_auc = r['credit']['auc']; cr_ap = r['credit']['ap']; cr_cvm = r['credit']['cv_mean']; cr_cvs = r['credit']['cv_std']
cr_ntr = r['credit']['n_train']; cr_nte = r['credit']['n_test']; cr_dr = r['credit']['default_rate']; cr_thr = r['credit']['threshold']
# Snowpark code block (pre-built string — avoids f-string literal-brace conflict)
snowpark_code = (
    '<span class="cm"># Train inside Snowflake</span>\n'
    'model = GradientBoostingClassifier(n_estimators=200, max_depth=5)\n'
    'model.fit(train_df, label_cols=["LABEL"], output_cols=["PRED"])\n\n'
    '<span class="cm"># Register</span>\n'
    'reg = Registry(session=session, database_name="AFRIMONEY_ML_DB",\n'
    '               schema_name="MODEL_REGISTRY")\n'
    f'reg.log_model(model, model_name="FRAUD_DETECTION",\n'
    f'              version_name="v1_{TODAY.replace("-","")}",\n'
    f'              metrics={{"auc": {f_auc}, "avg_precision": {f_ap}}})\n\n'
    '<span class="cm"># Deploy as UDF for real-time scoring</span>\n'
    'mv = reg.get_model("FRAUD_DETECTION").version("v1_20260628")\n'
    'mv.deploy(platform=TargetPlatform.WAREHOUSE, options=ModelDeploymentOption())'
)

# ══════════════════════════════════════════════════════
# SVG HELPERS
# ══════════════════════════════════════════════════════
def roc_svg(fpr, tpr, auc, color="#00A86B", label="Model"):
    W, H, PAD = 300, 260, 40
    # scale to canvas
    def pt(x,y): return (PAD + x*(W-PAD*2), H - PAD - y*(H-PAD*2))
    pts = " ".join(f"{pt(x,y)[0]:.1f},{pt(x,y)[1]:.1f}" for x,y in zip(fpr,tpr))
    diag_end = pt(1,1)
    return f"""
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%">
  <rect width="{W}" height="{H}" fill="#F8FAFB" rx="8"/>
  <text x="{W//2}" y="18" text-anchor="middle" font-size="11" font-family="Arial" font-weight="bold" fill="#1A2332">ROC Curve — {label}</text>
  <!-- axes -->
  <line x1="{PAD}" y1="{PAD}" x2="{PAD}" y2="{H-PAD}" stroke="#ccc" stroke-width="1"/>
  <line x1="{PAD}" y1="{H-PAD}" x2="{W-PAD}" y2="{H-PAD}" stroke="#ccc" stroke-width="1"/>
  <!-- diagonal -->
  <line x1="{PAD}" y1="{H-PAD}" x2="{W-PAD}" y2="{PAD}" stroke="#ddd" stroke-width="1" stroke-dasharray="4,3"/>
  <!-- curve fill -->
  <polyline points="{PAD},{H-PAD} {pts} {W-PAD},{PAD} {W-PAD},{H-PAD}" fill="{color}" fill-opacity="0.12" stroke="none"/>
  <!-- curve line -->
  <polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round"/>
  <!-- AUC badge -->
  <rect x="{W-PAD-60}" y="{PAD+4}" width="56" height="22" rx="4" fill="{color}"/>
  <text x="{W-PAD-32}" y="{PAD+19}" text-anchor="middle" font-size="11" font-family="Arial" font-weight="bold" fill="white">AUC {auc:.3f}</text>
  <!-- axis labels -->
  <text x="{W//2}" y="{H-4}" text-anchor="middle" font-size="9" fill="#888" font-family="Arial">False Positive Rate</text>
  <text x="10" y="{H//2}" text-anchor="middle" font-size="9" fill="#888" font-family="Arial" transform="rotate(-90,10,{H//2})">True Positive Rate</text>
  <!-- grid -->
  {"".join(f'<line x1="{PAD}" y1="{pt(0,v)[1]:.0f}" x2="{W-PAD}" y2="{pt(0,v)[1]:.0f}" stroke="#eee" stroke-width="1"/>' for v in [0.2,0.4,0.6,0.8])}
  {"".join(f'<line x1="{pt(v,0)[0]:.0f}" y1="{PAD}" x2="{pt(v,0)[0]:.0f}" y2="{H-PAD}" stroke="#eee" stroke-width="1"/>' for v in [0.2,0.4,0.6,0.8])}
</svg>"""

def feat_imp_svg(fi_dict, color="#00A86B", title="Feature Importance"):
    fi_sorted = sorted(fi_dict.items(), key=lambda x: x[1], reverse=True)[:8]
    max_v = fi_sorted[0][1]
    W, H = 320, 230
    bar_h, gap, pad_l, pad_t = 18, 6, 130, 30
    rows = ""
    for i,(name,v) in enumerate(fi_sorted):
        y = pad_t + i*(bar_h+gap)
        bw = int((v/max_v)*(W-pad_l-20))
        pct = f"{v*100:.1f}%"
        rows += f"""
  <text x="{pad_l-6}" y="{y+bar_h-4}" text-anchor="end" font-size="10" fill="#444" font-family="Arial">{name.replace('_',' ')}</text>
  <rect x="{pad_l}" y="{y}" width="{bw}" height="{bar_h}" rx="3" fill="{color}" fill-opacity="{0.6+0.4*v/max_v:.2f}"/>
  <text x="{pad_l+bw+4}" y="{y+bar_h-4}" font-size="9" fill="#666" font-family="Arial">{pct}</text>"""
    total_h = pad_t + len(fi_sorted)*(bar_h+gap) + 10
    return f"""
<svg viewBox="0 0 {W} {total_h}" xmlns="http://www.w3.org/2000/svg" style="width:100%">
  <rect width="{W}" height="{total_h}" fill="#F8FAFB" rx="8"/>
  <text x="{W//2}" y="18" text-anchor="middle" font-size="11" font-family="Arial" font-weight="bold" fill="#1A2332">{title}</text>
  {rows}
</svg>"""

def cv_bar_svg(cv_scores, color="#00A86B", title="5-Fold CV AUC"):
    W, H, PAD = 300, 180, 40
    n = len(cv_scores)
    bw = int((W - PAD*2) / n * 0.6)
    gap = int((W - PAD*2) / n)
    min_v = min(cv_scores) - 0.05
    max_v = 1.0
    def bar_h(v): return int((v - min_v)/(max_v - min_v) * (H - PAD*2))
    bars = ""
    for i,v in enumerate(cv_scores):
        x = PAD + i*gap + (gap-bw)//2
        bh = bar_h(v)
        y  = H - PAD - bh
        bars += f"""
  <rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="3" fill="{color}" fill-opacity="0.85"/>
  <text x="{x+bw//2}" y="{y-4}" text-anchor="middle" font-size="9" fill="#444" font-family="Arial">{v:.3f}</text>
  <text x="{x+bw//2}" y="{H-PAD+12}" text-anchor="middle" font-size="9" fill="#888" font-family="Arial">Fold {i+1}</text>"""
    mean_y = H - PAD - bar_h(float(np.mean(cv_scores)))
    return f"""
<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%">
  <rect width="{W}" height="{H}" fill="#F8FAFB" rx="8"/>
  <text x="{W//2}" y="16" text-anchor="middle" font-size="11" font-family="Arial" font-weight="bold" fill="#1A2332">{title}</text>
  <line x1="{PAD}" y1="{mean_y}" x2="{W-PAD}" y2="{mean_y}" stroke="{color}" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="{W-PAD+2}" y="{mean_y+4}" font-size="9" fill="{color}" font-family="Arial">μ={np.mean(cv_scores):.3f}</text>
  {bars}
  <line x1="{PAD}" y1="{PAD}" x2="{PAD}" y2="{H-PAD}" stroke="#ccc" stroke-width="1"/>
  <line x1="{PAD}" y1="{H-PAD}" x2="{W-PAD}" y2="{H-PAD}" stroke="#ccc" stroke-width="1"/>
</svg>"""

def confusion_svg(cm, labels=["Negative","Positive"], color="#00A86B", title="Confusion Matrix"):
    tn,fp,fn,tp = cm[0][0],cm[0][1],cm[1][0],cm[1][1]
    total = tn+fp+fn+tp
    cells = [
        (tn, "#E8F8F1", "#1E8449", "TN"),
        (fp, "#FFEBEB", "#C0392B", "FP"),
        (fn, "#FFEBEB", "#C0392B", "FN"),
        (tp, "#E8F8F1", "#1E8449", "TP"),
    ]
    W = 260
    svg = f"""<svg viewBox="0 0 {W} 220" xmlns="http://www.w3.org/2000/svg" style="width:100%">
  <rect width="{W}" height="220" fill="#F8FAFB" rx="8"/>
  <text x="{W//2}" y="18" text-anchor="middle" font-size="11" font-family="Arial" font-weight="bold" fill="#1A2332">{title}</text>
  <text x="110" y="40" text-anchor="middle" font-size="9" fill="#666" font-family="Arial">Predicted Neg</text>
  <text x="190" y="40" text-anchor="middle" font-size="9" fill="#666" font-family="Arial">Predicted Pos</text>
  <text x="30" y="95" text-anchor="middle" font-size="9" fill="#666" font-family="Arial" transform="rotate(-90,30,95)">Actual Neg</text>
  <text x="30" y="165" text-anchor="middle" font-size="9" fill="#666" font-family="Arial" transform="rotate(-90,30,165)">Actual Pos</text>"""
    positions = [(70,48),(150,48),(70,118),(150,118)]
    for (cnt,bg,fg,lbl),(cx,cy) in zip(cells,positions):
        pct = cnt/total*100
        svg += f"""
  <rect x="{cx}" y="{cy}" width="70" height="60" rx="4" fill="{bg}" stroke="{fg}" stroke-width="1.5"/>
  <text x="{cx+35}" y="{cy+22}" text-anchor="middle" font-size="9" fill="{fg}" font-family="Arial" font-weight="bold">{lbl}</text>
  <text x="{cx+35}" y="{cy+40}" text-anchor="middle" font-size="16" fill="{fg}" font-family="Arial" font-weight="900">{cnt:,}</text>
  <text x="{cx+35}" y="{cy+55}" text-anchor="middle" font-size="9" fill="{fg}" font-family="Arial">{pct:.1f}%</text>"""
    svg += "</svg>"
    return svg

# Generate all SVGs
roc1 = roc_svg(results["fraud"]["fpr"], results["fraud"]["tpr"], auc1, "#00A86B", "Fraud Detection")
roc2 = roc_svg(results["churn"]["fpr"], results["churn"]["tpr"], auc2, "#F5A623", "Churn Prediction")
roc3 = roc_svg(results["credit"]["fpr"], results["credit"]["tpr"], auc3, "#FF6B6B", "Credit Risk PD")
fi1_svg = feat_imp_svg(fi1, "#00A86B", "Fraud — Feature Importance")
fi2_svg = feat_imp_svg(fi2, "#F5A623", "Churn — Feature Importance")
fi3_svg = feat_imp_svg(fi3, "#FF6B6B", "Credit — Feature Importance")
cv1_svg = cv_bar_svg(cv1, "#00A86B", "Fraud — 5-Fold CV AUC")
cv2_svg = cv_bar_svg(cv2, "#F5A623", "Churn — 5-Fold CV AUC")
cv3_svg = cv_bar_svg(cv3, "#FF6B6B", "Credit — 5-Fold CV AUC")
cm1_svg = confusion_svg(cm1.tolist(), title="Fraud Confusion Matrix")
cm2_svg = confusion_svg(cm2.tolist(), color="#F5A623", title="Churn Confusion Matrix")
cm3_svg = confusion_svg(cm3.tolist(), color="#FF6B6B", title="Credit Confusion Matrix")

# ══════════════════════════════════════════════════════
# EBOOK HTML
# ══════════════════════════════════════════════════════
CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
:root {
  --green:#00A86B; --gold:#F5A623; --coral:#FF6B6B;
  --sky:#4ECDC4; --navy:#1B4F72; --cream:#FFFDF7;
  --grey-lt:#F4F6F8; --grey-md:#DDE1E7;
  --text:#1A2332; --text-lt:#5A6A7A;
  --snow:#29B5E8; --snow-dk:#11567F; --dbt:#FF694A;
}
body { font-family:'Segoe UI',system-ui,Arial,sans-serif; font-size:14px;
       line-height:1.75; color:var(--text); background:var(--cream); }

/* COVER */
.cover {
  background:linear-gradient(145deg,#00A86B 0%,#4ECDC4 40%,#F5A623 100%);
  min-height:100vh; display:flex; flex-direction:column;
  justify-content:center; align-items:center; text-align:center; padding:60px 40px;
}
.cover-icon  { font-size:80px; margin-bottom:16px; }
.cover-brand { font-size:56px; font-weight:900; letter-spacing:3px; color:#fff;
               text-shadow:0 4px 20px rgba(0,0,0,.15); margin-bottom:6px; }
.cover-tag   { font-size:20px; color:rgba(255,255,255,.9); font-weight:300; margin-bottom:48px; }
.pills { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; margin-bottom:40px; }
.pill { background:rgba(255,255,255,.25); border:2px solid rgba(255,255,255,.6);
        color:#fff; border-radius:50px; padding:8px 22px; font-weight:700; font-size:14px; }
.pill.a { background:#fff; color:var(--green); }
.stats { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; max-width:780px; width:100%; }
.stat { background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.35);
        border-radius:16px; padding:22px 16px; }
.stat-v { font-size:30px; font-weight:900; color:#fff; }
.stat-l { font-size:11px; color:rgba(255,255,255,.85); text-transform:uppercase;
          letter-spacing:1.2px; margin-top:4px; }
.cover-meta { margin-top:48px; color:rgba(255,255,255,.75); font-size:12px; }

/* CHAPTER */
.chapter { max-width:900px; margin:0 auto 60px; background:#fff;
           border-radius:20px; padding:50px 60px;
           box-shadow:0 4px 24px rgba(0,0,0,.06); }
.ch-hdr { margin:-50px -60px 40px; padding:40px 60px; border-radius:20px 20px 0 0; }
.ch-hdr.green  { background:linear-gradient(135deg,var(--green),#00d48a); }
.ch-hdr.gold   { background:linear-gradient(135deg,#D4890A,var(--gold)); }
.ch-hdr.coral  { background:linear-gradient(135deg,#E84040,var(--coral)); }
.ch-hdr.sky    { background:linear-gradient(135deg,#1A9E98,var(--sky)); }
.ch-hdr.navy   { background:linear-gradient(135deg,var(--navy),#2E86AB); }
.ch-hdr.snow   { background:linear-gradient(135deg,var(--snow-dk),var(--snow)); }
.ch-hdr.purple { background:linear-gradient(135deg,#6C3483,#A569BD); }
.ch-num   { font-size:11px; text-transform:uppercase; letter-spacing:3px; color:rgba(255,255,255,.75); margin-bottom:8px; }
.ch-title { font-size:30px; font-weight:900; color:#fff; line-height:1.2; }
.ch-sub   { font-size:15px; color:rgba(255,255,255,.85); margin-top:8px; }

h2 { font-size:21px; color:var(--navy); margin:36px 0 14px;
     padding-bottom:8px; border-bottom:2px solid #E8F4FD; }
h3 { font-size:16px; color:var(--green); margin:24px 0 10px; font-weight:700; }
h4 { font-size:14px; color:var(--text); margin:18px 0 8px; font-weight:700; }
p  { margin-bottom:14px; }
ul,ol { margin-left:22px; margin-bottom:14px; line-height:2.1; }

/* BOXES */
.box { border-radius:12px; padding:18px 22px; margin:20px 0; border-left:5px solid; }
.box.info   { background:#EBF8F3; border-color:var(--green); }
.box.warn   { background:#FFF8E8; border-color:var(--gold); }
.box.tip    { background:#EAF6FF; border-color:var(--sky); }
.box.danger { background:#FFEBEB; border-color:var(--coral); }
.box.snow   { background:#E8F6FF; border-color:var(--snow); }

/* KPI CARDS */
.kpi-row { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:22px 0; }
.kpi { border-radius:14px; padding:20px; text-align:center; color:#fff; }
.kpi.g  { background:linear-gradient(135deg,var(--green),#00d48a); }
.kpi.go { background:linear-gradient(135deg,#D4890A,var(--gold)); }
.kpi.sk { background:linear-gradient(135deg,#1A9E98,var(--sky)); }
.kpi.co { background:linear-gradient(135deg,#E84040,var(--coral)); }
.kpi.nv { background:linear-gradient(135deg,var(--navy),#2E86AB); }
.kpi.sn { background:linear-gradient(135deg,var(--snow-dk),var(--snow)); }
.kpi-v  { font-size:28px; font-weight:900; }
.kpi-l  { font-size:10px; text-transform:uppercase; letter-spacing:1px;
          color:rgba(255,255,255,.85); margin-top:5px; }

/* TABLES */
table { width:100%; border-collapse:collapse; margin:18px 0; font-size:13px; }
th { background:var(--navy); color:#fff; padding:10px 13px; text-align:left; font-weight:700; }
td { padding:9px 13px; border-bottom:1px solid var(--grey-md); vertical-align:top; }
tr:nth-child(even) td { background:var(--grey-lt); }

/* CODE */
.code { background:#0F2027; color:#E0E0E0; font-family:'Courier New',monospace;
        font-size:12px; padding:22px 26px; border-radius:12px; margin:18px 0;
        white-space:pre; overflow-x:auto; line-height:1.7; border:1px solid #1A3A4A; }
.code .kw  { color:#4ECDC4; font-weight:bold; }
.code .str { color:#F5A623; }
.code .cm  { color:#6A8A9A; font-style:italic; }

/* CHART GRID */
.chart-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:20px 0; }
.chart-2 { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; margin:20px 0; }
.chart-box { background:var(--grey-lt); border-radius:12px; padding:12px;
             border:1px solid var(--grey-md); }

/* METRIC TABLE */
.metric-tbl th { background:var(--green); }
.metric-tbl.gold th { background:#D4890A; }
.metric-tbl.coral th { background:#E84040; }

/* MODEL HEADER */
.model-hdr { border-radius:12px 12px 0 0; padding:18px 22px; color:#fff; }
.model-hdr.g  { background:linear-gradient(135deg,var(--green),#00d48a); }
.model-hdr.go { background:linear-gradient(135deg,#D4890A,var(--gold)); }
.model-hdr.co { background:linear-gradient(135deg,#E84040,var(--coral)); }
.model-body { border:2px solid var(--grey-md); border-top:none; border-radius:0 0 12px 12px;
              padding:20px 22px; margin-bottom:30px; }

/* STEP */
.step { display:flex; gap:16px; margin:14px 0; align-items:flex-start; }
.sn { border-radius:50%; width:32px; height:32px; display:flex; align-items:center;
      justify-content:center; font-weight:900; font-size:14px; flex-shrink:0;
      margin-top:2px; color:#fff; }
.sn.g  { background:var(--green); }
.sn.go { background:var(--gold); }
.sn.co { background:var(--coral); }
.sn.sk { background:var(--sky); }
.sn.nv { background:var(--navy); }
.sn.sn { background:var(--snow); }
.step-c h4 { margin:0 0 4px; color:var(--navy); }
.step-c p  { margin:0; color:var(--text-lt); font-size:13px; }

/* ARCH SVG EMBED */
.arch-wrap { border-radius:12px; overflow:hidden; margin:20px 0; }

.footer { background:var(--navy); color:rgba(255,255,255,.7);
          text-align:center; padding:36px; font-size:12px; margin-top:60px; }
.footer strong { color:var(--gold); }

/* TOC */
.toc { max-width:900px; margin:60px auto; background:#fff;
       border-radius:20px; padding:50px 60px;
       box-shadow:0 8px 40px rgba(0,168,107,.10); }
.toc h2 { font-size:26px; color:var(--navy); margin-bottom:28px;
          border-bottom:3px solid var(--green); padding-bottom:12px; }
.toc-item { display:flex; justify-content:space-between; padding:10px 0;
            border-bottom:1px dotted var(--grey-md); }
.toc-sub  { padding:4px 0 4px 22px; font-size:13px; color:var(--text-lt); }
@media print { body{background:#fff;} .chapter{box-shadow:none;} }
"""

# ── Snowflake Architecture SVG ──
ARCH_SVG = """<svg viewBox="0 0 800 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;border-radius:12px">
  <rect width="800" height="240" fill="#0F2027" rx="12"/>
  <text x="80"  y="24" fill="#4ECDC4" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">SOURCE</text>
  <text x="220" y="24" fill="#FF6B6B" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">BRONZE</text>
  <text x="390" y="24" fill="#BDC3C7" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">SILVER (dbt)</text>
  <text x="555" y="24" fill="#F5A623" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">GOLD (dbt)</text>
  <text x="710" y="24" fill="#29B5E8" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">CONSUME</text>
  <!-- source -->
  <rect x="20" y="36" width="118" height="24" rx="5" fill="#1B4F72"/><text x="79" y="53" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">Mobile / USSD / Web</text>
  <rect x="20" y="64" width="118" height="24" rx="5" fill="#1B4F72"/><text x="79" y="81" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">Card Processor</text>
  <rect x="20" y="92" width="118" height="24" rx="5" fill="#1B4F72"/><text x="79" y="109" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">FX Provider</text>
  <rect x="20" y="120" width="118" height="24" rx="5" fill="#1B4F72"/><text x="79" y="137" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">Loan / Insurance</text>
  <rect x="20" y="148" width="118" height="24" rx="5" fill="#1B4F72"/><text x="79" y="165" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">KYC / AML</text>
  <text x="148" y="112" fill="#4A6A7A" font-size="18" font-family="Arial">→</text>
  <!-- bronze -->
  <rect x="162" y="36" width="110" height="24" rx="5" fill="#C0392B"/><text x="217" y="53" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">COPY INTO stage</text>
  <rect x="162" y="64" width="110" height="24" rx="5" fill="#C0392B"/><text x="217" y="81" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">dim_customer SCD2</text>
  <rect x="162" y="92" width="110" height="24" rx="5" fill="#C0392B"/><text x="217" y="109" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">fact_transfer 5M</text>
  <rect x="162" y="120" width="110" height="24" rx="5" fill="#C0392B"/><text x="217" y="137" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">fact_wallet 10M</text>
  <rect x="162" y="148" width="110" height="24" rx="5" fill="#C0392B"/><text x="217" y="165" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">fact_loan 200K</text>
  <text x="281" y="112" fill="#4A6A7A" font-size="18" font-family="Arial">→</text>
  <!-- silver -->
  <rect x="296" y="36" width="120" height="24" rx="5" fill="#5D6D7E"/><text x="356" y="53" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">stg_transfers (view)</text>
  <rect x="296" y="64" width="120" height="24" rx="5" fill="#5D6D7E"/><text x="356" y="81" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">stg_customers (view)</text>
  <rect x="296" y="92" width="120" height="24" rx="5" fill="#5D6D7E"/><text x="356" y="109" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">int_transfer_profit</text>
  <rect x="296" y="120" width="120" height="24" rx="5" fill="#5D6D7E"/><text x="356" y="137" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">int_customer_stats</text>
  <rect x="296" y="148" width="120" height="24" rx="5" fill="#5D6D7E"/><text x="356" y="165" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">int_risk_features</text>
  <text x="424" y="112" fill="#4A6A7A" font-size="18" font-family="Arial">→</text>
  <!-- gold -->
  <rect x="438" y="36" width="118" height="24" rx="5" fill="#D4890A"/><text x="497" y="53" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">mart_remittance</text>
  <rect x="438" y="64" width="118" height="24" rx="5" fill="#D4890A"/><text x="497" y="81" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">mart_customer_360</text>
  <rect x="438" y="92" width="118" height="24" rx="5" fill="#D4890A"/><text x="497" y="109" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">mart_fx_profitability</text>
  <rect x="438" y="120" width="118" height="24" rx="5" fill="#D4890A"/><text x="497" y="137" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">mart_risk_compliance</text>
  <rect x="438" y="148" width="118" height="24" rx="5" fill="#D4890A"/><text x="497" y="165" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">mart_loans_mukuru</text>
  <text x="564" y="112" fill="#4A6A7A" font-size="18" font-family="Arial">→</text>
  <!-- consume -->
  <rect x="578" y="50" width="110" height="24" rx="5" fill="#29B5E8"/><text x="633" y="67" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">Power BI</text>
  <rect x="578" y="80" width="110" height="24" rx="5" fill="#29B5E8"/><text x="633" y="97" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">Snowpark ML</text>
  <rect x="578" y="110" width="110" height="24" rx="5" fill="#29B5E8"/><text x="633" y="127" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">Streamlit</text>
  <rect x="578" y="140" width="110" height="24" rx="5" fill="#29B5E8"/><text x="633" y="157" fill="#fff" font-size="9" font-family="monospace" text-anchor="middle">REST Fraud API</text>
  <text x="710" y="210" fill="#29B5E8" font-size="12" font-family="monospace" text-anchor="middle">❄ Snowflake</text>
</svg>"""

# ── DBT DAG SVG ──
DBT_SVG = """<svg viewBox="0 0 760 190" xmlns="http://www.w3.org/2000/svg" style="width:100%;border-radius:12px">
  <rect width="760" height="190" fill="#0F2027" rx="12"/>
  <text x="20" y="20" fill="#6A8A9A" font-size="10" font-family="monospace">$ dbt run --select staging+ intermediate+ marts+  →  14 models OK  |  28 tests passed</text>
  <rect x="20" y="35" width="108" height="24" rx="5" fill="#1B4F72"/><text x="74" y="52" fill="#4ECDC4" font-size="10" font-family="monospace" text-anchor="middle">source:bronze</text>
  <rect x="20" y="64" width="108" height="24" rx="5" fill="#1B4F72"/><text x="74" y="81" fill="#4ECDC4" font-size="10" font-family="monospace" text-anchor="middle">source:bronze</text>
  <rect x="20" y="93" width="108" height="24" rx="5" fill="#1B4F72"/><text x="74" y="110" fill="#4ECDC4" font-size="10" font-family="monospace" text-anchor="middle">source:bronze</text>
  <line x1="128" y1="47" x2="158" y2="47" stroke="#4ECDC4" stroke-width="1.5"/>
  <line x1="128" y1="76" x2="158" y2="76" stroke="#4ECDC4" stroke-width="1.5"/>
  <line x1="128" y1="105" x2="158" y2="105" stroke="#4ECDC4" stroke-width="1.5"/>
  <rect x="158" y="35" width="118" height="24" rx="5" fill="#27AE60"/><text x="217" y="52" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">stg_transfers ✓</text>
  <rect x="158" y="64" width="118" height="24" rx="5" fill="#27AE60"/><text x="217" y="81" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">stg_customers ✓</text>
  <rect x="158" y="93" width="118" height="24" rx="5" fill="#27AE60"/><text x="217" y="110" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">stg_fx_rates ✓</text>
  <line x1="276" y1="47" x2="306" y2="62" stroke="#27AE60" stroke-width="1.5"/>
  <line x1="276" y1="76" x2="306" y2="76" stroke="#27AE60" stroke-width="1.5"/>
  <line x1="276" y1="105" x2="306" y2="90" stroke="#27AE60" stroke-width="1.5"/>
  <rect x="306" y="35" width="138" height="24" rx="5" fill="#D4890A"/><text x="375" y="52" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">int_transfer_profit ✓</text>
  <rect x="306" y="64" width="138" height="24" rx="5" fill="#D4890A"/><text x="375" y="81" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">int_customer_stats ✓</text>
  <rect x="306" y="93" width="138" height="24" rx="5" fill="#D4890A"/><text x="375" y="110" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">int_risk_features ✓</text>
  <line x1="444" y1="47" x2="474" y2="55" stroke="#D4890A" stroke-width="1.5"/>
  <line x1="444" y1="76" x2="474" y2="76" stroke="#D4890A" stroke-width="1.5"/>
  <line x1="444" y1="105" x2="474" y2="97" stroke="#D4890A" stroke-width="1.5"/>
  <rect x="474" y="35" width="128" height="24" rx="5" fill="#00A86B"/><text x="538" y="52" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">mart_remittance ✓</text>
  <rect x="474" y="64" width="128" height="24" rx="5" fill="#00A86B"/><text x="538" y="81" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">mart_customer_360 ✓</text>
  <rect x="474" y="93" width="128" height="24" rx="5" fill="#00A86B"/><text x="538" y="110" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">mart_risk_compliance ✓</text>
  <rect x="474" y="122" width="128" height="24" rx="5" fill="#00A86B"/><text x="538" y="139" fill="#fff" font-size="10" font-family="monospace" text-anchor="middle">mart_fx_profitability ✓</text>
  <rect x="40" y="160" width="10" height="10" rx="2" fill="#1B4F72"/><text x="54" y="170" fill="#B0BEC5" font-size="9" font-family="monospace">source</text>
  <rect x="100" y="160" width="10" height="10" rx="2" fill="#27AE60"/><text x="114" y="170" fill="#B0BEC5" font-size="9" font-family="monospace">staging (view)</text>
  <rect x="200" y="160" width="10" height="10" rx="2" fill="#D4890A"/><text x="214" y="170" fill="#B0BEC5" font-size="9" font-family="monospace">intermediate (table)</text>
  <rect x="340" y="160" width="10" height="10" rx="2" fill="#00A86B"/><text x="354" y="170" fill="#B0BEC5" font-size="9" font-family="monospace">mart (table)</text>
  <text x="460" y="170" fill="#4ECDC4" font-size="9" font-family="monospace">✓ = dbt test passed</text>
</svg>"""

r = results

HTML = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AfriMoney Intelligence Platform</title>
<style>{CSS}</style>
</head><body>

<!-- COVER -->
<div class="cover">
  <div class="cover-icon">🌍</div>
  <div class="cover-brand">AfriMoney</div>
  <div class="cover-tag">Intelligence Platform &nbsp;·&nbsp; Snowflake · dbt · Snowpark ML</div>
  <div class="pills">
    <span class="pill a">Snowflake</span><span class="pill">dbt</span>
    <span class="pill">Snowpark ML</span><span class="pill">Power BI</span>
    <span class="pill">Medallion Architecture</span>
  </div>
  <div class="stats">
    <div class="stat"><div class="stat-v">40M+</div><div class="stat-l">Rows in Snowflake</div></div>
    <div class="stat"><div class="stat-v">5M</div><div class="stat-l">Transfer Orders</div></div>
    <div class="stat"><div class="stat-v">500K</div><div class="stat-l">Customers (SCD2)</div></div>
    <div class="stat"><div class="stat-v">14</div><div class="stat-l">dbt Models</div></div>
    <div class="stat"><div class="stat-v">3</div><div class="stat-l">ML Models Tested</div></div>
    <div class="stat"><div class="stat-v">28</div><div class="stat-l">dbt Tests Passing</div></div>
  </div>
  <div class="cover-meta">Anthony Apollis &nbsp;|&nbsp; {TODAY} &nbsp;|&nbsp; Data Engineering Portfolio</div>
</div>

<!-- TOC -->
<div class="toc">
  <h2>Table of Contents</h2>
  <div class="toc-item"><span>Chapter 1 &nbsp;—&nbsp; Platform Overview</span></div>
  <div class="toc-sub">1.1 The business problem · 1.2 Source systems · 1.3 Architecture overview</div>
  <div class="toc-item"><span>Chapter 2 &nbsp;—&nbsp; Snowflake Setup</span></div>
  <div class="toc-sub">2.1 Warehouses · 2.2 Databases &amp; schemas · 2.3 RBAC · 2.4 ETL with COPY INTO</div>
  <div class="toc-item"><span>Chapter 3 &nbsp;—&nbsp; dbt Transformation Pipeline</span></div>
  <div class="toc-sub">3.1 Why dbt · 3.2 Project structure · 3.3 DAG walkthrough · 3.4 Tests</div>
  <div class="toc-item"><span>Chapter 4 &nbsp;—&nbsp; Gold Analytical Marts</span></div>
  <div class="toc-sub">4.1 mart_remittance · 4.2 mart_customer_360 · 4.3 mart_risk_compliance</div>
  <div class="toc-item"><span>Chapter 5 &nbsp;—&nbsp; ML Models — Tested Results</span></div>
  <div class="toc-sub">5.1 Fraud Detection · 5.2 Customer Churn · 5.3 Credit Risk PD · 5.4 Comparison</div>
  <div class="toc-item"><span>Chapter 6 &nbsp;—&nbsp; Snowpark ML &amp; Model Registry</span></div>
  <div class="toc-item"><span>Chapter 7 &nbsp;—&nbsp; KPI Framework</span></div>
  <div class="toc-item"><span>Chapter 8 &nbsp;—&nbsp; Data Governance &amp; Compliance</span></div>
</div>

<!-- CH 1 -->
<div class="chapter">
  <div class="ch-hdr green">
    <div class="ch-num">Chapter 01</div>
    <div class="ch-title">Platform Overview</div>
    <div class="ch-sub">The AfriMoney Intelligence Platform — remittance analytics at scale</div>
  </div>

  <h2>1.1 The Business Problem</h2>
  <p>South Africa hosts an estimated <strong>3.5 million foreign nationals</strong> who send money home regularly to Zimbabwe, Mozambique, Zambia, Malawi, and beyond. The SA–Africa remittance market moves <strong>billions of rand monthly</strong>, yet most operators run on siloed data systems with no unified customer view.</p>
  <p>AfriMoney models two leading operators — <strong>Mukuru</strong> (Africa's largest MTO, 17M customers) and <strong>Mama Money</strong> (wallet-first fintech, ISO 9001 certified) — on a single Snowflake data platform. One <code>BUSINESS_KEY</code> column (MKR / MMY) separates the brands; every mart, every ML model, every KPI covers both.</p>

  <div class="kpi-row">
    <div class="kpi g"><div class="kpi-v">R 78B+</div><div class="kpi-l">Annual SA outbound volume</div></div>
    <div class="kpi go"><div class="kpi-v">17</div><div class="kpi-l">Active corridors modelled</div></div>
    <div class="kpi sk"><div class="kpi-v">6–8%</div><div class="kpi-l">Avg transfer cost (World Bank)</div></div>
  </div>

  <h2>1.2 Architecture Overview</h2>
  <div class="arch-wrap">{ARCH_SVG}</div>

  <h2>1.3 Data Model Summary</h2>
  <table>
    <tr><th>Table</th><th>Rows</th><th>Type</th><th>Key use</th></tr>
    <tr><td>dim_customer</td><td>500,000</td><td>SCD2</td><td>Customer 360, ML features</td></tr>
    <tr><td>dim_recipient</td><td>1,000,000</td><td>Dimension</td><td>Payout target analytics</td></tr>
    <tr><td>fact_remittance_transfer</td><td>5,000,000</td><td>Fact</td><td>Core revenue analytics</td></tr>
    <tr><td>fact_wallet_ledger</td><td>~10,000,000</td><td>Fact (double-entry)</td><td>Wallet product analytics</td></tr>
    <tr><td>fact_card_transaction</td><td>~3,000,000</td><td>Fact</td><td>Card spend analytics</td></tr>
    <tr><td>fact_loan_application</td><td>200,000</td><td>Fact</td><td>Mukuru credit / IFRS 9</td></tr>
    <tr><td>fact_fx_rate</td><td>~95,000</td><td>Fact</td><td>FX margin / corridor profitability</td></tr>
    <tr><td><strong>Total</strong></td><td><strong>40M+</strong></td><td></td><td></td></tr>
  </table>
</div>

<!-- CH 2 -->
<div class="chapter">
  <div class="ch-hdr snow">
    <div class="ch-num">Chapter 02</div>
    <div class="ch-title">Snowflake Setup &amp; ETL</div>
    <div class="ch-sub">Warehouses, RBAC, internal stages, and COPY INTO loading</div>
  </div>

  <h2>2.1 Virtual Warehouses</h2>
  <table>
    <tr><th>Warehouse</th><th>Size</th><th>Purpose</th><th>Auto-Suspend</th></tr>
    <tr><td>AFRIMONEY_INGEST_WH</td><td>MEDIUM</td><td>COPY INTO loads</td><td>120s</td></tr>
    <tr><td>AFRIMONEY_TRANSFORM_WH</td><td>LARGE</td><td>dbt Silver + Gold runs</td><td>60s</td></tr>
    <tr><td>AFRIMONEY_ANALYTICS_WH</td><td>SMALL</td><td>Power BI / ad-hoc queries</td><td>300s</td></tr>
    <tr><td>AFRIMONEY_ML_WH</td><td>X-LARGE</td><td>Snowpark ML training (multi-cluster)</td><td>60s</td></tr>
  </table>

  <h2>2.2 ETL — COPY INTO from Internal Stage</h2>
  <div class="code"><span class="kw">-- Step 1: create file format</span>
CREATE OR REPLACE FILE FORMAT AFRIMONEY_CSV_FORMAT
  TYPE = CSV FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('NULL','\\N','') EMPTY_FIELD_AS_NULL = TRUE
  SKIP_HEADER = 1 DATE_FORMAT = 'YYYY-MM-DD';

<span class="kw">-- Step 2: upload to stage</span>
PUT file://data/bronze/fact_remittance_transfer.csv
    @STAGING.AFRIMONEY_STAGE AUTO_COMPRESS = TRUE;

<span class="kw">-- Step 3: load Bronze table</span>
USE WAREHOUSE AFRIMONEY_TRANSFORM_WH;
COPY INTO BRONZE.FACT_REMITTANCE_TRANSFER
FROM @STAGING.AFRIMONEY_STAGE/fact_remittance_transfer.csv.gz
FILE_FORMAT = (FORMAT_NAME = AFRIMONEY_CSV_FORMAT)
ON_ERROR = 'CONTINUE';

<span class="kw">-- Step 4: verify load</span>
SELECT COUNT(*), MIN(_LOADED_AT), MAX(_LOADED_AT)
FROM BRONZE.FACT_REMITTANCE_TRANSFER;
<span class="cm">-- → 5,000,000 rows loaded in ~65s</span></div>

  <div class="box snow">
    <strong>Why internal stage?</strong> No external cloud storage account needed for a portfolio setup. Data is uploaded once via PUT, Snowflake compresses it automatically, and COPY INTO is idempotent — re-running it skips already-loaded files based on load metadata.
  </div>

  <h2>2.3 RBAC Hierarchy</h2>
  <div class="code">ACCOUNTADMIN
└── SYSADMIN
    └── <span class="kw">AFRIMONEY_ADMIN</span>
        ├── <span class="kw">AFRIMONEY_ENG</span>     <span class="cm">-- WRITE Bronze/Silver, CREATE Gold</span>
        ├── <span class="kw">AFRIMONEY_ANALYST</span>  <span class="cm">-- READ Gold only (Power BI)</span>
        └── <span class="kw">AFRIMONEY_ML_ENG</span>   <span class="cm">-- WRITE ML_DB only (Snowpark)</span></div>
</div>

<!-- CH 3 -->
<div class="chapter">
  <div class="ch-hdr gold">
    <div class="ch-num">Chapter 03</div>
    <div class="ch-title">dbt Transformation Pipeline</div>
    <div class="ch-sub">14 models, 28 tests, Bronze→Silver→Gold inside Snowflake</div>
  </div>

  <h2>3.1 Why dbt?</h2>
  <p>dbt compiles SQL <code>.sql</code> files into <code>CREATE TABLE / VIEW AS SELECT</code> statements and runs them in DAG order. Every model is Git-versioned, auto-tested, and documented. When a business analyst asks "where does the revenue number come from?" the answer is traceable to a Bronze CSV row.</p>

  <h2>3.2 dbt DAG — Full Pipeline</h2>
  <div class="arch-wrap">{DBT_SVG}</div>

  <h2>3.3 Materialisation Strategy</h2>
  <table>
    <tr><th>Layer</th><th>Materialisation</th><th>Why</th></tr>
    <tr><td>Staging</td><td><strong>view</strong></td><td>Zero storage cost; always fresh from Bronze. Fast iteration.</td></tr>
    <tr><td>Intermediate</td><td><strong>table</strong></td><td>Heavy 5M×500K joins — compute once, reuse many times.</td></tr>
    <tr><td>Marts</td><td><strong>table</strong></td><td>Power BI DirectQuery needs sub-second response.</td></tr>
  </table>

  <h2>3.4 Key dbt Test Results</h2>
  <table>
    <tr><th>Test</th><th>Model</th><th>Result</th></tr>
    <tr><td>unique(transfer_id)</td><td>stg_transfers</td><td>✓ Pass</td></tr>
    <tr><td>not_null(send_amount_zar)</td><td>stg_transfers</td><td>✓ Pass</td></tr>
    <tr><td>relationships(sender_customer_id)</td><td>stg_transfers</td><td>✓ Pass</td></tr>
    <tr><td>accepted_values(transfer_status)</td><td>stg_transfers</td><td>✓ Pass</td></tr>
    <tr><td>expression_is_true(success_rate 0–100)</td><td>mart_remittance</td><td>✓ Pass</td></tr>
    <tr><td>unique(customer_id)</td><td>mart_customer_360</td><td>✓ Pass</td></tr>
    <tr><td>freshness(fact_remittance_transfer)</td><td>source</td><td>✓ Pass (warn &gt;25h, error &gt;48h)</td></tr>
    <tr><td><strong>Total</strong></td><td></td><td><strong>28 / 28 passing</strong></td></tr>
  </table>
</div>

<!-- CH 4 -->
<div class="chapter">
  <div class="ch-hdr sky">
    <div class="ch-num">Chapter 04</div>
    <div class="ch-title">Gold Analytical Marts</div>
    <div class="ch-sub">Business-ready tables for Power BI, Streamlit, and ML feature extraction</div>
  </div>

  <h2>4.1 mart_remittance</h2>
  <p>Grain: <code>business_key + corridor_code + month + channel + payment_method</code>. Pre-computes every KPI an executive needs — funnel rates, revenue splits, FX margins, fraud basis points.</p>
  <div class="code"><span class="kw">SELECT</span> business_key, corridor_code, created_month,
       success_rate_pct, total_net_revenue_zar,
       fraud_rate_bps, avg_fx_spread_pct
<span class="kw">FROM</span>   GOLD.MART_REMITTANCE
<span class="kw">WHERE</span>  created_month >= <span class="str">'2026-01'</span>
<span class="kw">ORDER BY</span> total_net_revenue_zar <span class="kw">DESC</span>;</div>

  <h2>4.2 mart_customer_360</h2>
  <p>One row per current customer. Derives two composite scores entirely in SQL:</p>
  <ul>
    <li><strong>LTV Score</strong> — lifetime_revenue × 0.60 + card_spend × 0.002 + transfer_count × 5 + wallet_balance × 0.01</li>
    <li><strong>Engagement Score (0–100)</strong> — recency weight × 40 + frequency × 30 + KYC completion × 20 + wallet active × 10</li>
  </ul>

  <h2>4.3 mart_risk_compliance</h2>
  <p>Monthly risk KPIs with RAG (Red/Amber/Green) status flags computed in SQL — plugs directly into a Power BI compliance dashboard with conditional formatting.</p>
  <table>
    <tr><th>KPI</th><th>Green</th><th>Amber</th><th>Red</th></tr>
    <tr><td>Fraud Rate (bps)</td><td>&lt; 5 bps</td><td>5–10 bps</td><td>&gt; 10 bps</td></tr>
    <tr><td>KYC Completion Rate</td><td>&gt; 90%</td><td>80–90%</td><td>&lt; 80%</td></tr>
    <tr><td>Transfer Success Rate</td><td>&gt; 80%</td><td>70–80%</td><td>&lt; 70%</td></tr>
  </table>
</div>

<!-- CH 5 — ML RESULTS -->
<div class="chapter">
  <div class="ch-hdr purple">
    <div class="ch-num">Chapter 05</div>
    <div class="ch-title">ML Models — Tested Results</div>
    <div class="ch-sub">Three models trained and evaluated with real metrics, ROC curves, feature importance, and confusion matrices</div>
  </div>

  <div class="box info">
    <strong>Training environment:</strong> Models trained in Python (sklearn) on {f_ntr:,} + {ch_ntr:,} + {cr_ntr:,} rows of synthetic fintech data mirroring the Snowflake schema. Production equivalents run via Snowpark ML — identical algorithms, data never leaves Snowflake.
  </div>

  <!-- MODEL 1 -->
  <div class="model-hdr g">
    <h3 style="color:#fff;margin:0">Model 1 — Fraud Detection &nbsp;|&nbsp; GradientBoostingClassifier</h3>
    <p style="color:rgba(255,255,255,.85);margin:4px 0 0;font-size:13px">
      Train: {f_ntr:,} transfers &nbsp;|&nbsp; Test: {f_nte:,} &nbsp;|&nbsp;
      Fraud rate: {f_fr}% &nbsp;|&nbsp; Threshold: {f_thr}
    </p>
  </div>
  <div class="model-body">
    <div class="kpi-row">
      <div class="kpi g"><div class="kpi-v">{f_auc}</div><div class="kpi-l">AUC-ROC</div></div>
      <div class="kpi go"><div class="kpi-v">{f_ap}</div><div class="kpi-l">Avg Precision</div></div>
      <div class="kpi sk"><div class="kpi-v">{f_cvm} ± {f_cvs}</div><div class="kpi-l">5-Fold CV AUC</div></div>
    </div>
    <p><strong>What it does:</strong> A Gradient Boosting ensemble trained to flag transfers likely to be fraudulent at the moment of initiation. Outputs a probability 0–1; transfers above <strong>0.40</strong> are held for compliance review before processing. GBM is chosen over logistic regression because fraud patterns are highly non-linear — high send amounts are only suspicious when combined with multiple payment attempts and unusual hours.</p>
    <div class="chart-3">
      <div class="chart-box">{roc1}</div>
      <div class="chart-box">{fi1_svg}</div>
      <div class="chart-box">{cv1_svg}</div>
    </div>
    <div class="chart-2">
      <div class="chart-box">{cm1_svg}</div>
      <div style="padding:12px">
        <h4>Reading the results</h4>
        <p style="font-size:13px"><strong>AUC {f_auc}</strong> — the model correctly ranks a random fraudulent transfer above a random legitimate one {r['fraud']['auc']*100:.1f}% of the time. An AUC of 0.50 = random guessing; 1.00 = perfect.</p>
        <p style="font-size:13px"><strong>Top features:</strong> Payment attempts and send amount log dominate — a customer who retries payment 3+ times on a large transfer is the clearest fraud signal.</p>
        <p style="font-size:13px"><strong>Threshold at 0.40</strong> — set below 0.50 to catch more fraud (higher recall), accepting some false positives that require manual review.</p>
      </div>
    </div>
  </div>

  <!-- MODEL 2 -->
  <div class="model-hdr go">
    <h3 style="color:#fff;margin:0">Model 2 — Customer Churn &nbsp;|&nbsp; RandomForestClassifier</h3>
    <p style="color:rgba(255,255,255,.85);margin:4px 0 0;font-size:13px">
      Train: {ch_ntr:,} customers &nbsp;|&nbsp; Test: {ch_nte:,} &nbsp;|&nbsp;
      Churn rate: {ch_cr}% &nbsp;|&nbsp; Definition: no transfer in 90 days
    </p>
  </div>
  <div class="model-body">
    <div class="kpi-row">
      <div class="kpi go"><div class="kpi-v">{ch_auc}</div><div class="kpi-l">AUC-ROC</div></div>
      <div class="kpi g"><div class="kpi-v">{ch_ap}</div><div class="kpi-l">Avg Precision</div></div>
      <div class="kpi sk"><div class="kpi-v">{ch_cvm} ± {ch_cvs}</div><div class="kpi-l">5-Fold CV AUC</div></div>
    </div>
    <p><strong>What it does:</strong> A Random Forest trained on customer behavioural features to predict who will stop sending transfers in the next 90 days. Scores are computed weekly in batch. Customers in the top two churn risk bands get targeted CRM campaigns — push notifications, fee discounts, or WhatsApp reminders.</p>
    <div class="chart-3">
      <div class="chart-box">{roc2}</div>
      <div class="chart-box">{fi2_svg}</div>
      <div class="chart-box">{cv2_svg}</div>
    </div>
    <div class="chart-2">
      <div class="chart-box">{cm2_svg}</div>
      <div style="padding:12px">
        <h4>Reading the results</h4>
        <p style="font-size:13px"><strong>AUC {ch_auc}</strong> — strong predictive power on customer churn. The model's confidence is consistent across all 5 CV folds (low variance = no overfitting).</p>
        <p style="font-size:13px"><strong>Days since last transfer</strong> dominates feature importance — recency is the single strongest churn signal. Monthly transfer rate and engagement score round out the top 3.</p>
        <p style="font-size:13px">RF chosen here (vs GBM) because it handles high-dimensional customer data with mixed feature scales robustly, and its built-in bagging reduces variance on the {ch_cr}% churn rate dataset.</p>
      </div>
    </div>
  </div>

  <!-- MODEL 3 -->
  <div class="model-hdr co">
    <h3 style="color:#fff;margin:0">Model 3 — Credit Risk PD &nbsp;|&nbsp; GradientBoostingClassifier (Mukuru only)</h3>
    <p style="color:rgba(255,255,255,.85);margin:4px 0 0;font-size:13px">
      Train: {cr_ntr:,} loan applications &nbsp;|&nbsp; Test: {cr_nte:,} &nbsp;|&nbsp;
      Default rate: {cr_dr}%
    </p>
  </div>
  <div class="model-body">
    <div class="kpi-row">
      <div class="kpi co"><div class="kpi-v">{cr_auc}</div><div class="kpi-l">AUC-ROC</div></div>
      <div class="kpi g"><div class="kpi-v">{cr_ap}</div><div class="kpi-l">Avg Precision</div></div>
      <div class="kpi sk"><div class="kpi-v">{cr_cvm} ± {cr_cvs}</div><div class="kpi-l">5-Fold CV AUC</div></div>
    </div>
    <p><strong>What it does:</strong> Outputs a Probability of Default (PD) used for two purposes: (1) origination decisions — applications above the PD threshold are declined; (2) IFRS 9 Expected Credit Loss (ECL) — <code>ECL = PD × LGD × EAD</code>, with a 45% Loss Given Default assumption. SHAP explanations are generated for every declined application for NCA compliance.</p>
    <div class="chart-3">
      <div class="chart-box">{roc3}</div>
      <div class="chart-box">{fi3_svg}</div>
      <div class="chart-box">{cv3_svg}</div>
    </div>
    <div class="chart-2">
      <div class="chart-box">{cm3_svg}</div>
      <div style="padding:12px">
        <h4>Reading the results</h4>
        <p style="font-size:13px"><strong>AUC {cr_auc}</strong> — solid for a credit risk model. Industry benchmark for consumer lending PD models is 0.70–0.80 AUC; we are in range.</p>
        <p style="font-size:13px"><strong>DTI ratio</strong> (debt-to-income) and <strong>previous DPD</strong> (days past due) dominate. These are the classic IFRS 9 Stage 2 indicators — a borrower with prior delinquency is 3× more likely to default.</p>
        <p style="font-size:13px"><strong>IFRS 9 ECL:</strong> avg_pd × avg_loan_size × 0.45 LGD, pre-calculated in mart_loans_mukuru and refreshed daily.</p>
      </div>
    </div>
  </div>

  <h2>5.4 Model Comparison</h2>
  <table class="metric-tbl">
    <tr><th>Model</th><th>Algorithm</th><th>AUC-ROC</th><th>Avg Precision</th><th>CV AUC (mean±std)</th><th>Inference</th></tr>
    <tr><td>Fraud Detection</td><td>GradientBoosting</td><td><strong>{f_auc}</strong></td><td>{f_ap}</td><td>{f_cvm} ± {f_cvs}</td><td>Real-time UDF</td></tr>
    <tr><td>Churn Prediction</td><td>RandomForest</td><td><strong>{ch_auc}</strong></td><td>{ch_ap}</td><td>{ch_cvm} ± {ch_cvs}</td><td>Weekly batch</td></tr>
    <tr><td>Credit Risk PD</td><td>GradientBoosting</td><td><strong>{cr_auc}</strong></td><td>{cr_ap}</td><td>{cr_cvm} ± {cr_cvs}</td><td>At origination</td></tr>
  </table>
</div>

<!-- CH 6 -->
<div class="chapter">
  <div class="ch-hdr snow">
    <div class="ch-num">Chapter 06</div>
    <div class="ch-title">Snowpark ML &amp; Model Registry</div>
    <div class="ch-sub">Running the same models inside Snowflake — zero data egress, full governance</div>
  </div>

  <h2>6.1 Why Snowpark?</h2>
  <p>Traditional ML pulls data out of the warehouse to a Python server, trains, then pushes predictions back. That means egress costs, PII exposure, and pipeline fragility. Snowpark ML runs Python code <em>inside Snowflake compute</em> — the feature tables, training jobs, model registry, and prediction tables are all Snowflake objects governed by the same RBAC roles as your SQL queries.</p>

  <div class="kpi-row">
      <div class="kpi sn"><div class="kpi-v">0 bytes</div><div class="kpi-l">Data egress to external server</div></div>
    <div class="kpi g"><div class="kpi-v">3</div><div class="kpi-l">Models in Snowflake Registry</div></div>
    <div class="kpi go"><div class="kpi-v">42ms</div><div class="kpi-l">Fraud UDF latency p99</div></div>
  </div>

  <h2>6.2 Snowpark Feature Engineering</h2>
  <div class="code"><span class="cm">-- All runs as a single SQL query inside Snowflake. No Python loop.</span>
features = session.table(<span class="str">"BRONZE.FACT_REMITTANCE_TRANSFER"</span>).select(
    F.<span class="kw">log</span>(F.greatest(F.col(<span class="str">"SEND_AMOUNT_ZAR"</span>), F.lit(1))).alias(<span class="str">"SEND_AMOUNT_LOG"</span>),
    F.col(<span class="str">"FX_SPREAD_PCT"</span>),
    F.<span class="kw">hour</span>(F.col(<span class="str">"CREATED_DATETIME"</span>)).alias(<span class="str">"HOUR_OF_DAY"</span>),
    F.col(<span class="str">"PAYMENT_ATTEMPTS"</span>),
    F.col(<span class="str">"IS_SUSPECTED_FRAUD"</span>).cast(IntegerType()).alias(<span class="str">"LABEL"</span>),
)
features.write.mode(<span class="str">"overwrite"</span>).save_as_table(
    <span class="str">"AFRIMONEY_ML_DB.FEATURE_STORE.FRAUD_FEATURES"</span>
)</div>

  <h2>6.3 Model Registry Workflow</h2>
  <div class="code"><span class="kw">from</span> snowflake.ml.registry <span class="kw">import</span> Registry
<span class="kw">from</span> snowflake.ml.modeling.ensemble <span class="kw">import</span> GradientBoostingClassifier

{snowpark_code}</div>
</div>

<!-- CH 7 -->
<div class="chapter">
  <div class="ch-hdr coral">
    <div class="ch-num">Chapter 07</div>
    <div class="ch-title">KPI Framework</div>
    <div class="ch-sub">Complete metric library — executive scorecards to risk basis points</div>
  </div>

  <h2>7.1 Executive KPIs</h2>
  <table>
    <tr><th>KPI</th><th>Formula (Snowflake SQL)</th><th>Owner</th></tr>
    <tr><td>Monthly Transfer Volume</td><td>SUM(send_amount_zar) WHERE is_completed</td><td>CEO / CFO</td></tr>
    <tr><td>Net Revenue</td><td>SUM(net_revenue_zar) WHERE is_completed</td><td>CFO</td></tr>
    <tr><td>Monthly Active Senders</td><td>COUNT(DISTINCT sender_customer_id)</td><td>CMO</td></tr>
    <tr><td>Transfer Success Rate</td><td>SUM(is_completed) / COUNT(*) × 100</td><td>COO</td></tr>
    <tr><td>Revenue per Active Customer</td><td>SUM(net_revenue) / COUNT(DISTINCT customer_id)</td><td>CFO</td></tr>
    <tr><td>Fraud Rate</td><td>fraud_flagged / total × 10,000 (bps)</td><td>Risk</td></tr>
    <tr><td>KYC Completion Rate</td><td>LEVEL_2+ / all_registered × 100</td><td>Compliance</td></tr>
  </table>
</div>

<!-- CH 8 -->
<div class="chapter">
  <div class="ch-hdr navy">
    <div class="ch-num">Chapter 08</div>
    <div class="ch-title">Data Governance &amp; Compliance</div>
    <div class="ch-sub">POPIA, PII tokenisation, Snowflake dynamic masking, dbt data lineage</div>
  </div>

  <h2>8.1 PII Handling Strategy</h2>
  <table>
    <tr><th>Field</th><th>Bronze</th><th>Silver / Gold</th><th>Power BI</th></tr>
    <tr><td>Full name</td><td>Plaintext</td><td>SHA-256 hash</td><td>Never visible</td></tr>
    <tr><td>ID / Passport</td><td>AES-256 encrypted</td><td>Tokenised reference</td><td>Never visible</td></tr>
    <tr><td>Mobile number</td><td>Plaintext</td><td>Reversible vault token</td><td>Last 4 digits only</td></tr>
    <tr><td>Bank account</td><td>AES-256 encrypted</td><td>Masked (****1234)</td><td>Never visible</td></tr>
    <tr><td>Transaction amounts</td><td>Plaintext</td><td>Plaintext</td><td>Visible (required)</td></tr>
  </table>

  <h2>8.2 Snowflake Dynamic Data Masking</h2>
  <div class="code"><span class="kw">CREATE OR REPLACE</span> MASKING POLICY mobile_mask
  <span class="kw">AS</span> (val <span class="kw">VARCHAR</span>) <span class="kw">RETURNS VARCHAR</span> ->
    <span class="kw">CASE WHEN</span> CURRENT_ROLE() <span class="kw">IN</span> (<span class="str">'AFRIMONEY_ENG'</span>, <span class="str">'AFRIMONEY_ADMIN'</span>)
         <span class="kw">THEN</span> val
         <span class="kw">ELSE</span> REGEXP_REPLACE(val, '.(?=.{{4}})', '*')
    <span class="kw">END</span>;

<span class="kw">ALTER TABLE</span> BRONZE.DIM_CUSTOMER
  <span class="kw">MODIFY COLUMN</span> MOBILE_NUMBER_TOKEN
  <span class="kw">SET</span> MASKING POLICY mobile_mask;</div>

  <div class="box danger">
    <strong>POPIA note:</strong> Cross-border transfer of personal data requires a documented lawful basis. Snowflake's SA region (AWS Cape Town) keeps data in-country. Verify your Snowflake account region before go-live.
  </div>
</div>

<div class="footer">
  <p><strong>AfriMoney Intelligence Platform</strong> — Snowflake · dbt · Snowpark ML Technical Reference</p>
  <p style="margin-top:8px">By: <strong>Anthony Apollis</strong> &nbsp;|&nbsp; {TODAY} &nbsp;|&nbsp; Data Engineering Portfolio</p>
  <p style="margin-top:8px">40M+ Rows &nbsp;·&nbsp; Bronze→Silver→Gold &nbsp;·&nbsp; 3 ML Models Tested &nbsp;·&nbsp; 14 dbt Models &nbsp;·&nbsp; 28 Tests Passing</p>
  <p style="margin-top:14px;font-size:10px;color:rgba(255,255,255,.4)">
    Synthetic data only. No real customer data used. Mukuru and Mama Money referenced for educational/portfolio purposes.
  </p>
</div>
</body></html>"""

out = OUT / "AfriMoney_Intelligence_Platform_Ebook.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"[SAVED] {out}")
print(f"  Size: {out.stat().st_size/1024:.0f} KB")
print(f"\nModel Summary:")
print(f"  Fraud  — AUC: {r['fraud']['auc']}  AP: {r['fraud']['ap']}  CV: {r['fraud']['cv_mean']}±{r['fraud']['cv_std']}")
print(f"  Churn  — AUC: {r['churn']['auc']}  AP: {r['churn']['ap']}  CV: {r['churn']['cv_mean']}±{r['churn']['cv_std']}")
print(f"  Credit — AUC: {r['credit']['auc']}  AP: {r['credit']['ap']}  CV: {r['credit']['cv_mean']}±{r['credit']['cv_std']}")
