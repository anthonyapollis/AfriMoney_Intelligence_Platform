"""
African Fintech Intelligence Platform
Synthetic Data Generator — Phase 1: RAW / BRONZE layer
Mukuru + Mama Money unified model
Target: ~40M+ rows across all tables
"""

import os, sys, random, math, uuid
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
RAW  = BASE / "data" / "raw"
BRONZE = BASE / "data" / "bronze"
SILVER = BASE / "data" / "silver"

random.seed(42)
np.random.seed(42)

# ── Reference data ─────────────────────────────────────────────────────────────

BUSINESSES = [
    {"business_key": "MKR", "business_name": "Mukuru", "founded_year": 2004,
     "hq_country": "ZA", "primary_currency": "ZAR", "brand_colour": "#E31837"},
    {"business_key": "MMY", "business_name": "Mama Money", "founded_year": 2015,
     "hq_country": "ZA", "primary_currency": "ZAR", "brand_colour": "#F7941D"},
]

COUNTRIES = [
    ("ZA","South Africa","ZAR","Africa","Southern Africa",True),
    ("ZW","Zimbabwe","ZWL","Africa","Southern Africa",False),
    ("MZ","Mozambique","MZN","Africa","Southern Africa",False),
    ("ZM","Zambia","ZMW","Africa","Southern Africa",False),
    ("MW","Malawi","MWK","Africa","Southern Africa",False),
    ("TZ","Tanzania","TZS","Africa","Eastern Africa",False),
    ("KE","Kenya","KES","Africa","Eastern Africa",False),
    ("UG","Uganda","UGX","Africa","Eastern Africa",False),
    ("RW","Rwanda","RWF","Africa","Eastern Africa",False),
    ("NG","Nigeria","NGN","Africa","Western Africa",False),
    ("GH","Ghana","GHS","Africa","Western Africa",False),
    ("SN","Senegal","XOF","Africa","Western Africa",False),
    ("CD","DRC","CDF","Africa","Central Africa",False),
    ("ET","Ethiopia","ETB","Africa","Eastern Africa",False),
    ("SO","Somalia","SOS","Africa","Eastern Africa",False),
    ("UK","United Kingdom","GBP","Europe","Northern Europe",False),
    ("US","United States","USD","Americas","Northern America",False),
    ("AU","Australia","AUD","Oceania","Australia and NZ",False),
    ("NZ","New Zealand","NZD","Oceania","Australia and NZ",False),
    ("CN","China","CNY","Asia","Eastern Asia",False),
]

CORRIDORS_RAW = [
    ("ZA","ZW","ZAR","ZWL","SADC",True,True),
    ("ZA","MZ","ZAR","MZN","SADC",True,True),
    ("ZA","ZM","ZAR","ZMW","SADC",True,True),
    ("ZA","MW","ZAR","MWK","SADC",True,True),
    ("ZA","TZ","ZAR","TZS","SADC",True,True),
    ("ZA","KE","ZAR","KES","EAC",True,True),
    ("ZA","NG","ZAR","NGN","ECOWAS",True,False),
    ("ZA","GH","ZAR","GHS","ECOWAS",True,False),
    ("ZA","CD","ZAR","CDF","SADC",True,False),
    ("ZA","UG","ZAR","UGX","EAC",True,True),
    ("UK","ZW","GBP","ZWL","OTHER",True,False),
    ("UK","ZM","GBP","ZMW","OTHER",True,False),
    ("US","ZW","USD","ZWL","OTHER",True,False),
    ("AU","ZW","AUD","ZWL","OTHER",True,False),
    ("ZA","RW","ZAR","RWF","EAC",True,False),
    ("ZA","ET","ZAR","ETB","OTHER",True,False),
    ("ZA","SN","ZAR","XOF","ECOWAS",True,False),
]

CHANNELS = ["mobile_app","ussd","whatsapp","website","branch","booth",
            "retail_partner","call_centre","atm","api"]
PAYMENT_METHODS = ["bank_eft","debit_card","credit_card","cash","mobile_money",
                   "wallet","voucher","pos_tap"]
PAYOUT_METHODS  = ["cash_collection","bank_deposit","mobile_wallet",
                   "card_credit","home_delivery","merchant_payout"]
TRANSFER_STATUSES = ["CREATED","QUOTED","AWAITING_PAYMENT","PAID","COMPLIANCE_REVIEW",
                     "PROCESSING","SENT_TO_PARTNER","AVAILABLE_FOR_COLLECTION",
                     "COMPLETED","FAILED","CANCELLED","REFUNDED"]
KYCS = ["LEVEL_0","LEVEL_1","LEVEL_2","LEVEL_3"]
RISK_BANDS = ["LOW","MEDIUM","HIGH","VERY_HIGH"]
SEGMENTS = ["MICRO","STANDARD","PREMIUM","VIP"]
LANGUAGES = ["en","zu","xh","af","st","tn","ts","nd","ss","ve","nr","pt"]

START_DATE = datetime(2021, 1, 1)
END_DATE   = datetime(2026, 6, 28)
DAYS = (END_DATE - START_DATE).days

def rand_date(start=START_DATE, span_days=DAYS):
    return start + timedelta(days=random.randint(0, span_days),
                              hours=random.randint(0,23),
                              minutes=random.randint(0,59),
                              seconds=random.randint(0,59))

def rand_date_after(dt, max_add_days=30):
    return dt + timedelta(hours=random.randint(1,24*max_add_days))

def save_csv(df, path, name):
    fp = Path(path) / f"{name}.csv"
    df.to_csv(fp, index=False)
    print(f"  [OK] {name}.csv  ({len(df):,} rows, {fp.stat().st_size//1024:,} KB)")
    return fp

# ═══════════════════════════════════════════════════════════════════════════════
# 1. DIMENSION TABLES
# ═══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("PHASE 1 — DIMENSION TABLES")
print("=" * 60)

# DIM_BUSINESS
dim_business = pd.DataFrame(BUSINESSES)
dim_business["business_sk"] = range(1, len(dim_business)+1)
save_csv(dim_business, BRONZE, "dim_business")

