"""
Phase 1b: Generate all remaining tables (recipients, fx, transfers, etc.)
Optimized with chunked writes and set-based lookups
"""
import os, random, math, uuid
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
from pathlib import Path

BASE   = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
BRONZE = BASE / "data" / "bronze"

random.seed(42)
np.random.seed(42)

START_DATE = datetime(2021, 1, 1)
END_DATE   = datetime(2026, 6, 28)
DAYS = (END_DATE - START_DATE).days

def rand_date():
    return START_DATE + timedelta(days=random.randint(0, DAYS),
                                   hours=random.randint(0,23),
                                   minutes=random.randint(0,59))

def save(df, name):
    fp = BRONZE / f"{name}.csv"
    df.to_csv(fp, index=False)
    print(f"  [OK] {name}.csv  ({len(df):,} rows, {fp.stat().st_size//1024:,} KB)")

# Load existing customer data (already generated)
print("Loading customers...")
customers = pd.read_csv(BRONZE / "dim_customer.csv", low_memory=False)
cust_ids  = customers["customer_id"].tolist()
mkr_set   = set(customers[customers["business_key"]=="MKR"]["customer_id"].tolist())
mmy_set   = set(customers[customers["business_key"]=="MMY"]["customer_id"].tolist())
mkr_list  = list(mkr_set)
mmy_list  = list(mmy_set)
print(f"  Loaded {len(cust_ids):,} customers (MKR:{len(mkr_list):,} MMY:{len(mmy_list):,})")

# Date SK map
dim_date = pd.read_csv(BRONZE / "dim_date.csv")
date_sk_map = dict(zip(dim_date["full_date"], dim_date["date_sk"]))

CHANNELS   = ["mobile_app","ussd","whatsapp","website","branch","booth","retail_partner","call_centre","atm","api"]
PAYOUT_METHODS = ["cash_collection","bank_deposit","mobile_wallet","card_credit","home_delivery","merchant_payout"]
PAYMENT_METHODS = ["bank_eft","debit_card","credit_card","cash","mobile_money","wallet","voucher","pos_tap"]
FIRST_NAMES = ["Thabo","Sipho","Nomsa","Zanele","Blessing","Chidi","Abena","Fatima","Moses","Grace",
               "Emmanuel","Priscilla","Tendai","Rudo","Boniface","Aisha","Kofi","Amara","David","Sarah",
               "John","Mary","Peter","Elizabeth","James","Agnes","Michael","Charity","Robert","Florence"]
LAST_NAMES  = ["Moyo","Dube","Ncube","Nyathi","Okafor","Mensah","Diallo","Banda","Mwangi","Kariuki",
               "Mutua","Wanjiku","Sithole","Ndlovu","Mahlangu","Molefe","Khumalo","Mthembu","Mkhize","Zulu"]

# ──────────────────────────────────────────────────────────────────────────────
# RECIPIENTS — 1M (chunked)
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating recipients (1,000,000)...")
RECV_COUNTRIES = ["ZW","MZ","ZM","MW","TZ","KE","NG","GH","CD","UG","RW","ET","SN"]
RECV_PROBS     = [0.25,0.15,0.10,0.08,0.08,0.07,0.05,0.04,0.04,0.04,0.04,0.03,0.03]
RELATIONSHIPS  = ["spouse","parent","child","sibling","friend","colleague","other"]
REL_PROBS      = [0.22,0.20,0.18,0.18,0.10,0.07,0.05]

