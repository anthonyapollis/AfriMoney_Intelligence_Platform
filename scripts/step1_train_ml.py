"""Step 1 — Fast ML training: 50K rows, 100 trees, 3-fold CV."""
import numpy as np, pandas as pd, json, warnings
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score, average_precision_score, confusion_matrix, roc_curve
warnings.filterwarnings("ignore")
np.random.seed(42)

BASE   = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
ML_DIR = BASE / "ml_models"
ML_DIR.mkdir(exist_ok=True)

print("Generating data...")
N_T, N_C, N_L = 50_000, 30_000, 15_000

# ── FRAUD ──
sa = np.random.lognormal(7.2, 0.9, N_T).clip(50,50000)
fx = np.random.uniform(.02,.09,N_T)
hr = np.random.randint(0,24,N_T)
pa = np.random.choice([1,1,1,2,2,3,4],N_T)
kl = np.random.choice([0,1,2,3],N_T,p=[.05,.20,.50,.25])
ag = np.random.uniform(18,65,N_T)
tc = np.random.randint(1,80,N_T)
ci = np.random.choice(17,N_T)
ch = np.random.choice(6,N_T)
iw = np.random.binomial(1,.28,N_T)
fs = ((sa>15000).astype(float)*.25+(pa>=3).astype(float)*.30+
      (hr<5).astype(float)*.20+(kl==0).astype(float)*.25+np.random.uniform(0,.3,N_T))
fl = (fs>0.55).astype(int)
print(f"  Fraud rate:   {fl.mean()*100:.1f}%")
T  = pd.DataFrame({"send_amount_log":np.log1p(sa),"fee_pct":np.random.uniform(.03,.09,N_T),
                   "fx_spread_pct":fx,"hour_of_day":hr,"payment_attempts":pa,
                   "corridor_idx":ci,"channel_idx":ch,"is_weekend":iw,
                   "kyc_level":kl,"customer_age":ag,"customer_tx_count":tc})

# ── CHURN ──
ds = np.random.exponential(45,N_C).clip(1,365)
es = np.random.uniform(0,100,N_C)
wb = np.random.lognormal(6,1.2,N_C).clip(0,50000)
ct = np.random.randint(0,50,N_C)
cc = np.random.randint(1,6,N_C)
kc = np.random.choice([0,1,2,3],N_C,p=[.05,.20,.50,.25])
nt = np.random.randint(1,80,N_C)
mr = nt/(ds/30+1)
cs = ((ds>90).astype(float)*.40+(mr<.5).astype(float)*.25+
      (wb<100).astype(float)*.15+(kc<2).astype(float)*.10+np.random.uniform(0,.15,N_C))
cl = (cs>0.45).astype(int)
print(f"  Churn rate:   {cl.mean()*100:.1f}%")
C  = pd.DataFrame({"total_transfers":nt,"days_since_last":ds,"engagement_score":es,
                   "wallet_balance":np.log1p(wb),"card_transactions":ct,
                   "distinct_corridors":cc,"kyc_level":kc,"monthly_tx_rate":mr})

# ── CREDIT ──
pr = np.random.lognormal(7.5,.6,N_L).clip(500,30000)
im = np.random.lognormal(8.5,.5,N_L)
dp = np.random.choice([0,0,0,1,2,3,5,10,30,60],N_L)
lc = np.random.randint(1,10,N_L)
dt = (pr/(im*6)).clip(0,1)
em = np.random.randint(1,120,N_L)
kk = np.random.choice([1,2,3],N_L,p=[.2,.5,.3])
dl = (dt*.35+(dp>0).astype(float)*.30+(em<12).astype(float)*.15+
      (lc>5).astype(float)*.10+np.random.uniform(0,.15,N_L))
dl = (dl>0.45).astype(int)
print(f"  Default rate: {dl.mean()*100:.1f}%")
L  = pd.DataFrame({"principal_log":np.log1p(pr),"income_log":np.log1p(im),
                   "dti_ratio":dt,"prev_dpd":dp,"loan_count":lc,
                   "employment_months":em,"kyc_level":kk})

def samp(x,y,n=50):
    idx=np.round(np.linspace(0,len(x)-1,n)).astype(int)
    return x[idx].tolist(),y[idx].tolist()

def run(X,y,clf,label):
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,stratify=y,random_state=42)
    clf.fit(Xtr,ytr)
    p=clf.predict_proba(Xte)[:,1]
    auc=round(roc_auc_score(yte,p),4)
    ap =round(average_precision_score(yte,p),4)
    cv =cross_val_score(clf,X,y,cv=3,scoring="roc_auc",n_jobs=-1)
    fpr,tpr,_=roc_curve(yte,p)
    fs,ts=samp(fpr,tpr)
    cm=confusion_matrix(yte,(p>=.5).astype(int)).tolist()
    fi=dict(sorted(zip(X.columns,clf.feature_importances_),key=lambda x:-x[1])[:8])
    print(f"  {label}: AUC={auc}  AP={ap}  CV={cv.mean():.4f}±{cv.std():.4f}")
    return {"auc":auc,"ap":ap,"cv_mean":round(float(cv.mean()),4),"cv_std":round(float(cv.std()),4),
            "cm":cm,"fi":fi,"fpr":fs,"tpr":ts,
            "n_train":int(len(Xtr)),"n_test":int(len(Xte)),"label_rate":round(float(y.mean()*100),1)}

print("\nTraining (fast config — 100 trees, 3-fold CV)...")
r={}
r["fraud"]  = run(T,fl, GradientBoostingClassifier(n_estimators=100,max_depth=4,learning_rate=.08,subsample=.8,random_state=42),"Fraud")
r["churn"]  = run(C,cl, RandomForestClassifier(n_estimators=100,max_depth=7,min_samples_leaf=15,random_state=42,n_jobs=-1),"Churn")
r["credit"] = run(L,dl, GradientBoostingClassifier(n_estimators=100,max_depth=4,learning_rate=.08,subsample=.8,random_state=42),"Credit")

out=ML_DIR/"ml_results.json"
with open(out,"w") as f: json.dump(r,f,indent=2)
print(f"\n[SAVED] {out}")