# DIM_COUNTRY
dim_country = pd.DataFrame(COUNTRIES,
    columns=["country_code","country_name","currency_code","region",
             "sub_region","is_send_country"])
dim_country["country_sk"] = range(1, len(dim_country)+1)
save_csv(dim_country, BRONZE, "dim_country")

# DIM_CURRENCY
currencies = list({c[2] for c in COUNTRIES})
dim_currency = pd.DataFrame({
    "currency_code": currencies,
    "currency_name": [c + " Currency" for c in currencies],
    "currency_symbol": ["R","$","KSh","UGX","MWK","TZS","NGN","GHS","XOF",
                         "CDF","ETB","SOS","GBP","USD","AUD","NZD","CNY",
                         "ZWL","MZN","ZMW","RWF"][:len(currencies)],
    "decimal_places": [2]*len(currencies),
})
dim_currency["currency_sk"] = range(1, len(dim_currency)+1)
save_csv(dim_currency, BRONZE, "dim_currency")

# DIM_CORRIDOR
corridors = []
for i, (sc,dc,scy,dcy,bloc,mkr,mmy) in enumerate(CORRIDORS_RAW, 1):
    corridors.append({
        "corridor_sk": i,
        "corridor_code": f"{sc}-{dc}",
        "send_country": sc,
        "receive_country": dc,
        "send_currency": scy,
        "receive_currency": dcy,
        "trade_bloc": bloc,
        "mukuru_active": mkr,
        "mama_money_active": mmy,
        "is_high_volume": i <= 6,
        "regulatory_risk": random.choice(["LOW","MEDIUM","HIGH"]),
    })
dim_corridor = pd.DataFrame(corridors)
save_csv(dim_corridor, BRONZE, "dim_corridor")

# DIM_DATE (full date spine 2021-2026)
date_rows = []
d = date(2021,1,1)
sk = 1
while d <= date(2026,12,31):
    date_rows.append({
        "date_sk": sk,
        "full_date": d.isoformat(),
        "year": d.year,
        "quarter": (d.month-1)//3+1,
        "month": d.month,
        "month_name": d.strftime("%B"),
        "week_of_year": d.isocalendar()[1],
        "day_of_week": d.weekday()+1,
        "day_name": d.strftime("%A"),
        "day_of_month": d.day,
        "is_weekend": d.weekday() >= 5,
        "is_month_end": (d + timedelta(days=1)).month != d.month,
        "is_quarter_end": d.month in (3,6,9,12) and (d+timedelta(days=1)).month != d.month,
        "fiscal_year": d.year if d.month >= 3 else d.year-1,
        "fiscal_quarter": ((d.month+9)%12)//3+1,
    })
    d += timedelta(days=1)
    sk += 1
dim_date = pd.DataFrame(date_rows)
save_csv(dim_date, BRONZE, "dim_date")
date_sk_map = {r["full_date"]: r["date_sk"] for r in date_rows}

# DIM_CHANNEL
dim_channel = pd.DataFrame([{
    "channel_sk": i+1,
    "channel_code": ch,
    "channel_name": ch.replace("_"," ").title(),
    "is_digital": ch not in ("branch","booth","retail_partner","cash","atm"),
    "channel_type": "digital" if ch not in ("branch","booth","retail_partner") else "physical",
} for i,ch in enumerate(CHANNELS)])
save_csv(dim_channel, BRONZE, "dim_channel")

# DIM_PRODUCT
products = [
    (1,"INTL_REMITTANCE","International Money Transfer","remittance",True,True),
    (2,"WALLET","Digital Wallet","wallet",True,True),
    (3,"MAMA_CARD","Mama Money Card","card",False,True),
    (4,"MKR_CARD","Mukuru Card","card",True,False),
    (5,"FAST_LOAN","Mukuru Fast Loan","lending",True,False),
    (6,"FUNERAL_COVER","Mukuru Funeral Cover","insurance",True,False),
    (7,"MUKURUPAY_BILL","MukuruPay Bill Payment","payments",True,False),
    (8,"MUKURUPAY_MERCH","MukuruPay Merchant","payments",True,False),
    (9,"USD_SAVINGS","Digital USD Savings","savings",True,True),
    (10,"AIRTIME","Airtime Purchase","utility",True,True),
    (11,"ELECTRICITY","Electricity Purchase","utility",True,True),
    (12,"CASH_SEND","Cash Send","transfer",True,True),
]
dim_product = pd.DataFrame(products, columns=[
    "product_sk","product_code","product_name","product_category",
    "mukuru_offers","mama_money_offers"])
save_csv(dim_product, BRONZE, "dim_product")

# DIM_PAYMENT_METHOD
dim_payment_method = pd.DataFrame([{
    "payment_method_sk": i+1,
    "method_code": m,
    "method_name": m.replace("_"," ").title(),
    "is_digital": m not in ("cash","voucher"),
    "processing_time_mins": random.choice([1,2,5,10,30,60,240,1440]),
} for i,m in enumerate(PAYMENT_METHODS)])
save_csv(dim_payment_method, BRONZE, "dim_payment_method")

# DIM_PAYOUT_METHOD
dim_payout_method = pd.DataFrame([{
    "payout_method_sk": i+1,
    "method_code": m,
    "method_name": m.replace("_"," ").title(),
    "is_instant": m in ("card_credit","mobile_wallet"),
    "typical_hours": random.choice([0,1,4,24,48]),
} for i,m in enumerate(PAYOUT_METHODS)])
save_csv(dim_payout_method, BRONZE, "dim_payout_method")

# DIM_TRANSFER_STATUS
dim_transfer_status = pd.DataFrame([{
    "status_sk": i+1,
    "status_code": s,
    "status_name": s.replace("_"," ").title(),
    "is_terminal": s in ("COMPLETED","FAILED","CANCELLED","REFUNDED"),
    "is_success": s == "COMPLETED",
    "status_category": ("terminal" if s in ("COMPLETED","FAILED","CANCELLED","REFUNDED")
                        else "compliance" if s == "COMPLIANCE_REVIEW"
                        else "in_progress"),
} for i,s in enumerate(TRANSFER_STATUSES)])
save_csv(dim_transfer_status, BRONZE, "dim_transfer_status")