N = 1_000_000
CHUNK = 100_000
chunks = []
for start in range(0, N, CHUNK):
    end = min(start + CHUNK, N)
    size = end - start
    custs = random.choices(cust_ids, k=size)
    countries = np.random.choice(RECV_COUNTRIES, size=size, p=RECV_PROBS)
    rels = np.random.choice(RELATIONSHIPS, size=size, p=REL_PROBS)
    pouts = np.random.choice(PAYOUT_METHODS, size=size)
    fnames = [random.choice(FIRST_NAMES) for _ in range(size)]
    lnames = [random.choice(LAST_NAMES)  for _ in range(size)]
    verified = np.random.random(size) < 0.75
    has_bank = np.random.random(size) < 0.4
    has_wall = np.random.random(size) < 0.5

    df = pd.DataFrame({
        "recipient_id": [f"RECIP-{start+i+1:08d}" for i in range(size)],
        "sender_customer_id": custs,
        "business_key": ["MKR" if c in mkr_set else "MMY" for c in custs],
        "first_name": fnames,
        "last_name": lnames,
        "relationship": rels,
        "receive_country": countries,
        "preferred_payout_method": pouts,
        "mobile_token": [f"MOB-{random.randint(1000000,9999999)}" for _ in range(size)],
        "bank_account_token": [f"BANK-{uuid.uuid4().hex[:12]}" if h else None for h in has_bank],
        "wallet_token": [f"WALL-{uuid.uuid4().hex[:12]}" if h else None for h in has_wall],
        "is_verified": verified,
        "created_date": [(rand_date()).date().isoformat() for _ in range(size)],
        "transfer_count": 0,
    })
    chunks.append(df)
    print(f"  Recipients: {end:,}/{N:,}")

dim_recipient = pd.concat(chunks, ignore_index=True)
dim_recipient["recipient_sk"] = range(1, len(dim_recipient)+1)
save(dim_recipient, "dim_recipient")

recip_ids = dim_recipient["recipient_id"].tolist()
# Build cust→recip lookup (sample to save memory)
cust_to_recips = {}
for row in dim_recipient[["sender_customer_id","recipient_id"]].itertuples(index=False):
    lst = cust_to_recips.setdefault(row.sender_customer_id, [])
    if len(lst) < 10:
        lst.append(row.recipient_id)
del dim_recipient, chunks
print("  Recipients done.")

# ──────────────────────────────────────────────────────────────────────────────
# FX RATES
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating FX rates...")
dim_corridor = pd.read_csv(BRONZE / "dim_corridor.csv")
BASE_FX = {
    "ZWL":0.42,"MZN":3.20,"ZMW":0.88,"MWK":62.0,"TZS":155.0,
    "KES":5.50,"NGN":85.0,"GHS":0.55,"CDF":16.5,"UGX":230.0,
    "RWF":8.20,"ETB":4.10,"XOF":34.0,"GBP":0.043,"USD":0.052,
    "AUD":0.080,"NZD":0.087,"CNY":0.38,
}
fx_rows = []
rate_id = 1
for _, corr in dim_corridor.iterrows():
    scy = corr["send_currency"]
    dcy = corr["receive_currency"]
    if dcy == scy:
        continue
    base_rate = BASE_FX.get(dcy, 1.0)
    dt = START_DATE
    rate = base_rate
    while dt <= END_DATE:
        vol  = random.gauss(0, 0.003)
        rate = max(rate * (1 + vol), base_rate * 0.5)
        spread = random.uniform(0.03, 0.08)
        cust_rate = rate * (1 - spread)
        fx_rows.append({
            "fx_rate_id": rate_id,
            "corridor_code": corr["corridor_code"],
            "send_currency": scy,
            "receive_currency": dcy,
            "rate_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(), 0),
            "market_rate": round(rate, 6),
            "customer_rate": round(cust_rate, 6),
            "fx_spread_pct": round(spread * 100, 4),
            "margin_per_unit": round(rate - cust_rate, 6),
            "rate_source": "REUTERS",
            "is_active": dt.date() == END_DATE.date(),
        })
        rate_id += 1
        dt += timedelta(hours=6)

fact_fx_rate = pd.DataFrame(fx_rows)
save(fact_fx_rate, "fact_fx_rate")

# Build latest FX lookup
latest_fx = {}
for code in dim_corridor["corridor_code"].unique():
    subset = fact_fx_rate[fact_fx_rate["corridor_code"]==code]
    if not subset.empty:
        r = subset.iloc[-1]
        latest_fx[code] = {"market_rate": r["market_rate"],
                            "customer_rate": r["customer_rate"],
                            "fx_spread_pct": r["fx_spread_pct"]}
