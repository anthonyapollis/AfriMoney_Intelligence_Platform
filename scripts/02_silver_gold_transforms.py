"""
African Fintech Intelligence Platform
Phase 2: Silver & Gold Layer Transforms
Builds analytical mart tables from Bronze
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE   = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
BRONZE = BASE / "data" / "bronze"
SILVER = BASE / "data" / "silver"
GOLD   = BASE / "data" / "gold"

def save(df, path, name):
    fp = Path(path) / f"{name}.csv"
    df.to_csv(fp, index=False)
    print(f"  [SAVED] {name}.csv  ({len(df):,} rows)")
    return fp

print("Loading bronze tables...")
transfers   = pd.read_csv(BRONZE / "fact_remittance_transfer.csv", low_memory=False)
customers   = pd.read_csv(BRONZE / "dim_customer.csv", low_memory=False)
recipients  = pd.read_csv(BRONZE / "dim_recipient.csv", low_memory=False)
fx_rates    = pd.read_csv(BRONZE / "fact_fx_rate.csv", low_memory=False)
wallets     = pd.read_csv(BRONZE / "fact_wallet_ledger.csv", low_memory=False)
cards       = pd.read_csv(BRONZE / "fact_card_transaction.csv", low_memory=False)
loans       = pd.read_csv(BRONZE / "fact_loan_application.csv", low_memory=False)
loan_repay  = pd.read_csv(BRONZE / "fact_loan_repayment.csv", low_memory=False)
insurance   = pd.read_csv(BRONZE / "fact_insurance_policy.csv", low_memory=False)
claims      = pd.read_csv(BRONZE / "fact_insurance_claim.csv", low_memory=False)
usd         = pd.read_csv(BRONZE / "fact_usd_savings.csv", low_memory=False)
payouts     = pd.read_csv(BRONZE / "fact_payout.csv", low_memory=False)
dim_date    = pd.read_csv(BRONZE / "dim_date.csv")
print("  All tables loaded.\n")

# ── Parse dates ────────────────────────────────────────────────────────────────
transfers["created_date"] = pd.to_datetime(transfers["created_datetime"]).dt.date
transfers["created_month"] = pd.to_datetime(transfers["created_datetime"]).dt.to_period("M").astype(str)
transfers["created_year"]  = pd.to_datetime(transfers["created_datetime"]).dt.year

# ══════════════════════════════════════════════════════════════════════════════
# SILVER: STG_CUSTOMER (enriched)
# ══════════════════════════════════════════════════════════════════════════════
print("Building Silver layer...")

# Customer transfer stats
cust_stats = transfers.groupby("sender_customer_id").agg(
    total_transfers=("transfer_id","count"),
    completed_transfers=("is_completed","sum"),
    total_send_zar=("send_amount_zar","sum"),
    avg_send_zar=("send_amount_zar","mean"),
    total_fee_zar=("transfer_fee_zar","sum"),
    total_revenue_zar=("net_revenue_zar","sum"),
    first_transfer_date=("created_datetime","min"),
    last_transfer_date=("created_datetime","max"),
).reset_index()
cust_stats.columns = ["customer_id"] + list(cust_stats.columns[1:])

stg_customer = customers.merge(cust_stats, on="customer_id", how="left")
stg_customer["total_transfers"] = stg_customer["total_transfers"].fillna(0).astype(int)
stg_customer["completed_transfers"] = stg_customer["completed_transfers"].fillna(0).astype(int)
stg_customer["success_rate"] = (stg_customer["completed_transfers"] / stg_customer["total_transfers"].clip(lower=1)).round(4)
stg_customer["is_active_sender"] = stg_customer["total_transfers"] > 0
stg_customer["is_repeat_sender"] = stg_customer["completed_transfers"] >= 2
save(stg_customer, SILVER, "stg_customer")

# ══════════════════════════════════════════════════════════════════════════════
# SILVER: STG_TRANSFER_LIFECYCLE
# ══════════════════════════════════════════════════════════════════════════════
stg_transfer = transfers.copy()
# Revenue categories
stg_transfer["revenue_band"] = pd.cut(
    stg_transfer["net_revenue_zar"],
    bins=[-np.inf, 0, 50, 150, 300, np.inf],
    labels=["negative","low","medium","high","premium"])
stg_transfer["send_amount_band"] = pd.cut(
    stg_transfer["send_amount_zar"],
    bins=[0,500,1000,2000,5000,np.inf],
    labels=["micro","small","medium","large","xlarge"])
save(stg_transfer, SILVER, "stg_transfer_lifecycle")

print()

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_REMITTANCE — Monthly corridor summary
# ══════════════════════════════════════════════════════════════════════════════
print("Building Gold Marts...")

mart_remit_monthly = transfers[transfers["is_completed"]==True].groupby(
    ["business_key","corridor_code","created_month","channel","payment_method","payout_method"]
).agg(
    transfer_count=("transfer_id","count"),
    total_send_zar=("send_amount_zar","sum"),
    total_fee_zar=("transfer_fee_zar","sum"),
    total_fx_margin_zar=("fx_margin_zar","sum"),
    total_partner_cost_zar=("partner_cost_zar","sum"),
    total_gross_revenue_zar=("gross_revenue_zar","sum"),
    total_net_revenue_zar=("net_revenue_zar","sum"),
    avg_send_amount_zar=("send_amount_zar","mean"),
    avg_fee_zar=("transfer_fee_zar","mean"),
    avg_completion_mins=("completion_minutes","mean"),
    unique_senders=("sender_customer_id","nunique"),
    unique_recipients=("recipient_id","nunique"),
    fraud_flagged=("is_suspected_fraud","sum"),
).reset_index()
mart_remit_monthly["avg_revenue_per_transfer"] = (
    mart_remit_monthly["total_net_revenue_zar"] / mart_remit_monthly["transfer_count"]).round(2)
mart_remit_monthly["fee_as_pct_of_send"] = (
    mart_remit_monthly["total_fee_zar"] / mart_remit_monthly["total_send_zar"] * 100).round(4)
save(mart_remit_monthly, GOLD / "mart_remittance", "mart_remittance_monthly")

# Daily corridor
mart_remit_daily = transfers[transfers["is_completed"]==True].groupby(
    ["business_key","corridor_code","created_date"]
).agg(
    transfer_count=("transfer_id","count"),
    total_send_zar=("send_amount_zar","sum"),
    total_net_revenue_zar=("net_revenue_zar","sum"),
    avg_send_zar=("send_amount_zar","mean"),
    unique_senders=("sender_customer_id","nunique"),
).reset_index()
save(mart_remit_daily, GOLD / "mart_remittance", "mart_remittance_daily")

# Transfer funnel by status
mart_funnel = transfers.groupby(["business_key","corridor_code","created_month","transfer_status"]).agg(
    count=("transfer_id","count"),
    total_zar=("send_amount_zar","sum"),
).reset_index()
save(mart_funnel, GOLD / "mart_remittance", "mart_transfer_funnel")

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_CUSTOMER_360
# ══════════════════════════════════════════════════════════════════════════════

# Customer LTV segments
cust360 = stg_customer[[
    "customer_id","business_key","registration_datetime","kyc_level","risk_band",
    "customer_segment","nationality","monthly_income_band","acquisition_source",
    "total_transfers","completed_transfers","total_send_zar","avg_send_zar",
    "total_fee_zar","total_revenue_zar","success_rate","is_active_sender","is_repeat_sender"
]].copy()

# Wallet balance per customer
wallet_bal = wallets.groupby("customer_id").agg(
    wallet_entries=("ledger_id","count"),
    wallet_cash_in_zar=("amount_zar", lambda x: x[wallets.loc[x.index,"entry_direction"]=="debit"].sum()),
    latest_balance_zar=("running_balance_zar","last"),
).reset_index()
cust360 = cust360.merge(wallet_bal, on="customer_id", how="left")

# Card spend per customer
card_spend = cards[cards["transaction_status"]=="APPROVED"].groupby("customer_id").agg(
    card_txn_count=("card_txn_id","count"),
    total_card_spend_zar=("amount_zar","sum"),
    avg_card_txn_zar=("amount_zar","mean"),
).reset_index()
cust360 = cust360.merge(card_spend, on="customer_id", how="left")

# LTV scoring (simple)
cust360["ltv_score"] = (
    cust360["total_revenue_zar"].fillna(0) * 0.6 +
    cust360["total_card_spend_zar"].fillna(0) * 0.002 +
    cust360["completed_transfers"].fillna(0) * 5
).round(2)
cust360["ltv_band"] = pd.cut(
    cust360["ltv_score"],
    bins=[-np.inf,0,100,500,2000,np.inf],
    labels=["zero","low","medium","high","champion"])

save(cust360, GOLD / "mart_customer_360", "mart_customer_360")

# Monthly active customers
transfers["reg_month"] = pd.to_datetime(transfers["created_datetime"]).dt.to_period("M").astype(str)
mac = transfers[transfers["is_completed"]==True].groupby(
    ["business_key","created_month"]
).agg(
    monthly_active_customers=("sender_customer_id","nunique"),
    new_customers=("is_first_transfer","sum"),
    repeat_customers=("is_repeat_customer","sum"),
    completed_transfers=("transfer_id","count"),
    total_volume_zar=("send_amount_zar","sum"),
    total_revenue_zar=("net_revenue_zar","sum"),
).reset_index()
mac["revenue_per_mac"] = (mac["total_revenue_zar"]/mac["monthly_active_customers"]).round(2)
mac["repeat_rate_pct"] = (mac["repeat_customers"]/mac["monthly_active_customers"]*100).round(2)
save(mac, GOLD / "mart_customer_360", "mart_monthly_active_customers")

# Cohort retention (monthly registration cohort)
transfers_with_reg = transfers.merge(
    customers[["customer_id","registration_datetime"]],
    left_on="sender_customer_id", right_on="customer_id", how="left")
transfers_with_reg["cohort_month"] = pd.to_datetime(
    transfers_with_reg["registration_datetime"]).dt.to_period("M").astype(str)
transfers_with_reg["activity_month"] = pd.to_datetime(
    transfers_with_reg["created_datetime"]).dt.to_period("M").astype(str)

cohort = transfers_with_reg[transfers_with_reg["is_completed"]==True].groupby(
    ["business_key","cohort_month","activity_month"]
).agg(active_customers=("sender_customer_id","nunique")).reset_index()
save(cohort, GOLD / "mart_customer_360", "mart_cohort_retention")

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_FX_PROFITABILITY
# ══════════════════════════════════════════════════════════════════════════════

fx_monthly = fx_rates.copy()
fx_rates["rate_month"] = pd.to_datetime(fx_rates["rate_datetime"]).dt.to_period("M").astype(str)
fx_month_agg = fx_rates.groupby(["corridor_code","rate_month"]).agg(
    avg_market_rate=("market_rate","mean"),
    avg_customer_rate=("customer_rate","mean"),
    avg_spread_pct=("fx_spread_pct","mean"),
    max_spread_pct=("fx_spread_pct","max"),
    min_spread_pct=("fx_spread_pct","min"),
    rate_count=("fx_rate_id","count"),
).reset_index()
save(fx_month_agg, GOLD / "mart_fx_profitability", "mart_fx_monthly_rates")

# FX profitability by corridor (completed transfers)
fx_profit = transfers[transfers["is_completed"]==True].groupby(
    ["business_key","corridor_code","created_month"]
).agg(
    transfer_count=("transfer_id","count"),
    total_send_zar=("send_amount_zar","sum"),
    total_fx_margin_zar=("fx_margin_zar","sum"),
    total_fee_zar=("transfer_fee_zar","sum"),
    avg_spread_pct=("fx_spread_pct","mean"),
).reset_index()
fx_profit["fx_margin_per_transfer"] = (fx_profit["total_fx_margin_zar"]/fx_profit["transfer_count"]).round(2)
fx_profit["fx_margin_as_pct_volume"] = (fx_profit["total_fx_margin_zar"]/fx_profit["total_send_zar"]*100).round(4)
save(fx_profit, GOLD / "mart_fx_profitability", "mart_fx_profitability_corridor")

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_WALLET_CARD
# ══════════════════════════════════════════════════════════════════════════════

# Wallet monthly summary
wallets["txn_month"] = pd.to_datetime(wallets["entry_datetime"]).dt.to_period("M").astype(str)
wallet_monthly = wallets.groupby(["business_key","txn_month","entry_type"]).agg(
    txn_count=("ledger_id","count"),
    total_amount_zar=("amount_zar","sum"),
    avg_amount_zar=("amount_zar","mean"),
    unique_wallets=("customer_id","nunique"),
).reset_index()
save(wallet_monthly, GOLD / "mart_wallet_card", "mart_wallet_monthly")

# Card monthly summary
cards["txn_month"] = pd.to_datetime(cards["transaction_datetime"]).dt.to_period("M").astype(str)
card_monthly = cards[cards["transaction_status"]=="APPROVED"].groupby(
    ["business_key","txn_month","merchant_category","transaction_type"]
).agg(
    txn_count=("card_txn_id","count"),
    total_spend_zar=("amount_zar","sum"),
    avg_txn_zar=("amount_zar","mean"),
    unique_cards=("customer_id","nunique"),
    fraud_flagged=("is_fraud_flagged","sum"),
).reset_index()
save(card_monthly, GOLD / "mart_wallet_card", "mart_card_monthly")

# Card decline analysis
card_decline = cards[cards["transaction_status"]=="DECLINED"].groupby(
    ["business_key","decline_reason","txn_month"]
).agg(count=("card_txn_id","count"),total_zar=("amount_zar","sum")).reset_index()
save(card_decline, GOLD / "mart_wallet_card", "mart_card_declines")

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_LOANS_MUKURU
# ══════════════════════════════════════════════════════════════════════════════

loans["app_month"] = pd.to_datetime(loans["application_datetime"]).dt.to_period("M").astype(str)
loan_monthly = loans.groupby(["app_month","decision","loan_status"]).agg(
    application_count=("loan_id","count"),
    total_principal=("principal_zar","sum"),
    avg_principal=("principal_zar","mean"),
    avg_pd_score=("probability_of_default","mean"),
    total_ecl=("expected_credit_loss_zar","sum"),
    avg_term_months=("term_months","mean"),
).reset_index()
save(loan_monthly, GOLD / "mart_loans_mukuru", "mart_loan_monthly")

# Delinquency
delinq = loans[loans["decision"]=="APPROVED"].copy()
delinq["dpd_band"] = pd.cut(
    delinq["days_past_due"],
    bins=[-1,0,30,60,90,180,np.inf],
    labels=["current","1-30dpd","31-60dpd","61-90dpd","91-180dpd","180+dpd"])
delinq_agg = delinq.groupby(["app_month","dpd_band"]).agg(
    count=("loan_id","count"),
    total_principal=("principal_zar","sum"),
    total_ecl=("expected_credit_loss_zar","sum"),
).reset_index()
save(delinq_agg, GOLD / "mart_loans_mukuru", "mart_loan_delinquency")

# Repayment performance
repay_perf = loan_repay.groupby(["payment_status"]).agg(
    count=("repayment_id","count"),
    total_due=("amount_due_zar","sum"),
    total_paid=("amount_paid_zar","sum"),
).reset_index()
repay_perf["collection_rate_pct"] = (repay_perf["total_paid"]/repay_perf["total_due"]*100).round(2)
save(repay_perf, GOLD / "mart_loans_mukuru", "mart_loan_repayment_performance")

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_INSURANCE_MUKURU
# ══════════════════════════════════════════════════════════════════════════════

insurance["start_month"] = pd.to_datetime(insurance["policy_start_date"]).dt.to_period("M").astype(str)
insur_monthly = insurance.groupby(["start_month","plan_name","policy_status"]).agg(
    policy_count=("policy_id","count"),
    total_monthly_premium=("monthly_premium_zar","sum"),
    total_cover_zar=("cover_amount_zar","sum"),
    total_premiums_collected=("total_premiums_paid_zar","sum"),
).reset_index()
save(insur_monthly, GOLD / "mart_insurance_mukuru", "mart_insurance_monthly")

claims_summary = claims.groupby(["decision"]).agg(
    claim_count=("claim_id","count"),
    total_claimed=("claimed_amount_zar","sum"),
    total_paid=("paid_amount_zar","sum"),
    avg_turnaround_days=("turnaround_days","mean"),
).reset_index()
claims_summary["claims_ratio_pct"] = (claims_summary["total_paid"]/claims_summary["total_claimed"]*100).round(2)
save(claims_summary, GOLD / "mart_insurance_mukuru", "mart_claims_summary")

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_RISK_COMPLIANCE
# ══════════════════════════════════════════════════════════════════════════════

risk_transfer = transfers.groupby(["business_key","created_month"]).agg(
    total_transfers=("transfer_id","count"),
    fraud_flagged=("is_suspected_fraud","sum"),
    completed=("is_completed","sum"),
    failed=("is_failed","sum"),
    cancelled=("is_cancelled","sum"),
    refunded=("is_refunded","sum"),
    total_volume_zar=("send_amount_zar","sum"),
).reset_index()
risk_transfer["fraud_rate_bps"] = (risk_transfer["fraud_flagged"]/risk_transfer["total_transfers"]*10000).round(2)
risk_transfer["success_rate_pct"] = (risk_transfer["completed"]/risk_transfer["total_transfers"]*100).round(2)
risk_transfer["cancellation_rate_pct"] = (risk_transfer["cancelled"]/risk_transfer["total_transfers"]*100).round(2)
save(risk_transfer, GOLD / "mart_risk_compliance", "mart_risk_monthly")

kyc_summary = customers.groupby(["business_key","kyc_level","risk_band"]).agg(
    customer_count=("customer_id","count"),
).reset_index()
save(kyc_summary, GOLD / "mart_risk_compliance", "mart_kyc_distribution")

# ══════════════════════════════════════════════════════════════════════════════
# GOLD MART: MART_PARTNER_NETWORK
# ══════════════════════════════════════════════════════════════════════════════

payout_perf = payouts.groupby(["business_key","partner_code","receive_country","payout_method"]).agg(
    payout_count=("payout_id","count"),
    successful=("payout_status", lambda x: (x=="SUCCESS").sum()),
    total_amount_zar=("amount_zar_equivalent","sum"),
    avg_amount_zar=("amount_zar_equivalent","mean"),
).reset_index()
payout_perf["success_rate_pct"] = (payout_perf["successful"]/payout_perf["payout_count"]*100).round(2)
save(payout_perf, GOLD / "mart_partner_network", "mart_partner_payout_performance")

# USD savings summary
usd_summary = usd.groupby(["account_status"]).agg(
    account_count=("savings_id","count"),
    total_balance_usdc=("current_balance_usdc","sum"),
    total_balance_zar=("current_balance_zar","sum"),
    avg_balance_usdc=("current_balance_usdc","mean"),
    total_purchased_usdc=("total_purchased_usdc","sum"),
    total_sold_usdc=("total_sold_usdc","sum"),
).reset_index()
save(usd_summary, GOLD / "mart_wallet_card", "mart_usd_savings_summary")

print()
print("=" * 60)
print("PHASE 2 COMPLETE — Silver & Gold layers built")
print("=" * 60)