print()

# ═══════════════════════════════════════════════════════════════════════════════
# 2. CUSTOMERS — 500K
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 2 — CUSTOMERS (500,000)")
print("=" * 60)

N_CUSTOMERS = 500_000
N_MKR = 300_000
N_MMY = 200_000

FIRST_NAMES = ["Thabo","Sipho","Nomsa","Zanele","Blessing","Chidi","Abena",
               "Fatima","Moses","Grace","Emmanuel","Priscilla","Tendai","Rudo",
               "Boniface","Aisha","Kofi","Amara","David","Sarah","John","Mary",
               "Peter","Elizabeth","James","Agnes","Michael","Charity","Robert",
               "Florence","Samuel","Patience","Daniel","Hope","Joseph","Mercy",
               "Charles","Ruth","George","Esther","William","Naomi","Edward",
               "Doris","Francis","Winnie","Henry","Betty","Anthony","Rose"]
LAST_NAMES  = ["Moyo","Dube","Ncube","Nyathi","Okafor","Mensah","Diallo",
               "Banda","Mwangi","Kariuki","Mutua","Wanjiku","Sithole","Ndlovu",
               "Mahlangu","Molefe","Khumalo","Mthembu","Mkhize","Zulu","Nkosi",
               "Cele","Mncwango","Ntuli","Ngcobo","Maphumulo","Gumede","Nxumalo",
               "Buthelezi","Shabalala","Mhlongo","Bhengu","Mthethwa","Luthuli",
               "Myeni","Madlala","Nzama","Sithebe","Mbatha","Mchunu","Zwane"]

def gen_customers(n, biz_key, id_start):
    rows = []
    for i in range(n):
        cid = id_start + i
        reg_dt = rand_date()
        seg = np.random.choice(SEGMENTS, p=[0.35,0.40,0.18,0.07])
        kyc = np.random.choice(KYCS, p=[0.05,0.30,0.50,0.15])
        age = random.randint(18, 65)
        country = np.random.choice(
            ["ZW","MZ","ZM","MW","TZ","KE","NG","GH","CD","UG","RW","ET","SN"],
            p=[0.25,0.15,0.10,0.08,0.08,0.07,0.05,0.04,0.04,0.04,0.04,0.03,0.03])
        rows.append({
            "customer_id": f"CUST-{cid:07d}",
            "business_key": biz_key,
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "date_of_birth": (datetime.now() - timedelta(days=365*age + random.randint(0,364))).date().isoformat(),
            "age_years": age,
            "gender": random.choice(["M","F","M","F","M","F","M","U"]),
            "nationality": country,
            "residence_country": "ZA",
            "preferred_language": np.random.choice(LANGUAGES, p=[0.35,0.12,0.10,0.08,0.07,0.06,0.05,0.05,0.04,0.03,0.03,0.02]),
            "mobile_number_token": f"MSISDN-{random.randint(100000000,999999999)}",
            "email_hash": uuid.uuid4().hex[:24],
            "registration_datetime": reg_dt.isoformat(),
            "registration_channel": random.choice(CHANNELS),
            "kyc_level": kyc,
            "kyc_completed_date": (reg_dt + timedelta(days=random.randint(0,30))).date().isoformat() if kyc != "LEVEL_0" else None,
            "customer_status": np.random.choice(["ACTIVE","ACTIVE","ACTIVE","SUSPENDED","CLOSED","DORMANT"],
                                                p=[0.70,0.70,0.70,0.05,0.03,0.22]/np.array([0.70,0.70,0.70,0.05,0.03,0.22]).sum()),
            "risk_band": np.random.choice(RISK_BANDS, p=[0.60,0.28,0.09,0.03]),
            "customer_segment": seg,
            "monthly_income_band": np.random.choice(
                ["< R5k","R5k-R10k","R10k-R20k","R20k-R50k","R50k+"],
                p=[0.20,0.30,0.28,0.15,0.07]),
            "employer_type": np.random.choice(
                ["informal","formal_private","formal_govt","self_employed","unemployed"],
                p=[0.30,0.38,0.12,0.13,0.07]),
            "has_sa_id": random.random() < 0.55,
            "has_passport": random.random() < 0.70,
            "is_marketing_opt_in": random.random() < 0.62,
            "acquisition_source": np.random.choice(
                ["organic","referral","google_ads","facebook","outdoor","branch_walk_in","agent"],
                p=[0.18,0.25,0.15,0.12,0.08,0.12,0.10]),
            "lifetime_transfers": 0,  # to be updated
            "scd_version": 1,
            "scd_start_date": reg_dt.date().isoformat(),
            "scd_end_date": None,
            "is_current": True,
        })
    return rows

print("  Generating Mukuru customers...")
mkr_custs = gen_customers(N_MKR, "MKR", 1)
print("  Generating Mama Money customers...")
mmy_custs = gen_customers(N_MMY, "MMY", N_MKR+1)

all_custs = mkr_custs + mmy_custs
dim_customer = pd.DataFrame(all_custs)
dim_customer["customer_sk"] = range(1, len(dim_customer)+1)
save_csv(dim_customer, BRONZE, "dim_customer")

# Customer ID lookup
cust_ids = dim_customer["customer_id"].tolist()
mkr_cust_ids = [c["customer_id"] for c in mkr_custs]
mmy_cust_ids = [c["customer_id"] for c in mmy_custs]

print()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. RECIPIENTS — 1M
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 3 — RECIPIENTS (1,000,000)")
print("=" * 60)