del fx_rows
print("  FX rates done.")

# ──────────────────────────────────────────────────────────────────────────────
# TRANSFERS — 5M (chunked, written in parts)
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating transfers (5,000,000)...")
N_TFR   = 5_000_000
CHUNK   = 200_000
corr_list = dim_corridor.to_dict("records")
mkr_corrs = [c for c in corr_list if c["mukuru_active"]]
mmy_corrs = [c for c in corr_list if c["mama_money_active"]]
transfer_rows = []

for start in range(0, N_TFR, CHUNK):
    end   = min(start + CHUNK, N_TFR)
    chunk_rows = []
    for i in range(end - start):
        tid = start + i + 1
        biz = "MKR" if random.random() < 0.60 else "MMY"
        cust = random.choice(mkr_list if biz=="MKR" else mmy_list)
        corr = random.choice(mkr_corrs if biz=="MKR" else mmy_corrs)
        recips = cust_to_recips.get(cust)
        recip  = random.choice(recips) if recips else random.choice(recip_ids[:50000])
        created = rand_date()
        cdate   = created.date().isoformat()
        amount_zar = round(max(50, min(random.lognormvariate(math.log(1500), 0.8), 50000)), 2)
        fx  = latest_fx.get(corr["corridor_code"], {"market_rate":1,"customer_rate":0.95,"fx_spread_pct":5})
        recv_amount = round(amount_zar * fx["customer_rate"], 2)
        fee_pct = random.uniform(0.02, 0.08)
        fee     = round(amount_zar * fee_pct, 2)
        vat     = round(fee * 0.15, 2)
        mr, cr  = fx["market_rate"], fx["customer_rate"]
        fx_margin = round(amount_zar * (mr - cr) / max(mr,0.001), 2)
        partner_cost = round(amount_zar * random.uniform(0.005, 0.025), 2)
        gross_rev = fee + fx_margin
        net_rev   = gross_rev - partner_cost
        status = np.random.choice(
            ["COMPLETED","FAILED","CANCELLED","REFUNDED","AWAITING_PAYMENT"],
            p=[0.78,0.08,0.10,0.02,0.02])
        completed_dt = (created + timedelta(minutes=random.randint(5,2880))) if status=="COMPLETED" else None
        comp_mins    = int((completed_dt-created).total_seconds()/60) if completed_dt else None
        chunk_rows.append({
            "transfer_id": f"TFR-{tid:09d}",
            "transfer_reference": uuid.uuid4().hex[:12].upper(),
            "business_key": biz,
            "sender_customer_id": cust,
            "recipient_id": recip,
            "corridor_code": corr["corridor_code"],
            "send_country": corr["send_country"],
            "receive_country": corr["receive_country"],
            "send_currency": corr["send_currency"],
            "receive_currency": corr["receive_currency"],
            "channel": np.random.choice(CHANNELS, p=[0.30,0.15,0.10,0.12,0.05,0.04,0.06,0.03,0.02,0.13]),
            "payment_method": np.random.choice(PAYMENT_METHODS, p=[0.25,0.20,0.05,0.15,0.12,0.12,0.05,0.06]),
            "payout_method": random.choice(PAYOUT_METHODS),
            "created_datetime": created.isoformat(),
            "created_date_key": date_sk_map.get(cdate, 0),
            "completed_datetime": completed_dt.isoformat() if completed_dt else None,
            "completed_date_key": date_sk_map.get(completed_dt.date().isoformat(),0) if completed_dt else None,
            "transfer_status": status,
            "send_amount_zar": amount_zar,
            "receive_amount": recv_amount,
            "transfer_fee_zar": fee,
            "vat_zar": vat,
            "fx_margin_zar": fx_margin,
            "partner_cost_zar": partner_cost,
            "gross_revenue_zar": round(gross_rev,2),
            "net_revenue_zar": round(net_rev,2),
            "market_fx_rate": mr,
            "customer_fx_rate": cr,
            "fx_spread_pct": round(fx["fx_spread_pct"],4),
            "payment_attempts": random.randint(1,3),
            "payout_attempts": random.randint(1,3) if status=="COMPLETED" else 0,
            "completion_minutes": comp_mins,
            "is_completed":  status=="COMPLETED",
            "is_failed":     status=="FAILED",
            "is_cancelled":  status=="CANCELLED",
            "is_refunded":   status=="REFUNDED",
            "is_first_transfer": tid <= 50000,
            "is_repeat_customer": tid > 50000,
            "is_suspected_fraud": random.random() < 0.008,
        })
    transfer_rows.extend(chunk_rows)
    print(f"  Transfers: {end:,}/{N_TFR:,}")