N_RECIPIENTS = 1_000_000
recipients = []
for i in range(N_RECIPIENTS):
    cust = random.choice(cust_ids)
    biz  = "MKR" if cust in mkr_cust_ids[:N_MKR] else "MMY"
    cntry = np.random.choice(
        ["ZW","MZ","ZM","MW","TZ","KE","NG","GH","CD","UG","RW","ET","SN"],
        p=[0.25,0.15,0.10,0.08,0.08,0.07,0.05,0.04,0.04,0.04,0.04,0.03,0.03])
    recipients.append({
        "recipient_id": f"RECIP-{i+1:08d}",
        "sender_customer_id": cust,
        "business_key": biz,
        "first_name": random.choice(FIRST_NAMES),
        "last_name": random.choice(LAST_NAMES),
        "relationship": np.random.choice(
            ["spouse","parent","child","sibling","friend","colleague","other"],
            p=[0.22,0.20,0.18,0.18,0.10,0.07,0.05]),
        "receive_country": cntry,
        "preferred_payout_method": random.choice(PAYOUT_METHODS),
        "mobile_token": f"MOB-{random.randint(1000000,9999999)}",
        "bank_account_token": f"BANK-{uuid.uuid4().hex[:12]}" if random.random() < 0.4 else None,
        "wallet_token": f"WALL-{uuid.uuid4().hex[:12]}" if random.random() < 0.5 else None,
        "is_verified": random.random() < 0.75,
        "created_date": rand_date().date().isoformat(),
        "transfer_count": 0,
    })
dim_recipient = pd.DataFrame(recipients)
dim_recipient["recipient_sk"] = range(1, len(dim_recipient)+1)
save_csv(dim_recipient, BRONZE, "dim_recipient")

recip_ids = dim_recipient["recipient_id"].tolist()
# Build customer → recipient index
cust_to_recips = {}
for r in recipients:
    cust_to_recips.setdefault(r["sender_customer_id"], []).append(r["recipient_id"])

print()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. FX RATES — ~100K rows
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 4 — FX RATES (hourly, ~95K rows)")
print("=" * 60)

# Base market rates (ZAR base → receive currency)
BASE_FX = {
    "ZWL": 0.42, "MZN": 3.20, "ZMW": 0.88, "MWK": 62.0, "TZS": 155.0,
    "KES": 5.50, "NGN": 85.0, "GHS": 0.55, "CDF": 16.5, "UGX": 230.0,
    "RWF": 8.20, "ETB": 4.10, "XOF": 34.0, "GBP": 0.043, "USD": 0.052,
    "AUD": 0.080, "NZD": 0.087, "CNY": 0.38,
}

fx_rows = []
rate_id = 1
for corr in corridors:
    scy = corr["send_currency"]
    dcy = corr["receive_currency"]
    if dcy == scy:
        continue
    base_rate = BASE_FX.get(dcy, 1.0)
    # Hourly rates across the period
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
save_csv(fact_fx_rate, BRONZE, "fact_fx_rate")

# Build lookup: corridor → latest market rate
latest_fx = {}
for c in corridors:
    code = c["corridor_code"]
    subset = fact_fx_rate[fact_fx_rate["corridor_code"] == code]
    if not subset.empty:
        latest_fx[code] = subset.iloc[-1][["market_rate","customer_rate","fx_spread_pct"]].to_dict()

print()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. TRANSFER ORDERS — 5M
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 5 — TRANSFER ORDERS (5,000,000)")
print("=" * 60)

N_TRANSFERS = 5_000_000
CHUNK = 250_000

def make_transfers(n, id_start):
    rows = []
    for i in range(n):
        tid = id_start + i
        # Pick business weighted
        biz = np.random.choice(["MKR","MMY"], p=[0.60,0.40])
        if biz == "MKR":
            cust = random.choice(mkr_cust_ids)
            valid_corrs = [c for c in corridors if c["mukuru_active"]]
        else:
            cust = random.choice(mmy_cust_ids)
            valid_corrs = [c for c in corridors if c["mama_money_active"]]

        corr = random.choice(valid_corrs)
        recv_country = corr["receive_country"]

        # Recipient
        recips = cust_to_recips.get(cust)
        recip  = random.choice(recips) if recips else random.choice(recip_ids[:100000])

        created = rand_date()
        cdate   = created.date().isoformat()

        # Send amount in ZAR (realistic distribution)
        amount_zar = round(random.lognormvariate(math.log(1500), 0.8), 2)
        amount_zar = max(50, min(amount_zar, 50000))

        fx_info = latest_fx.get(corr["corridor_code"], {"market_rate":1,"customer_rate":0.95,"fx_spread_pct":5})
        cust_rate   = fx_info["customer_rate"]
        market_rate = fx_info["market_rate"]
        recv_amount = round(amount_zar * cust_rate, 2)
        fee_pct = random.uniform(0.02, 0.08)
        fee     = round(amount_zar * fee_pct, 2)
        vat     = round(fee * 0.15, 2)
        fx_margin = round(amount_zar * (market_rate - cust_rate) / market_rate, 2) if market_rate else 0
        partner_cost = round(amount_zar * random.uniform(0.005,0.025), 2)
        gross_rev   = fee + fx_margin
        net_rev     = gross_rev - partner_cost

        # Status weighted
        status = np.random.choice(
            ["COMPLETED","COMPLETED","COMPLETED","FAILED","CANCELLED","REFUNDED"],
            p=[0.82,0.82,0.82,0.06,0.08,0.02]/np.array([0.82,0.82,0.82,0.06,0.08,0.02]).sum()
        ) if random.random() < 0.9 else "AWAITING_PAYMENT"
        # Normalise
        status = np.random.choice(["COMPLETED","FAILED","CANCELLED","REFUNDED","AWAITING_PAYMENT"],
                                   p=[0.78,0.08,0.10,0.02,0.02])

        completed_dt = rand_date_after(created, 5) if status == "COMPLETED" else None
        comp_mins    = int((completed_dt - created).total_seconds()/60) if completed_dt else None

        channel = np.random.choice(
            CHANNELS,
            p=[0.30,0.15,0.10,0.12,0.05,0.04,0.06,0.03,0.02,0.13])
        pay_method = np.random.choice(PAYMENT_METHODS,
                p=[0.25,0.20,0.05,0.15,0.12,0.12,0.05,0.06])
        pout_method = random.choice(PAYOUT_METHODS)

        rows.append({
            "transfer_id":     f"TFR-{tid:09d}",
            "transfer_reference": uuid.uuid4().hex[:12].upper(),
            "business_key":    biz,
            "sender_customer_id": cust,
            "recipient_id":    recip,
            "corridor_code":   corr["corridor_code"],
            "send_country":    corr["send_country"],
            "receive_country": recv_country,
            "send_currency":   corr["send_currency"],
            "receive_currency": corr["receive_currency"],
            "channel":         channel,
            "payment_method":  pay_method,
            "payout_method":   pout_method,
            "created_datetime": created.isoformat(),
            "created_date_key": date_sk_map.get(cdate,0),
            "completed_datetime": completed_dt.isoformat() if completed_dt else None,
            "completed_date_key": date_sk_map.get(completed_dt.date().isoformat(),0) if completed_dt else None,
            "transfer_status": status,
            "send_amount_zar": amount_zar,
            "receive_amount":  recv_amount,
            "transfer_fee_zar": fee,
            "vat_zar":         vat,
            "fx_margin_zar":   fx_margin,
            "partner_cost_zar": partner_cost,
            "gross_revenue_zar": round(gross_rev, 2),
            "net_revenue_zar":   round(net_rev, 2),
            "market_fx_rate":    market_rate,
            "customer_fx_rate":  cust_rate,
            "fx_spread_pct":     round(fx_info["fx_spread_pct"], 4),
            "payment_attempts":  random.randint(1,3),
            "payout_attempts":   random.randint(1,3) if status == "COMPLETED" else 0,
            "completion_minutes": comp_mins,
            "is_completed":   status=="COMPLETED",
            "is_failed":      status=="FAILED",
            "is_cancelled":   status=="CANCELLED",
            "is_refunded":    status=="REFUNDED",
            "is_first_transfer": i < 50000,
            "is_repeat_customer": i >= 50000,
            "is_suspected_fraud": random.random() < 0.008,
        })
    return rows

all_transfers = []
for chunk_i in range(0, N_TRANSFERS, CHUNK):
    chunk_rows = make_transfers(CHUNK, chunk_i+1)
    all_transfers.extend(chunk_rows)
    pct = (chunk_i+CHUNK)*100//N_TRANSFERS
    print(f"  Transfers: {chunk_i+CHUNK:,}/{N_TRANSFERS:,} ({pct}%)")

fact_transfer = pd.DataFrame(all_transfers)
save_csv(fact_transfer, BRONZE, "fact_remittance_transfer")

transfer_ids = fact_transfer["transfer_id"].tolist()
transfer_created = dict(zip(fact_transfer["transfer_id"], fact_transfer["created_datetime"]))
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 6. TRANSFER STATUS HISTORY — ~15M rows
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 6 — TRANSFER STATUS HISTORY (~15M rows)")
print("=" * 60)

STATUS_FLOW = {
    "COMPLETED": ["CREATED","QUOTED","AWAITING_PAYMENT","PAID","PROCESSING",
                  "SENT_TO_PARTNER","AVAILABLE_FOR_COLLECTION","COMPLETED"],
    "FAILED":    ["CREATED","QUOTED","AWAITING_PAYMENT","PAID","COMPLIANCE_REVIEW","FAILED"],
    "CANCELLED": ["CREATED","QUOTED","AWAITING_PAYMENT","CANCELLED"],
    "REFUNDED":  ["CREATED","QUOTED","AWAITING_PAYMENT","PAID","PROCESSING","REFUNDED"],
    "AWAITING_PAYMENT": ["CREATED","QUOTED","AWAITING_PAYMENT"],
}

hist_rows = []
hist_id = 1
SAMPLE_IDS = random.sample(transfer_ids, min(1_500_000, len(transfer_ids)))

for tid in SAMPLE_IDS:
    row = fact_transfer[fact_transfer["transfer_id"]==tid].iloc[0]
    status = row["transfer_status"]
    flow = STATUS_FLOW.get(status, ["CREATED","COMPLETED"])
    dt = datetime.fromisoformat(row["created_datetime"])
    for s in flow:
        hist_rows.append({
            "status_history_id": hist_id,
            "transfer_id": tid,
            "business_key": row["business_key"],
            "status_code": s,
            "status_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(),0),
            "elapsed_minutes_from_created": int((dt - datetime.fromisoformat(row["created_datetime"])).total_seconds()/60),
            "system_user": f"SYS-{random.randint(1,50)}",
            "notes": None,
        })
        hist_id += 1
        dt = dt + timedelta(minutes=random.randint(1,240))

fact_status_history = pd.DataFrame(hist_rows)
save_csv(fact_status_history, BRONZE, "fact_transfer_status_history")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 7. PAYMENTS (funding) — 5.5M rows
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 7 — PAYMENTS (5,500,000)")
print("=" * 60)

payments = []
pid = 1
completed_ids = fact_transfer[fact_transfer["is_completed"]==True]["transfer_id"].tolist()
all_ids = transfer_ids

for tid in all_ids:
    row = fact_transfer[fact_transfer["transfer_id"]==tid].iloc[0]
    n_attempts = int(row["payment_attempts"])
    created_dt = datetime.fromisoformat(row["created_datetime"])
    for a in range(n_attempts):
        is_last = a == n_attempts - 1
        success = is_last and row["is_completed"]
        dt = created_dt + timedelta(minutes=random.randint(1,120)*a)
        payments.append({
            "payment_id": f"PAY-{pid:09d}",
            "transfer_id": tid,
            "business_key": row["business_key"],
            "sender_customer_id": row["sender_customer_id"],
            "payment_method": row["payment_method"],
            "payment_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(),0),
            "amount_zar": row["send_amount_zar"],
            "fee_zar": row["transfer_fee_zar"],
            "total_charged_zar": round(row["send_amount_zar"] + row["transfer_fee_zar"], 2),
            "attempt_number": a+1,
            "payment_status": "SUCCESS" if success else ("DECLINED" if a < n_attempts-1 else "FAILED"),
            "decline_reason": random.choice(["INSUFFICIENT_FUNDS","CARD_BLOCKED","LIMIT_EXCEEDED",None,None,None]) if not success else None,
            "payment_reference": uuid.uuid4().hex[:16].upper(),
            "gateway_code": f"GW-{random.randint(1,5)}",
        })
        pid += 1
        if pid % 1_000_000 == 0:
            print(f"  Payments: {pid:,}")