fact_transfer = pd.DataFrame(transfer_rows)
save(fact_transfer, "fact_remittance_transfer")
del transfer_rows

# ──────────────────────────────────────────────────────────────────────────────
# STATUS HISTORY (~15M)
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating status history (~7.5M rows from 1M transfers)...")
STATUS_FLOW = {
    "COMPLETED": ["CREATED","QUOTED","AWAITING_PAYMENT","PAID","PROCESSING","SENT_TO_PARTNER","AVAILABLE_FOR_COLLECTION","COMPLETED"],
    "FAILED":    ["CREATED","QUOTED","AWAITING_PAYMENT","PAID","COMPLIANCE_REVIEW","FAILED"],
    "CANCELLED": ["CREATED","QUOTED","AWAITING_PAYMENT","CANCELLED"],
    "REFUNDED":  ["CREATED","QUOTED","AWAITING_PAYMENT","PAID","PROCESSING","REFUNDED"],
    "AWAITING_PAYMENT": ["CREATED","QUOTED","AWAITING_PAYMENT"],
}

SAMPLE = fact_transfer.sample(min(1_000_000, len(fact_transfer)), random_state=42)
hist_rows = []
hid = 1
for row in SAMPLE.itertuples(index=False):
    flow = STATUS_FLOW.get(row.transfer_status, ["CREATED","COMPLETED"])
    dt   = datetime.fromisoformat(row.created_datetime)
    orig = dt
    for s in flow:
        hist_rows.append({
            "status_history_id": hid,
            "transfer_id": row.transfer_id,
            "business_key": row.business_key,
            "status_code": s,
            "status_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(), 0),
            "elapsed_minutes_from_created": int((dt-orig).total_seconds()/60),
            "system_user": f"SYS-{random.randint(1,50)}",
            "notes": None,
        })
        hid += 1
        dt += timedelta(minutes=random.randint(1,240))
    if hid % 2_000_000 == 0:
        print(f"  Status history: {hid:,}")

fact_status = pd.DataFrame(hist_rows)
save(fact_status, "fact_transfer_status_history")
del hist_rows, fact_status, SAMPLE

# ──────────────────────────────────────────────────────────────────────────────
# PAYMENTS — 5.5M
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating payments (5,500,000)...")
pay_rows = []
pid = 1
for row in fact_transfer.itertuples(index=False):
    n_att = int(row.payment_attempts)
    created_dt = datetime.fromisoformat(row.created_datetime)
    for a in range(n_att):
        is_last = a == n_att - 1
        success = is_last and row.is_completed
        dt = created_dt + timedelta(minutes=random.randint(1,120)*max(a,1))
        pay_rows.append({
            "payment_id": f"PAY-{pid:09d}",
            "transfer_id": row.transfer_id,
            "business_key": row.business_key,
            "sender_customer_id": row.sender_customer_id,
            "payment_method": row.payment_method,
            "payment_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(), 0),
            "amount_zar": row.send_amount_zar,
            "fee_zar": row.transfer_fee_zar,
            "total_charged_zar": round(row.send_amount_zar + row.transfer_fee_zar, 2),
            "attempt_number": a+1,
            "payment_status": "SUCCESS" if success else ("DECLINED" if a < n_att-1 else "FAILED"),
            "decline_reason": random.choice(["INSUFFICIENT_FUNDS","CARD_BLOCKED","LIMIT_EXCEEDED",None,None]) if not success else None,
            "payment_reference": uuid.uuid4().hex[:16].upper(),
            "gateway_code": f"GW-{random.randint(1,5)}",
        })
        pid += 1
    if pid % 2_000_000 == 0:
        print(f"  Payments: {pid:,}")