fact_payment = pd.DataFrame(payments)
save_csv(fact_payment, BRONZE, "fact_payment")
del payments
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 8. PAYOUTS — 4.5M
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 8 — PAYOUTS (4,500,000)")
print("=" * 60)

payouts = []
poid = 1
for tid in completed_ids[:2_000_000]:
    row = fact_transfer[fact_transfer["transfer_id"]==tid].iloc[0]
    n_att = int(row["payout_attempts"])
    created_dt = datetime.fromisoformat(row["created_datetime"])
    for a in range(max(1, n_att)):
        is_last = a == n_att-1
        dt = created_dt + timedelta(hours=random.randint(1,48)*(a+1))
        payouts.append({
            "payout_id": f"PO-{poid:09d}",
            "transfer_id": tid,
            "business_key": row["business_key"],
            "recipient_id": row["recipient_id"],
            "receive_country": row["receive_country"],
            "payout_method": row["payout_method"],
            "payout_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(),0),
            "amount_receive_currency": row["receive_amount"],
            "amount_zar_equivalent": row["send_amount_zar"],
            "partner_code": f"PARTNER-{random.randint(1,30):02d}",
            "partner_location_id": f"LOC-{random.randint(1,5000):05d}",
            "attempt_number": a+1,
            "payout_status": "SUCCESS" if is_last else "FAILED",
            "failure_reason": random.choice(["PARTNER_OFFLINE","ID_MISMATCH","LIMIT_EXCEEDED",None]) if not is_last else None,
            "collection_code": uuid.uuid4().hex[:8].upper() if row["payout_method"]=="cash_collection" else None,
            "collected_datetime": (dt + timedelta(hours=random.randint(1,72))).isoformat() if row["payout_method"]=="cash_collection" and is_last else None,
        })
        poid += 1
        if poid % 1_000_000 == 0:
            print(f"  Payouts: {poid:,}")

fact_payout = pd.DataFrame(payouts)
save_csv(fact_payout, BRONZE, "fact_payout")
del payouts
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 9. WALLET LEDGER — 10M rows
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 9 — WALLET LEDGER (10,000,000)")
print("=" * 60)

WALLET_ENTRY_TYPES = [
    ("CASH_IN","debit","wallet_top_up"),
    ("TRANSFER_OUT","credit","remittance"),
    ("TRANSFER_IN","debit","inbound_remittance"),
    ("CARD_LOAD","credit","card_funding"),
    ("USD_BUY","credit","fx_conversion"),
    ("USD_SELL","debit","fx_conversion"),
    ("FEE_CHARGE","credit","fee"),
    ("REFUND","debit","refund"),
    ("SALARY_DEPOSIT","debit","salary"),
    ("AIRTIME_BUY","credit","utility"),
    ("ELECTRICITY_BUY","credit","utility"),
    ("CASH_SEND","credit","cash_send"),
]

wallet_rows = []
wid = 1
N_WALLETS = 250_000
wallet_cust_ids = random.sample(cust_ids, N_WALLETS)

for cust in wallet_cust_ids:
    biz = "MKR" if cust in mkr_cust_ids else "MMY"
    n_entries = random.randint(10, 120)
    balance = 0.0
    reg_dt = datetime.fromisoformat(
        dim_customer[dim_customer["customer_id"]==cust]["registration_datetime"].values[0])
    for e in range(n_entries):
        entry_type, direction, category = random.choice(WALLET_ENTRY_TYPES)
        amount = round(abs(random.lognormvariate(math.log(500), 0.9)), 2)
        amount = max(10, min(amount, 20000))
        if direction == "debit":
            balance += amount
        else:
            balance = max(0, balance - amount)
        entry_dt = rand_date_after(reg_dt, 1800)
        entry_dt = min(entry_dt, END_DATE)
        wallet_rows.append({
            "ledger_id": f"WL-{wid:010d}",
            "wallet_id": f"WALL-{hash(cust)%10000000:07d}",
            "customer_id": cust,
            "business_key": biz,
            "entry_type": entry_type,
            "entry_direction": direction,
            "amount_zar": amount,
            "running_balance_zar": round(balance, 2),
            "entry_datetime": entry_dt.isoformat(),
            "date_key": date_sk_map.get(entry_dt.date().isoformat(),0),
            "reference_id": f"REF-{random.randint(1,9999999):07d}",
            "category": category,
            "channel": random.choice(CHANNELS),
            "description": f"{entry_type.replace('_',' ').title()}",
        })
        wid += 1
    if wid % 2_000_000 == 0:
        print(f"  Wallet ledger: {wid:,}")

fact_wallet_ledger = pd.DataFrame(wallet_rows)
save_csv(fact_wallet_ledger, BRONZE, "fact_wallet_ledger")
del wallet_rows
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 10. CARD TRANSACTIONS — 3M
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 10 — CARD TRANSACTIONS (3,000,000)")
print("=" * 60)

MERCHANT_CATEGORIES = ["grocery","fuel","pharmacy","clothing","airtime","electricity",
                        "restaurant","transport","hardware","electronics","online","atm_withdrawal"]

card_rows = []
N_CARD_CUSTS = 120_000
card_cust_ids = random.sample(cust_ids, N_CARD_CUSTS)
cid_card = 1
for cust in card_cust_ids:
    biz = "MKR" if cust in mkr_cust_ids else "MMY"
    card_type = "MUKURU_CARD" if biz == "MKR" else "MAMA_CARD"
    n_txns = random.randint(5, 60)
    for _ in range(n_txns):
        dt = rand_date()
        amount = round(abs(random.lognormvariate(math.log(300), 0.9)), 2)
        amount = max(5, min(amount, 5000))
        mcc = random.choice(MERCHANT_CATEGORIES)
        card_rows.append({
            "card_txn_id": f"CTX-{cid_card:09d}",
            "card_account_id": f"CARD-{hash(cust)%1000000:06d}",
            "customer_id": cust,
            "business_key": biz,
            "card_type": card_type,
            "merchant_category": mcc,
            "merchant_name": f"MERCHANT-{random.randint(1,10000):05d}",
            "merchant_country": "ZA" if random.random() < 0.85 else random.choice(["ZW","MZ","ZM"]),
            "transaction_datetime": dt.isoformat(),
            "date_key": date_sk_map.get(dt.date().isoformat(),0),
            "amount_zar": amount,
            "transaction_type": np.random.choice(
                ["purchase","atm_withdrawal","refund","salary_credit"],
                p=[0.70,0.12,0.08,0.10]),
            "channel": np.random.choice(["card_swipe","contactless","online","atm"],
                                         p=[0.40,0.30,0.20,0.10]),
            "authorisation_code": uuid.uuid4().hex[:6].upper(),
            "transaction_status": np.random.choice(["APPROVED","DECLINED","REVERSED"],
                                                    p=[0.88,0.09,0.03]),
            "decline_reason": random.choice(["INSUFFICIENT_FUNDS","WRONG_PIN","EXPIRED",None]) if random.random()<0.09 else None,
            "is_international": random.random() < 0.05,
            "is_contactless": random.random() < 0.30,
            "is_fraud_flagged": random.random() < 0.006,
        })
        cid_card += 1
    if cid_card % 1_000_000 == 0:
        print(f"  Card txns: {cid_card:,}")

fact_card_txn = pd.DataFrame(card_rows)
save_csv(fact_card_txn, BRONZE, "fact_card_transaction")
del card_rows
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 11. MUKURU LOANS — 200K applications
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 11 — MUKURU LOANS (200,000)")
print("=" * 60)

loan_rows = []
loan_repay_rows = []
loan_id = 1
repay_id = 1
LOAN_CUSTS = random.sample(mkr_cust_ids, 80_000)

for cust in LOAN_CUSTS:
    n_apps = random.randint(1,4)
    app_dt = rand_date()
    for _ in range(n_apps):
        decision = np.random.choice(["APPROVED","DECLINED","PENDING"],p=[0.55,0.38,0.07])
        principal = round(random.uniform(500,10000),2) if decision=="APPROVED" else round(random.uniform(500,10000),2)
        term_months = random.choice([1,2,3,6])
        interest_rate = random.uniform(0.05,0.20)
        monthly_rate = interest_rate/12
        monthly_payment = round(principal * monthly_rate / (1-(1+monthly_rate)**-term_months),2) if decision=="APPROVED" else 0
        pd_score = round(random.betavariate(2,8),4)

        loan_rows.append({
            "loan_id": f"LOAN-{loan_id:08d}",
            "customer_id": cust,
            "business_key": "MKR",
            "application_datetime": app_dt.isoformat(),
            "date_key": date_sk_map.get(app_dt.date().isoformat(),0),
            "decision": decision,
            "decision_datetime": (app_dt+timedelta(minutes=random.randint(5,1440))).isoformat(),
            "loan_purpose": np.random.choice(["emergency","school_fees","home","business","medical","other"],p=[0.30,0.20,0.15,0.15,0.12,0.08]),
            "principal_zar": principal,
            "interest_rate_annual_pct": round(interest_rate*100,2),
            "term_months": term_months,
            "monthly_payment_zar": monthly_payment,
            "total_repayable_zar": round(monthly_payment*term_months,2) if decision=="APPROVED" else 0,
            "disbursement_method": "MUKURU_CARD",
            "disbursement_datetime": (app_dt+timedelta(hours=random.randint(1,48))).isoformat() if decision=="APPROVED" else None,
            "loan_status": np.random.choice(["ACTIVE","SETTLED","DEFAULTED","WRITTEN_OFF"],p=[0.40,0.45,0.10,0.05]) if decision=="APPROVED" else "DECLINED",
            "probability_of_default": pd_score,
            "expected_credit_loss_zar": round(principal*pd_score,2),
            "days_past_due": random.randint(0,180) if decision=="APPROVED" and random.random()<0.15 else 0,
            "card_account_age_days": random.randint(30,1800),
            "avg_monthly_card_spend_zar": round(random.uniform(200,5000),2),
            "salary_indicator": random.random()<0.6,
            "previous_loans": random.randint(0,5),
            "previous_loans_repaid": random.randint(0,5),
        })
        loan_id += 1

        # Repayments for approved
        if decision == "APPROVED":
            disburse_dt = app_dt + timedelta(hours=random.randint(1,48))
            for m in range(term_months):
                due_dt = disburse_dt + timedelta(days=30*(m+1))
                paid = random.random() < 0.85
                repay_rows_entry = {
                    "repayment_id": f"REPAY-{repay_id:09d}",
                    "loan_id": f"LOAN-{loan_id-1:08d}",
                    "customer_id": cust,
                    "business_key": "MKR",
                    "instalment_number": m+1,
                    "due_date": due_dt.date().isoformat(),
                    "paid_datetime": (due_dt+timedelta(days=random.randint(-5,15))).isoformat() if paid else None,
                    "amount_due_zar": monthly_payment,
                    "amount_paid_zar": monthly_payment if paid else round(monthly_payment*random.uniform(0,0.9),2),
                    "payment_status": "PAID" if paid else "MISSED",
                    "days_past_due": max(0,random.randint(0,30)) if not paid else 0,
                }
                loan_repay_rows.append(repay_rows_entry)
                repay_id += 1

        app_dt = app_dt + timedelta(days=random.randint(60,365))

fact_loans = pd.DataFrame(loan_rows)
save_csv(fact_loans, BRONZE, "fact_loan_application")
fact_loan_repay = pd.DataFrame(loan_repay_rows)
save_csv(fact_loan_repay, BRONZE, "fact_loan_repayment")
del loan_repay_rows
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 12. MUKURU INSURANCE — 80K policies
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 12 — MUKURU INSURANCE (80,000 policies)")
print("=" * 60)

insur_rows = []
claim_rows = []
iid = 1
clid = 1
INSUR_CUSTS = random.sample(mkr_cust_ids, 40_000)

FUNERAL_PLANS = [
    ("BASIC",150,35000,4),("STANDARD",250,75000,6),
    ("EXTENDED",400,120000,8),("PREMIER",600,200000,12)
]