fact_payment = pd.DataFrame(pay_rows)
save(fact_payment, "fact_payment")
del pay_rows

# ──────────────────────────────────────────────────────────────────────────────
# PAYOUTS — 4.5M
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating payouts (4,500,000)...")
completed = fact_transfer[fact_transfer["is_completed"]==True].head(2_000_000)
pout_rows = []
poid = 1
for row in completed.itertuples(index=False):
    n_att = max(1, int(row.payout_attempts))
    created_dt = datetime.fromisoformat(row.created_datetime)
    for a in range(n_att):
        is_last = a == n_att-1
        dt = created_dt + timedelta(hours=random.randint(1,48)*(a+1))
        pout_rows.append({
            "payout_id": f"PO-{poid:09d}",
            "transfer_id": row.transfer_id,
            "business_key": row.business_key,
            "recipient_id": row.recipient_id,
            "receive_country": row.receive_country,
            "payout_method": row.payout_method,
            "payout_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(), 0),
            "amount_receive_currency": row.receive_amount,
            "amount_zar_equivalent": row.send_amount_zar,
            "partner_code": f"PARTNER-{random.randint(1,30):02d}",
            "partner_location_id": f"LOC-{random.randint(1,5000):05d}",
            "attempt_number": a+1,
            "payout_status": "SUCCESS" if is_last else "FAILED",
            "failure_reason": random.choice(["PARTNER_OFFLINE","ID_MISMATCH","LIMIT_EXCEEDED",None]) if not is_last else None,
            "collection_code": uuid.uuid4().hex[:8].upper() if row.payout_method=="cash_collection" else None,
        })
        poid += 1
    if poid % 1_000_000 == 0:
        print(f"  Payouts: {poid:,}")

fact_payout = pd.DataFrame(pout_rows)
save(fact_payout, "fact_payout")
del pout_rows

# ──────────────────────────────────────────────────────────────────────────────
# WALLET LEDGER — 10M
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating wallet ledger (10,000,000)...")
ENTRY_TYPES = [
    ("CASH_IN","debit"),("TRANSFER_OUT","credit"),("TRANSFER_IN","debit"),
    ("CARD_LOAD","credit"),("USD_BUY","credit"),("USD_SELL","debit"),
    ("FEE_CHARGE","credit"),("REFUND","debit"),("SALARY_DEPOSIT","debit"),
    ("AIRTIME_BUY","credit"),("ELECTRICITY_BUY","credit"),("CASH_SEND","credit"),
]
N_WALL = 250_000
wall_custs = random.sample(cust_ids, N_WALL)
wall_rows = []
wid = 1
WALL_CHUNK = 50_000
for batch_start in range(0, N_WALL, WALL_CHUNK):
    batch = wall_custs[batch_start:batch_start+WALL_CHUNK]
    for cust in batch:
        biz = "MKR" if cust in mkr_set else "MMY"
        n_entries = random.randint(10, 80)
        balance = 0.0
        for _ in range(n_entries):
            entry_type, direction = random.choice(ENTRY_TYPES)
            amount = round(max(10, min(abs(random.lognormvariate(math.log(500), 0.9)), 20000)), 2)
            balance = balance + amount if direction=="debit" else max(0, balance-amount)
            dt = rand_date()
            wall_rows.append({
                "ledger_id": f"WL-{wid:010d}",
                "wallet_id": f"WALL-{abs(hash(cust))%10000000:07d}",
                "customer_id": cust,
                "business_key": biz,
                "entry_type": entry_type,
                "entry_direction": direction,
                "amount_zar": amount,
                "running_balance_zar": round(balance, 2),
                "entry_datetime": dt.isoformat(),
                "date_key": date_sk_map.get(dt.date().isoformat(), 0),
                "reference_id": f"REF-{random.randint(1,9999999):07d}",
                "channel": random.choice(CHANNELS),
            })
            wid += 1
    print(f"  Wallet ledger: {wid:,}")

fact_wallet = pd.DataFrame(wall_rows)
save(fact_wallet, "fact_wallet_ledger")
del wall_rows

# ──────────────────────────────────────────────────────────────────────────────
# CARD TRANSACTIONS — 3M
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating card transactions (3,000,000)...")
MERCH_CATS = ["grocery","fuel","pharmacy","clothing","airtime","electricity",
              "restaurant","transport","hardware","electronics","online","atm_withdrawal"]
N_CARD = 120_000
card_custs = random.sample(cust_ids, N_CARD)
card_rows = []
cid = 1
for cust in card_custs:
    biz = "MKR" if cust in mkr_set else "MMY"
    card_type = "MUKURU_CARD" if biz=="MKR" else "MAMA_CARD"
    n_txns = random.randint(5, 50)
    for _ in range(n_txns):
        dt = rand_date()
        amount = round(max(5, min(abs(random.lognormvariate(math.log(300),0.9)), 5000)),2)
        status = np.random.choice(["APPROVED","DECLINED","REVERSED"],p=[0.88,0.09,0.03])
        card_rows.append({
            "card_txn_id": f"CTX-{cid:09d}",
            "card_account_id": f"CARD-{abs(hash(cust))%1000000:06d}",
            "customer_id": cust,
            "business_key": biz,
            "card_type": card_type,
            "merchant_category": random.choice(MERCH_CATS),
            "merchant_name": f"MERCHANT-{random.randint(1,10000):05d}",
            "merchant_country": "ZA" if random.random()<0.85 else random.choice(["ZW","MZ","ZM"]),
            "transaction_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(), 0),
            "amount_zar": amount,
            "transaction_type": np.random.choice(["purchase","atm_withdrawal","refund","salary_credit"],p=[0.70,0.12,0.08,0.10]),
            "channel": np.random.choice(["card_swipe","contactless","online","atm"],p=[0.40,0.30,0.20,0.10]),
            "authorisation_code": uuid.uuid4().hex[:6].upper(),
            "transaction_status": status,
            "decline_reason": random.choice(["INSUFFICIENT_FUNDS","WRONG_PIN","EXPIRED",None]) if status=="DECLINED" else None,
            "is_fraud_flagged": random.random() < 0.006,
        })
        cid += 1
    if cid % 1_000_000 == 0:
        print(f"  Card: {cid:,}")

fact_card = pd.DataFrame(card_rows)
save(fact_card, "fact_card_transaction")
del card_rows