for cust in INSUR_CUSTS:
    plan = random.choice(FUNERAL_PLANS)
    start = rand_date()
    status = np.random.choice(["ACTIVE","LAPSED","CANCELLED"],p=[0.70,0.20,0.10])
    insur_rows.append({
        "policy_id": f"POL-{iid:08d}",
        "customer_id": cust,
        "business_key": "MKR",
        "product_name": "Mukuru Funeral Cover",
        "plan_name": plan[0],
        "monthly_premium_zar": plan[1],
        "cover_amount_zar": plan[2],
        "num_lives_covered": plan[3],
        "policy_start_date": start.date().isoformat(),
        "policy_status": status,
        "lapse_date": (start+timedelta(days=random.randint(30,730))).date().isoformat() if status!="ACTIVE" else None,
        "total_premiums_paid_zar": round(plan[1]*random.randint(1,48),2),
        "beneficiary_name": random.choice(FIRST_NAMES)+" "+random.choice(LAST_NAMES),
        "repatriation_country": np.random.choice(["ZW","MZ","ZM","MW"],p=[0.50,0.20,0.15,0.15]),
    })
    iid += 1

    # Claims
    if random.random() < 0.08 and status == "ACTIVE":
        claim_dt = start + timedelta(days=random.randint(60,730))
        approved = random.random() < 0.80
        claim_rows.append({
            "claim_id": f"CLM-{clid:07d}",
            "policy_id": f"POL-{iid-1:08d}",
            "customer_id": cust,
            "business_key": "MKR",
            "claim_datetime": claim_dt.isoformat(),
            "date_key": date_sk_map.get(claim_dt.date().isoformat(),0),
            "claim_type": random.choice(["MAIN_MEMBER","SPOUSE","CHILD","PARENT","EXTENDED"]),
            "claimed_amount_zar": plan[2],
            "decision": "APPROVED" if approved else "REPUDIATED",
            "paid_amount_zar": plan[2] if approved else 0,
            "turnaround_days": random.randint(1,30),
            "repudiation_reason": random.choice(["EXCLUSION","FRAUD","WAITING_PERIOD"]) if not approved else None,
        })
        clid += 1

fact_insurance = pd.DataFrame(insur_rows)
fact_claims    = pd.DataFrame(claim_rows)
save_csv(fact_insurance, BRONZE, "fact_insurance_policy")
save_csv(fact_claims,    BRONZE, "fact_insurance_claim")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 13. DIGITAL USD SAVINGS — Mama Money
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 13 — DIGITAL USD SAVINGS (Mama Money, 50K)")
print("=" * 60)

usd_rows = []
USD_CUSTS = random.sample(mmy_cust_ids, 50_000)
usdc_price = 1.0  # USDC pegged

for cust in USD_CUSTS:
    opens = rand_date()
    balance_usdc = round(random.uniform(0, 5000), 2)
    usd_rows.append({
        "savings_id": f"USD-{hash(cust)%10000000:07d}",
        "customer_id": cust,
        "business_key": "MMY",
        "account_opened_date": opens.date().isoformat(),
        "account_status": np.random.choice(["ACTIVE","DORMANT","CLOSED"],p=[0.75,0.15,0.10]),
        "current_balance_usdc": balance_usdc,
        "current_balance_usd": balance_usdc,
        "current_balance_zar": round(balance_usdc / 0.052, 2),
        "total_purchased_usdc": round(balance_usdc + random.uniform(0,2000), 2),
        "total_sold_usdc": round(random.uniform(0,1000), 2),
        "last_purchase_date": (opens+timedelta(days=random.randint(1,500))).date().isoformat(),
        "underlying_asset": "USDC",
        "is_usdc_backed": True,
    })

fact_usd_savings = pd.DataFrame(usd_rows)
save_csv(fact_usd_savings, BRONZE, "fact_usd_savings")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# 14. PARTNER / LOCATION
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 14 — PARTNERS & LOCATIONS")
print("=" * 60)

partners = []
for i in range(1,51):
    country = random.choice(["ZW","MZ","ZM","MW","TZ","KE","NG","GH","CD","UG"])
    partners.append({
        "partner_sk": i,
        "partner_id": f"PARTNER-{i:02d}",
        "partner_name": f"Partner {i} Ltd",
        "partner_type": np.random.choice(["mobile_money_op","bank","cash_agent","card_issuer"],p=[0.35,0.30,0.25,0.10]),
        "country": country,
        "is_active": random.random()<0.85,
        "commission_pct": round(random.uniform(0.5,3.5),2),
        "settlement_days": random.choice([1,2,3,5]),
        "volume_last_30d_zar": round(random.uniform(500000,50000000),2),
        "mukuru_partner": random.random()<0.8,
        "mama_money_partner": random.random()<0.6,
    })
dim_partner = pd.DataFrame(partners)
save_csv(dim_partner, BRONZE, "dim_partner")

locations = []
for i in range(1,5001):
    country = random.choice(["ZW","MZ","ZM","MW","TZ","KE","NG","GH","CD","UG","ZA"])
    lat = round(random.uniform(-34,-5),6)
    lon = round(random.uniform(12,40),6)
    locations.append({
        "location_sk": i,
        "location_id": f"LOC-{i:05d}",
        "location_name": f"Location {i}",
        "location_type": np.random.choice(["branch","booth","retail","atm","partner_outlet"],p=[0.10,0.15,0.40,0.15,0.20]),
        "country": country,
        "city": f"City-{random.randint(1,100)}",
        "latitude": lat,
        "longitude": lon,
        "is_active": random.random()<0.80,
        "partner_id": f"PARTNER-{random.randint(1,50):02d}",
    })
dim_location = pd.DataFrame(locations)
save_csv(dim_location, BRONZE, "dim_location")

print()
print("=" * 60)
print("PHASE 1 COMPLETE — ALL RAW/BRONZE DATA GENERATED")
print("=" * 60)

total = (
    len(dim_customer) + len(dim_recipient) + len(fact_transfer) +
    len(fact_status_history) + len(fact_payment) + len(fact_payout) +
    len(fact_wallet_ledger) + len(fact_card_txn) + len(fact_loans) +
    len(fact_loan_repay) + len(fact_insurance) + len(fact_claims) +
    len(fact_usd_savings) + len(fact_fx_rate)
)
print(f"\nTotal rows generated: {total:,}")