# ──────────────────────────────────────────────────────────────────────────────
# LOANS — 200K
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating loans (200,000)...")
LOAN_CUSTS = random.sample(mkr_list, min(80_000, len(mkr_list)))
loan_rows  = []
repay_rows = []
lid, rid = 1, 1
for cust in LOAN_CUSTS:
    n_apps = random.randint(1,3)
    app_dt = rand_date()
    for _ in range(n_apps):
        decision = np.random.choice(["APPROVED","DECLINED","PENDING"],p=[0.55,0.38,0.07])
        principal = round(random.uniform(500,10000), 2)
        term   = random.choice([1,2,3,6])
        rate   = random.uniform(0.05,0.20)
        mrate  = rate/12
        mpmt   = round(principal*mrate/(1-(1+mrate)**-term), 2) if decision=="APPROVED" else 0
        pd_s   = round(random.betavariate(2,8), 4)
        loan_rows.append({
            "loan_id": f"LOAN-{lid:08d}",
            "customer_id": cust,
            "business_key": "MKR",
            "application_datetime": app_dt.isoformat(),
            "date_key": date_sk_map.get(app_dt.date().isoformat(), 0),
            "decision": decision,
            "loan_purpose": np.random.choice(["emergency","school_fees","home","business","medical","other"],p=[0.30,0.20,0.15,0.15,0.12,0.08]),
            "principal_zar": principal,
            "interest_rate_annual_pct": round(rate*100,2),
            "term_months": term,
            "monthly_payment_zar": mpmt,
            "total_repayable_zar": round(mpmt*term,2),
            "disbursement_method": "MUKURU_CARD",
            "loan_status": np.random.choice(["ACTIVE","SETTLED","DEFAULTED","WRITTEN_OFF"],p=[0.40,0.45,0.10,0.05]) if decision=="APPROVED" else "DECLINED",
            "probability_of_default": pd_s,
            "expected_credit_loss_zar": round(principal*pd_s,2),
            "days_past_due": random.randint(0,180) if decision=="APPROVED" and random.random()<0.15 else 0,
            "card_account_age_days": random.randint(30,1800),
            "avg_monthly_card_spend_zar": round(random.uniform(200,5000),2),
            "salary_indicator": random.random()<0.6,
            "previous_loans": random.randint(0,5),
            "previous_loans_repaid": random.randint(0,5),
        })
        if decision=="APPROVED":
            disburse = app_dt + timedelta(hours=random.randint(1,48))
            for m in range(term):
                due = disburse + timedelta(days=30*(m+1))
                paid = random.random() < 0.85
                repay_rows.append({
                    "repayment_id": f"REPAY-{rid:09d}",
                    "loan_id": f"LOAN-{lid:08d}",
                    "customer_id": cust,
                    "business_key": "MKR",
                    "instalment_number": m+1,
                    "due_date": due.date().isoformat(),
                    "paid_datetime": (due+timedelta(days=random.randint(-5,15))).isoformat() if paid else None,
                    "amount_due_zar": mpmt,
                    "amount_paid_zar": mpmt if paid else round(mpmt*random.uniform(0,0.9),2),
                    "payment_status": "PAID" if paid else "MISSED",
                    "days_past_due": max(0,random.randint(0,30)) if not paid else 0,
                })
                rid += 1
        lid += 1
        app_dt += timedelta(days=random.randint(60,365))

save(pd.DataFrame(loan_rows),  "fact_loan_application")
save(pd.DataFrame(repay_rows), "fact_loan_repayment")
del loan_rows, repay_rows

# ──────────────────────────────────────────────────────────────────────────────
# INSURANCE — 40K policies
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating insurance (40,000 policies)...")
PLANS = [("BASIC",150,35000),("STANDARD",250,75000),("EXTENDED",400,120000),("PREMIER",600,200000)]
INSUR_CUSTS = random.sample(mkr_list, min(40_000, len(mkr_list)))
pol_rows = []
clm_rows = []
iid, clid = 1, 1
for cust in INSUR_CUSTS:
    plan = random.choice(PLANS)
    start = rand_date()
    status = np.random.choice(["ACTIVE","LAPSED","CANCELLED"],p=[0.70,0.20,0.10])
    pol_rows.append({
        "policy_id": f"POL-{iid:08d}",
        "customer_id": cust, "business_key": "MKR",
        "product_name": "Mukuru Funeral Cover",
        "plan_name": plan[0],
        "monthly_premium_zar": plan[1],
        "cover_amount_zar": plan[2],
        "policy_start_date": start.date().isoformat(),
        "policy_status": status,
        "total_premiums_paid_zar": round(plan[1]*random.randint(1,48),2),
        "beneficiary_name": random.choice(FIRST_NAMES)+" "+random.choice(LAST_NAMES),
        "repatriation_country": np.random.choice(["ZW","MZ","ZM","MW"],p=[0.50,0.20,0.15,0.15]),
    })
    if random.random()<0.08 and status=="ACTIVE":
        claim_dt = start + timedelta(days=random.randint(60,730))
        approved = random.random()<0.80
        clm_rows.append({
            "claim_id": f"CLM-{clid:07d}",
            "policy_id": f"POL-{iid:08d}",
            "customer_id": cust, "business_key": "MKR",
            "claim_datetime": claim_dt.isoformat(),
            "date_key": date_sk_map.get(claim_dt.date().isoformat(), 0),
            "claim_type": random.choice(["MAIN_MEMBER","SPOUSE","CHILD","PARENT","EXTENDED"]),
            "claimed_amount_zar": plan[2],
            "decision": "APPROVED" if approved else "REPUDIATED",
            "paid_amount_zar": plan[2] if approved else 0,
            "turnaround_days": random.randint(1,30),
            "repudiation_reason": random.choice(["EXCLUSION","FRAUD","WAITING_PERIOD"]) if not approved else None,
        })
        clid += 1
    iid += 1

save(pd.DataFrame(pol_rows), "fact_insurance_policy")
save(pd.DataFrame(clm_rows), "fact_insurance_claim")

# ──────────────────────────────────────────────────────────────────────────────
# USD SAVINGS (Mama Money) — 50K
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating USD savings (50,000)...")
USD_CUSTS = random.sample(mmy_list, min(50_000, len(mmy_list)))
usd_rows = []
for cust in USD_CUSTS:
    opens = rand_date()
    bal   = round(random.uniform(0,5000),2)
    usd_rows.append({
        "savings_id": f"USD-{abs(hash(cust))%10000000:07d}",
        "customer_id": cust, "business_key": "MMY",
        "account_opened_date": opens.date().isoformat(),
        "account_status": np.random.choice(["ACTIVE","DORMANT","CLOSED"],p=[0.75,0.15,0.10]),
        "current_balance_usdc": bal,
        "current_balance_usd": bal,
        "current_balance_zar": round(bal/0.052,2),
        "total_purchased_usdc": round(bal+random.uniform(0,2000),2),
        "total_sold_usdc": round(random.uniform(0,1000),2),
        "last_purchase_date": (opens+timedelta(days=random.randint(1,500))).date().isoformat(),
        "underlying_asset": "USDC",
        "is_usdc_backed": True,
    })
save(pd.DataFrame(usd_rows), "fact_usd_savings")

# ──────────────────────────────────────────────────────────────────────────────
# PARTNERS & LOCATIONS
# ──────────────────────────────────────────────────────────────────────────────
print("\nGenerating partners & locations...")
partners = []
for i in range(1,51):
    country = random.choice(["ZW","MZ","ZM","MW","TZ","KE","NG","GH","CD","UG"])
    partners.append({
        "partner_sk":i, "partner_id":f"PARTNER-{i:02d}",
        "partner_name":f"Partner {i} Ltd",
        "partner_type": np.random.choice(["mobile_money_op","bank","cash_agent","card_issuer"],p=[0.35,0.30,0.25,0.10]),
        "country":country, "is_active":random.random()<0.85,
        "commission_pct":round(random.uniform(0.5,3.5),2),
        "settlement_days":random.choice([1,2,3,5]),
        "volume_last_30d_zar":round(random.uniform(500000,50000000),2),
        "mukuru_partner":random.random()<0.8,
        "mama_money_partner":random.random()<0.6,
    })
save(pd.DataFrame(partners), "dim_partner")

locations = []
for i in range(1,5001):
    locations.append({
        "location_sk":i, "location_id":f"LOC-{i:05d}",
        "location_name":f"Location {i}",
        "location_type":np.random.choice(["branch","booth","retail","atm","partner_outlet"],p=[0.10,0.15,0.40,0.15,0.20]),
        "country":random.choice(["ZW","MZ","ZM","MW","TZ","KE","NG","GH","CD","UG","ZA"]),
        "city":f"City-{random.randint(1,100)}",
        "latitude":round(random.uniform(-34,-5),6),
        "longitude":round(random.uniform(12,40),6),
        "is_active":random.random()<0.80,
        "partner_id":f"PARTNER-{random.randint(1,50):02d}",
    })
save(pd.DataFrame(locations), "dim_location")

# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("ALL DATA GENERATION COMPLETE")
print("="*60)
total_size = sum(f.stat().st_size for f in BRONZE.glob("*.csv"))
print(f"\nTotal bronze data: {total_size/1024/1024:.0f} MB")
for f in sorted(BRONZE.glob("*.csv")):
    print(f"  {f.name:45s} {f.stat().st_size/1024/1024:8.1f} MB")
