"""
African Fintech Intelligence Platform
Phase 5: Ebook Generator
Produces a comprehensive HTML ebook + styled PDF-ready report
"""

from pathlib import Path
import datetime

BASE  = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
EBOOK = BASE / "ebook"

TODAY = datetime.date.today().isoformat()

# ══════════════════════════════════════════════════════════════════════════════
# CSS STYLING
# ══════════════════════════════════════════════════════════════════════════════
CSS = """
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.7;
    color: #1a1a2e;
    background: #f8f9fa;
  }
  .cover {
    background: linear-gradient(135deg, #0D1B2A 0%, #1A3A5C 50%, #0D1B2A 100%);
    color: white;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 60px 40px;
    page-break-after: always;
  }
  .cover-logo { font-size: 72px; margin-bottom: 20px; }
  .cover-title {
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 2px;
    background: linear-gradient(90deg, #FFD700, #F7941D, #FFD700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
    line-height: 1.2;
  }
  .cover-subtitle {
    font-size: 22px;
    color: #90CAF9;
    margin-bottom: 40px;
    font-weight: 300;
  }
  .cover-brands {
    display: flex;
    gap: 40px;
    justify-content: center;
    margin: 30px 0;
  }
  .brand-pill {
    padding: 10px 28px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 18px;
  }
  .brand-mkr { background: #E31837; color: white; }
  .brand-mmy { background: #F7941D; color: white; }
  .cover-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 40px;
    width: 100%;
    max-width: 800px;
  }
  .stat-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 20px;
  }
  .stat-num { font-size: 32px; font-weight: 900; color: #FFD700; }
  .stat-lbl { font-size: 11px; color: #B0BEC5; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
  .cover-meta { margin-top: 50px; color: #78909C; font-size: 12px; }

  .toc {
    max-width: 900px;
    margin: 60px auto;
    background: white;
    border-radius: 16px;
    padding: 50px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    page-break-after: always;
  }
  .toc h2 { color: #0D1B2A; font-size: 28px; margin-bottom: 30px; border-bottom: 3px solid #FFD700; padding-bottom: 12px; }
  .toc-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px dotted #ddd;
    font-size: 14px;
  }
  .toc-chapter { color: #1565C0; font-weight: 600; }
  .toc-page { color: #888; }
  .toc-sub { padding: 4px 0 4px 24px; border-bottom: 1px dotted #eee; font-size: 13px; color: #555; }

  .chapter {
    max-width: 900px;
    margin: 0 auto 60px;
    background: white;
    border-radius: 16px;
    padding: 50px 60px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  }
  .chapter-header {
    background: linear-gradient(135deg, #0D1B2A, #1A3A5C);
    color: white;
    margin: -50px -60px 40px;
    padding: 40px 60px;
    border-radius: 16px 16px 0 0;
  }
  .ch-num { font-size: 12px; text-transform: uppercase; letter-spacing: 3px; color: #FFD700; margin-bottom: 8px; }
  .ch-title { font-size: 32px; font-weight: 800; line-height: 1.2; }
  .ch-subtitle { font-size: 16px; color: #90CAF9; margin-top: 8px; }

  h2 { font-size: 22px; color: #0D1B2A; margin: 36px 0 14px; padding-bottom: 8px; border-bottom: 2px solid #E3F2FD; }
  h3 { font-size: 17px; color: #1565C0; margin: 24px 0 10px; }
  h4 { font-size: 15px; color: #37474F; margin: 18px 0 8px; }
  p { margin-bottom: 14px; }

  .highlight-box {
    background: linear-gradient(135deg, #E3F2FD, #F3E5F5);
    border-left: 5px solid #1565C0;
    border-radius: 0 8px 8px 0;
    padding: 18px 24px;
    margin: 20px 0;
  }
  .highlight-box.warning { background: #FFF8E1; border-color: #F9A825; }
  .highlight-box.success { background: #E8F5E9; border-color: #2E7D32; }
  .highlight-box.danger  { background: #FFEBEE; border-color: #C62828; }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 24px 0;
  }
  .kpi-card {
    background: linear-gradient(135deg, #0D1B2A, #1A3A5C);
    color: white;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }
  .kpi-val { font-size: 28px; font-weight: 900; color: #FFD700; }
  .kpi-lbl { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #B0BEC5; margin-top: 6px; }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 13px;
  }
  th {
    background: #0D1B2A;
    color: #FFD700;
    padding: 10px 12px;
    text-align: left;
    font-weight: 700;
  }
  td {
    padding: 9px 12px;
    border-bottom: 1px solid #ECEFF1;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #F8FAFB; }
  tr:hover td { background: #E3F2FD; }

  .arch-box {
    background: #0D1B2A;
    color: #E0E0E0;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    padding: 28px;
    border-radius: 10px;
    margin: 20px 0;
    white-space: pre;
    overflow-x: auto;
    border: 1px solid #1A3A5C;
    line-height: 1.6;
  }
  .arch-box .gold  { color: #FFD700; font-weight: bold; }
  .arch-box .cyan  { color: #80DEEA; }
  .arch-box .green { color: #A5D6A7; }
  .arch-box .red   { color: #EF9A9A; }
  .arch-box .orange{ color: #FFCC80; }

  .brand-section {
    border-radius: 12px;
    padding: 24px;
    margin: 20px 0;
  }
  .brand-mkr-section { background: #FFF5F5; border: 2px solid #E31837; }
  .brand-mmy-section { background: #FFF9F0; border: 2px solid #F7941D; }
  .brand-lbl { font-weight: 900; font-size: 14px; margin-bottom: 10px; }
  .mkr-lbl { color: #E31837; }
  .mmy-lbl { color: #F7941D; }

  .model-card {
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    padding: 20px;
    margin: 16px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .model-card h4 { margin-top: 0; }
  .metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px; }
  .metric-chip {
    background: #E3F2FD;
    color: #1565C0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
  }

  .page-break { page-break-after: always; }
  .footer {
    background: #0D1B2A;
    color: #78909C;
    text-align: center;
    padding: 30px;
    font-size: 12px;
    margin-top: 60px;
  }
  .footer strong { color: #FFD700; }
  @media print {
    body { background: white; }
    .chapter { box-shadow: none; border: 1px solid #ddd; }
    .cover { min-height: auto; }
  }
"""

# ══════════════════════════════════════════════════════════════════════════════
# HTML CONTENT
# ══════════════════════════════════════════════════════════════════════════════

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>African Fintech Intelligence Platform — Technical Ebook</title>
<style>{CSS}</style>
</head>
<body>

<!-- ══ COVER ══════════════════════════════════════════════════════════════ -->
<div class="cover">
  <div class="cover-logo">🌍</div>
  <div class="cover-title">African Fintech<br>Intelligence Platform</div>
  <div class="cover-subtitle">A Unified Multi-Brand Data Architecture for<br>International Remittance & Financial Services</div>
  <div class="cover-brands">
    <span class="brand-pill brand-mkr">MUKURU</span>
    <span style="font-size:28px;color:#90CAF9;align-self:center;">+</span>
    <span class="brand-pill brand-mmy">MAMA MONEY</span>
  </div>
  <div class="cover-stats">
    <div class="stat-box"><div class="stat-num">40M+</div><div class="stat-lbl">Rows Generated</div></div>
    <div class="stat-box"><div class="stat-num">5M</div><div class="stat-lbl">Transfer Orders</div></div>
    <div class="stat-box"><div class="stat-num">500K</div><div class="stat-lbl">Customers (SCD2)</div></div>
    <div class="stat-box"><div class="stat-num">17</div><div class="stat-lbl">Active Corridors</div></div>
    <div class="stat-box"><div class="stat-num">5</div><div class="stat-lbl">ML Models</div></div>
    <div class="stat-box"><div class="stat-num">Bronze→Gold</div><div class="stat-lbl">Medallion Architecture</div></div>
  </div>
  <div class="cover-meta">
    Prepared by: Anthony Apollis &nbsp;|&nbsp; {TODAY} &nbsp;|&nbsp; Portfolio Project — Data Engineering &amp; ML
  </div>
</div>

<!-- ══ TABLE OF CONTENTS ══════════════════════════════════════════════════ -->
<div class="toc">
  <h2>Table of Contents</h2>
  <div class="toc-item"><span class="toc-chapter">Chapter 1 — Business Context &amp; Problem Statement</span><span class="toc-page">4</span></div>
  <div class="toc-sub">1.1 Mukuru: Africa's Remittance Giant</div>
  <div class="toc-sub">1.2 Mama Money: Wallet-First Fintech</div>
  <div class="toc-sub">1.3 The Case for a Unified Platform</div>
  <div class="toc-sub">1.4 Market Size &amp; Opportunity</div>
  <div class="toc-item"><span class="toc-chapter">Chapter 2 — Data Architecture &amp; Design</span><span class="toc-page">12</span></div>
  <div class="toc-sub">2.1 Medallion Architecture (Bronze / Silver / Gold)</div>
  <div class="toc-sub">2.2 Source Systems Inventory</div>
  <div class="toc-sub">2.3 Unified vs. Brand-Specific Tables</div>
  <div class="toc-sub">2.4 Transaction Grain Decisions</div>
  <div class="toc-item"><span class="toc-chapter">Chapter 3 — Operational Data Model</span><span class="toc-page">22</span></div>
  <div class="toc-sub">3.1 Core Shared Entities</div>
  <div class="toc-sub">3.2 Mukuru Extensions (Loans, Insurance, MukuruPay)</div>
  <div class="toc-sub">3.3 Mama Money Extensions (Wallet, Card, USDC Savings)</div>
  <div class="toc-sub">3.4 Slowly Changing Dimensions</div>
  <div class="toc-item"><span class="toc-chapter">Chapter 4 — Analytical Star Schema</span><span class="toc-page">34</span></div>
  <div class="toc-sub">4.1 Conformed Dimensions</div>
  <div class="toc-sub">4.2 Fact Table Design</div>
  <div class="toc-sub">4.3 FACT_REMITTANCE_TRANSFER Deep Dive</div>
  <div class="toc-sub">4.4 Power BI Semantic Model</div>
  <div class="toc-item"><span class="toc-chapter">Chapter 5 — KPI Framework</span><span class="toc-page">46</span></div>
  <div class="toc-sub">5.1 Executive KPIs</div>
  <div class="toc-sub">5.2 Corridor &amp; FX KPIs</div>
  <div class="toc-sub">5.3 Wallet, Card &amp; Digital USD KPIs</div>
  <div class="toc-sub">5.4 Mukuru Lending &amp; Insurance KPIs</div>
  <div class="toc-sub">5.5 Risk &amp; Compliance KPIs</div>
  <div class="toc-sub">5.6 Vanity Metrics to Avoid</div>
  <div class="toc-item"><span class="toc-chapter">Chapter 6 — Machine Learning Pipeline</span><span class="toc-page">58</span></div>
  <div class="toc-sub">6.1 Model 1: Real-Time Fraud Detection</div>
  <div class="toc-sub">6.2 Model 2: Customer Churn Prediction</div>
  <div class="toc-sub">6.3 Model 3: Credit Risk (PD Model)</div>
  <div class="toc-sub">6.4 Model 4: Transfer Success Prediction</div>
  <div class="toc-sub">6.5 Model 5: Revenue / FX Margin Regression</div>
  <div class="toc-sub">6.6 MLOps &amp; Model Governance</div>
  <div class="toc-item"><span class="toc-chapter">Chapter 7 — Data Quality &amp; Governance</span><span class="toc-page">72</span></div>
  <div class="toc-sub">7.1 PII &amp; Tokenisation Strategy</div>
  <div class="toc-sub">7.2 Data Lineage</div>
  <div class="toc-sub">7.3 Quality Checks &amp; dbt Tests</div>
  <div class="toc-item"><span class="toc-chapter">Chapter 8 — Implementation Roadmap</span><span class="toc-page">80</span></div>
  <div class="toc-sub">8.1 Phase 1: Foundation (Months 1-3)</div>
  <div class="toc-sub">8.2 Phase 2: Analytics (Months 4-6)</div>
  <div class="toc-sub">8.3 Phase 3: ML &amp; Real-Time (Months 7-12)</div>
</div>

<!-- ══ CHAPTER 1 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 01</div>
    <div class="ch-title">Business Context &amp; Problem Statement</div>
    <div class="ch-subtitle">Understanding the African remittance landscape and the case for data unification</div>
  </div>

  <h2>1.1 The African Remittance Opportunity</h2>
  <p>Sub-Saharan Africa receives over <strong>USD 50 billion in remittances annually</strong>, making cross-border money transfers one of the continent's most critical financial services. For the estimated 3.5 million foreign nationals working in South Africa — primarily from Zimbabwe, Mozambique, Zambia, and Malawi — reliable, affordable money transfer to family members back home is a lifeline, not a luxury.</p>

  <div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-val">USD 50B+</div><div class="kpi-lbl">Annual SSA Remittances</div></div>
    <div class="kpi-card"><div class="kpi-val">3.5M+</div><div class="kpi-lbl">Foreign Nationals in SA</div></div>
    <div class="kpi-card"><div class="kpi-val">6-8%</div><div class="kpi-lbl">Average Transfer Cost (World Bank)</div></div>
  </div>

  <p>Yet the sector remains fragmented, expensive, and analytically immature. The World Bank's target of reducing transfer costs to 3% by 2030 (SDG 10.c) creates both regulatory pressure and competitive opportunity for data-driven operators who can optimise pricing, reduce fraud, and retain customers.</p>

  <div class="brand-section brand-mkr-section">
    <div class="brand-lbl mkr-lbl">MUKURU — Africa's Leading Money Transfer Operator</div>
    <p>Founded in 2004, Mukuru has grown into one of Africa's largest remittance businesses, claiming to have served over 17 million customers across 50+ countries. Its product suite extends well beyond money transfers into a full financial services stack:</p>
    <ul style="margin:10px 0 0 20px;line-height:2">
      <li><strong>International Remittances</strong> — cash collection, bank deposits, mobile wallet payouts</li>
      <li><strong>Mukuru Card</strong> — a prepaid Mastercard for banked and unbanked customers</li>
      <li><strong>Mukuru Fast Loan</strong> — short-term credit linked to Card eligibility</li>
      <li><strong>Mukuru Funeral Cover</strong> — micro-insurance with repatriation services</li>
      <li><strong>MukuruPay</strong> — bill payments, merchant payments, cash-funded e-commerce</li>
      <li><strong>Dollar Savings</strong> — USD-denominated savings product</li>
    </ul>
  </div>

  <div class="brand-section brand-mmy-section">
    <div class="brand-lbl mmy-lbl">MAMA MONEY — Wallet-First Fintech Challenger</div>
    <p>Founded in 2015, Mama Money has built its reputation on transparent pricing ("no hidden fees") and a wallet-centric model that puts the customer in control of their funds. Key offerings include:</p>
    <ul style="margin:10px 0 0 20px;line-height:2">
      <li><strong>International Transfers</strong> — via mobile wallets, cash collection, and bank deposits across 13+ countries</li>
      <li><strong>Mama Money Wallet</strong> — ZAR digital wallet as the hub of the financial ecosystem</li>
      <li><strong>Mama Money Card</strong> — salary deposits, card spend, cash sends, airtime, and electricity</li>
      <li><strong>Digital USD Savings</strong> — USDC-backed stablecoin savings, displayed as "digital US dollars"</li>
      <li><strong>Limit Uplift Programme</strong> — structured process to increase send limits through document submission</li>
    </ul>
  </div>

  <h2>1.2 The Case for a Unified Data Platform</h2>
  <p>Despite operating in the same market with similar customer profiles, Mukuru and Mama Money have historically maintained separate data infrastructure — separate customer tables, separate transfer logs, separate KYC stores. This creates four critical business problems:</p>

  <table>
    <tr><th>Problem</th><th>Impact</th><th>Unified Platform Solution</th></tr>
    <tr><td><strong>Siloed reporting</strong></td><td>No single view of combined market position, corridor share, or customer overlap</td><td>DIM_BUSINESS dimension enables unified and split reporting from the same model</td></tr>
    <tr><td><strong>Duplicate KYC costs</strong></td><td>Same customer may be re-verified across products; regulatory burden doubles</td><td>Shared customer entity with product-level KYC attributes</td></tr>
    <tr><td><strong>Fragmented fraud signals</strong></td><td>Fraud patterns visible only within one brand, not across the full customer relationship</td><td>Cross-brand fraud model trained on all transaction signals</td></tr>
    <tr><td><strong>Poor product cross-sell</strong></td><td>Transfer customer not targeted for Card or Savings products</td><td>Unified customer 360 enables product propensity scoring</td></tr>
  </table>

  <h2>1.3 Why This Data Model Matters</h2>

  <div class="highlight-box">
    <strong>Design principle:</strong> The strongest architecture is <em>one shared platform with a Business dimension</em> distinguishing Mukuru from Mama Money. Every shared entity — customer, recipient, transfer, wallet, card, FX rate — exists once in the canonical layer. Brand-specific extensions (loans, insurance, USDC savings) sit alongside the shared core without polluting it.
  </div>
</div>

<!-- ══ CHAPTER 2 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 02</div>
    <div class="ch-title">Data Architecture &amp; Design</div>
    <div class="ch-subtitle">Medallion architecture, source systems, and layer-by-layer design decisions</div>
  </div>

  <h2>2.1 The Medallion Architecture</h2>
  <p>This platform follows the industry-standard <strong>Bronze / Silver / Gold</strong> medallion pattern, implemented across a shared Snowflake / Azure Synapse / Databricks lakehouse:</p>

  <div class="arch-box"><span class="gold">SOURCE SYSTEMS</span>
│
├── Mobile application (iOS + Android)
├── Website (web checkout)
├── WhatsApp / USSD channels
├── Branch and booth network (Mukuru extensive; Mama Money partner-based)
├── Retail pay-in partners (Shoprite, Pick n Pay, etc.)
├── Banks and payment gateways
├── Mobile-money operators (EcoCash, M-Pesa, Airtel Money, MTN Mobile Money)
├── Card processors (Mastercard network)
├── Loan servicing platform (Mukuru)
├── Insurance administrator (Mukuru Funeral Cover)
├── KYC / AML providers (Trulioo, Onfido)
├── FX-rate providers (Reuters / Bloomberg)
└── Customer-support platform (Zendesk / Salesforce)
        │
        ▼
<span class="red">BRONZE / RAW LAYER</span>
Immutable, source-aligned, append-only
All tables prefixed with their source system
No transformations — exact copies of source records
        │
        ▼
<span class="orange">SILVER / CANONICAL LAYER</span>
Cleansed, deduplicated, type-safe
Unified customer, transfer, wallet, FX and compliance models
Business rules applied; PII tokenised
One record per business entity
        │
        ▼
<span class="green">GOLD / ANALYTICS LAYER (MARTS)</span>
mart_remittance    — Corridor, channel and product performance
mart_customer_360  — LTV, churn score, cohort, segmentation
mart_fx_profitability — Spread, margin and pricing analytics
mart_wallet_card   — Wallet balances, card spend, salary
mart_risk_compliance — Fraud signals, KYC funnel, AML alerts
mart_partner_network — Payout partner SLA and settlement
mart_loans_mukuru  — Credit portfolio, delinquency, ECL
mart_insurance_mukuru — Policy, premium and claims analytics</div>

  <h2>2.2 Transaction Grain Decisions</h2>
  <p>The most important modelling decision in any remittance platform is the grain of the fact tables. <strong>Never combine TRANSFER_ORDER, PAYMENT, and PAYOUT into one table.</strong> One transfer order can have several failed funding attempts and multiple payout retries.</p>

  <table>
    <tr><th>Table</th><th>Grain</th><th>Why Separate?</th></tr>
    <tr><td>FACT_REMITTANCE_TRANSFER</td><td>One transfer order</td><td>The business event — one intention to send money</td></tr>
    <tr><td>FACT_TRANSFER_STATUS_HISTORY</td><td>One status change</td><td>Bottleneck &amp; SLA analysis; never rely on current status only</td></tr>
    <tr><td>FACT_PAYMENT</td><td>One funding attempt</td><td>Customers may try 3 different cards before succeeding</td></tr>
    <tr><td>FACT_PAYOUT</td><td>One disbursement attempt</td><td>Partner failures cause payout retries independent of the order</td></tr>
    <tr><td>FACT_FX_RATE</td><td>One rate at a point in time</td><td>Hourly snapshotting enables rate-lock and margin-audit queries</td></tr>
    <tr><td>FACT_WALLET_LEDGER_ENTRY</td><td>One debit or credit posting</td><td>Double-entry accounting; balance is always derivable</td></tr>
    <tr><td>FACT_CARD_TRANSACTION</td><td>One card authorisation</td><td>Auth and settlement are separate events with separate timestamps</td></tr>
    <tr><td>FACT_LOAN_APPLICATION</td><td>One application decision</td><td>A customer can apply multiple times; each is a discrete event</td></tr>
  </table>

  <h2>2.3 The Business Dimension Pattern</h2>
  <div class="highlight-box success">
    <strong>Key design decision:</strong> Rather than maintaining two separate schemas (one for Mukuru, one for Mama Money), the model uses a <code>DIM_BUSINESS</code> conformed dimension with a <code>business_key</code> (MKR / MMY) on every fact table. This means:
    <ul style="margin-top:8px;margin-left:20px;line-height:2">
      <li>Executive reporting spans both brands with a single DAX measure</li>
      <li>Brand-specific filtering is a simple WHERE clause, not a schema switch</li>
      <li>New brands or products can be added without schema changes</li>
      <li>Competitive benchmarking between brands is immediate</li>
    </ul>
  </div>

  <h2>2.4 Data Volume at Scale</h2>
  <table>
    <tr><th>Table</th><th>Rows</th><th>Growth Rate</th><th>Retention</th></tr>
    <tr><td>dim_customer</td><td>500,000</td><td>~8,000/month</td><td>Indefinite (SCD2)</td></tr>
    <tr><td>dim_recipient</td><td>1,000,000</td><td>~15,000/month</td><td>Indefinite</td></tr>
    <tr><td>fact_remittance_transfer</td><td>5,000,000</td><td>~80,000/month</td><td>7 years minimum</td></tr>
    <tr><td>fact_transfer_status_history</td><td>~15,000,000</td><td>~500,000/month</td><td>7 years</td></tr>
    <tr><td>fact_payment</td><td>5,500,000</td><td>~90,000/month</td><td>7 years</td></tr>
    <tr><td>fact_payout</td><td>4,500,000</td><td>~75,000/month</td><td>7 years</td></tr>
    <tr><td>fact_wallet_ledger</td><td>~10,000,000</td><td>~200,000/month</td><td>Indefinite</td></tr>
    <tr><td>fact_card_transaction</td><td>~3,000,000</td><td>~60,000/month</td><td>5 years</td></tr>
    <tr><td>fact_fx_rate</td><td>~95,000</td><td>~1,400/month (hourly)</td><td>10 years</td></tr>
    <tr><td><strong>TOTAL</strong></td><td><strong>~44M+</strong></td><td>~1M+/month</td><td>—</td></tr>
  </table>
</div>

<!-- ══ CHAPTER 3 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 03</div>
    <div class="ch-title">Operational Data Model</div>
    <div class="ch-subtitle">Shared entities, brand-specific extensions, and slowly changing dimensions</div>
  </div>

  <h2>3.1 Core Shared Entities</h2>
  <p>The following entities are shared across both Mukuru and Mama Money because the underlying business process — a customer in South Africa sending money to a recipient in another country — is structurally identical.</p>

  <h3>Customer (SCD Type 2)</h3>
  <p>The customer dimension uses a <strong>Type 2 Slowly Changing Dimension</strong> to preserve history for the following attributes:</p>
  <ul style="margin-left:20px;line-height:2">
    <li>KYC level (as customers get verified, their limit increases)</li>
    <li>Customer status (ACTIVE → SUSPENDED → REACTIVATED journeys matter for fraud)</li>
    <li>Risk band (risk re-assessment over time)</li>
    <li>Residential country (customers relocate)</li>
    <li>Transaction-limit segment (limit uplift programme drives segment change)</li>
    <li>Marketing consent (GDPR / POPIA compliance)</li>
  </ul>

  <div class="highlight-box danger">
    <strong>PII Protection:</strong> Mobile numbers, national ID numbers, passport numbers, and bank account numbers must <em>never</em> appear in the analytics layer in plain text. Store only tokenised or hashed values. The operational system holds the cleartext under access controls. Power BI reports must never expose raw identity data.
  </div>

  <h3>Recipient Dimension</h3>
  <p>A recipient represents the person receiving the money — typically a family member of the sender. The model must handle two edge cases correctly:</p>
  <ol style="margin-left:20px;line-height:2">
    <li><strong>One recipient, multiple senders:</strong> A mother in Harare may receive from her son (Mukuru) and her daughter (Mama Money). She should be represented as one RECIPIENT_PROFILE with two CUSTOMER_RECIPIENT_RELATIONSHIP rows.</li>
    <li><strong>Saved vs. ad-hoc recipients:</strong> The saved-recipient record in the app is different from the one-time recipient for a first transfer. Both must be captured without conflation.</li>
  </ol>

  <h3>Transfer Status Lifecycle</h3>
  <p>A transfer passes through a deterministic state machine. The status history table must be maintained so that SLA analysis (e.g., "how long does the ZA→ZW corridor spend in COMPLIANCE_REVIEW?") can be answered without relying solely on the current status field:</p>

  <div class="arch-box"><span class="cyan">CREATED</span> → <span class="cyan">QUOTED</span> → <span class="cyan">AWAITING_PAYMENT</span> → <span class="cyan">PAID</span>
         → <span class="orange">COMPLIANCE_REVIEW</span> (triggered by rules engine)
         → <span class="cyan">PROCESSING</span> → <span class="cyan">SENT_TO_PARTNER</span>
         → <span class="cyan">AVAILABLE_FOR_COLLECTION</span> → <span class="green">COMPLETED</span>

Alternative paths:
<span class="cyan">PAID</span> → <span class="red">FAILED</span>
<span class="cyan">AWAITING_PAYMENT</span> → <span class="red">CANCELLED</span>
<span class="cyan">PROCESSING</span> → <span class="red">REFUNDED</span></div>

  <h2>3.2 Mukuru-Specific Extensions</h2>

  <div class="brand-section brand-mkr-section">
    <div class="brand-lbl mkr-lbl">Mukuru Fast Loans</div>
    <p>Mukuru's fast loan product is linked to <strong>Mukuru Card eligibility</strong>. The loan data model requires:</p>
    <ul style="margin-left:20px;line-height:1.8;margin-top:8px">
      <li>LOAN_APPLICATION — decision, score, and eligibility criteria</li>
      <li>LOAN_ELIGIBILITY_SCORE — derived from card usage, income activity, credit bureau check</li>
      <li>LOAN — originated amount, term, rate</li>
      <li>LOAN_DISBURSEMENT — disbursement to Mukuru Card account</li>
      <li>LOAN_REPAYMENT_SCHEDULE — expected payment dates</li>
      <li>LOAN_REPAYMENT — actual payments</li>
      <li>LOAN_DELINQUENCY_EVENT — DPD triggers</li>
    </ul>
    <p style="margin-top:10px"><strong>Key ML features:</strong> card_account_age_days, avg_monthly_card_spend, salary_payment_indicator, previous_loans_repaid_count, probability_of_default, expected_credit_loss.</p>
  </div>

  <div class="brand-section brand-mkr-section" style="margin-top:16px">
    <div class="brand-lbl mkr-lbl">Mukuru Funeral Cover</div>
    <p>Micro-insurance with four key processes: <strong>Policy issuance → Premium collection → Claim lodgement → Claim settlement</strong>. Unique to Mukuru is the <strong>repatriation service</strong> — physically transporting the remains of deceased members to their home country.</p>
    <p style="margin-top:8px">Required tables: INSURANCE_POLICY, INSURED_PERSON, BENEFICIARY, INSURANCE_PREMIUM, INSURANCE_CLAIM, CLAIM_ASSESSMENT, CLAIM_PAYMENT, REPATRIATION_SERVICE.</p>
  </div>

  <h2>3.3 Mama Money-Specific Extensions</h2>

  <div class="brand-section brand-mmy-section">
    <div class="brand-lbl mmy-lbl">Wallet-Centred Architecture</div>
    <p>Mama Money positions the wallet as the central account from which customers do everything. All movements must be represented as <strong>double-entry ledger postings</strong>:</p>
    <div style="font-family:monospace;font-size:12px;background:#FFF3E0;padding:16px;border-radius:8px;margin-top:10px;line-height:2">
      Dr Customer ZAR Wallet &nbsp;&nbsp; Cr Remittance Settlement Clearing<br>
      Dr Customer ZAR Wallet &nbsp;&nbsp; Cr Customer Digital USD Savings<br>
      Dr Customer Digital USD &nbsp; Cr Customer ZAR Wallet (sell USD)<br>
      Dr Customer ZAR Wallet &nbsp;&nbsp; Cr Mama Card Funding Clearing
    </div>
  </div>

  <div class="brand-section brand-mmy-section" style="margin-top:16px">
    <div class="brand-lbl mmy-lbl">Digital USD (USDC) Savings</div>
    <p>Mama Money's USD savings product is backed by <strong>USDC (USD Coin)</strong> — a regulated stablecoin. The data model must distinguish:</p>
    <ul style="margin-left:20px;line-height:1.8;margin-top:8px">
      <li>The <strong>displayed currency</strong> (USD) from the <strong>underlying digital asset</strong> (USDC)</li>
      <li>Purchase events (ZAR → USDC at market rate)</li>
      <li>Sale events (USDC → ZAR)</li>
      <li>Balance snapshots (daily, for regulatory reporting)</li>
    </ul>
    <p style="margin-top:8px">This is <em>not</em> an ordinary USD bank account — it is a digital asset position that carries its own regulatory obligations under crypto asset service provider frameworks.</p>
  </div>
</div>

<!-- ══ CHAPTER 4 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 04</div>
    <div class="ch-title">Analytical Star Schema</div>
    <div class="ch-subtitle">Conformed dimensions, fact table design, and Power BI semantic model</div>
  </div>

  <h2>4.1 Conformed Dimensions</h2>
  <p>Conformed dimensions are the backbone of a multi-fact star schema. They allow Mukuru's remittance facts, Mama Money's wallet facts, and the shared card facts to be filtered together without creating fan-trap joins. The following dimensions are conformed across <strong>all</strong> fact tables in this platform:</p>

  <table>
    <tr><th>Dimension</th><th>Primary Use</th><th>Type</th></tr>
    <tr><td>DIM_DATE</td><td>All fact tables; time-series analysis</td><td>Static (date spine)</td></tr>
    <tr><td>DIM_BUSINESS</td><td>Brand-level filtering; portfolio view</td><td>Type 1 (rarely changes)</td></tr>
    <tr><td>DIM_CUSTOMER</td><td>All customer-linked facts</td><td>Type 2 SCD</td></tr>
    <tr><td>DIM_COUNTRY</td><td>Send/receive country; corridor lookup</td><td>Type 1</td></tr>
    <tr><td>DIM_CURRENCY</td><td>FX rates; monetary amounts</td><td>Type 1</td></tr>
    <tr><td>DIM_CHANNEL</td><td>Digital adoption; channel profitability</td><td>Type 1</td></tr>
    <tr><td>DIM_PRODUCT</td><td>Product-level revenue; cross-sell</td><td>Type 1</td></tr>
    <tr><td>DIM_PARTNER</td><td>Payout partner SLA; settlement</td><td>Type 2 (commission rates change)</td></tr>
    <tr><td>DIM_CORRIDOR</td><td>Corridor-level KPIs; regulatory risk</td><td>Type 1</td></tr>
    <tr><td>DIM_TRANSFER_STATUS</td><td>Transfer funnel; SLA analysis</td><td>Type 1</td></tr>
  </table>

  <h2>4.2 FACT_REMITTANCE_TRANSFER Design</h2>
  <p>This is the central fact table of the platform. Every metric that a Mukuru or Mama Money executive cares about — volume, revenue, margin, completion rate — is derivable from this table in combination with the conformed dimensions.</p>

  <table>
    <tr><th>Metric Group</th><th>Fields</th></tr>
    <tr><td><strong>Volume</strong></td><td>send_amount_zar, receive_amount, send_amount_zar (reporting currency)</td></tr>
    <tr><td><strong>Revenue</strong></td><td>transfer_fee_zar, fx_margin_zar, gross_revenue_zar, net_revenue_zar</td></tr>
    <tr><td><strong>Costs</strong></td><td>partner_cost_zar, vat_zar</td></tr>
    <tr><td><strong>FX</strong></td><td>market_fx_rate, customer_fx_rate, fx_spread_pct</td></tr>
    <tr><td><strong>Operational</strong></td><td>payment_attempt_count, payout_attempt_count, completion_minutes</td></tr>
    <tr><td><strong>Flags</strong></td><td>is_completed, is_failed, is_cancelled, is_refunded, is_first_transfer, is_suspected_fraud</td></tr>
  </table>

  <div class="highlight-box">
    <strong>Reporting currency design:</strong> Even though transfers flow between ZAR, ZWL, KES, and other currencies, a <em>standard reporting currency</em> (ZAR) amount is stored alongside every monetary field. This allows Power BI to sum revenue across corridors without a currency conversion step in DAX — a major performance improvement at scale.
  </div>

  <h2>4.3 Power BI Semantic Model</h2>
  <p>The recommended Power BI semantic model uses a <strong>multiple-star layout</strong> with no direct joins between fact tables. Shared filtering passes through conformed dimensions only:</p>

  <div class="arch-box">                         <span class="gold">DIM_DATE</span>
                            │
<span class="red">DIM_BUSINESS</span> ──── <span class="green">FACT_REMITTANCE_TRANSFER</span> ──── <span class="cyan">DIM_CUSTOMER</span>
                            │
                  ┌─────────┼─────────────────────────┐
            <span class="orange">DIM_CORRIDOR</span>  <span class="orange">DIM_CHANNEL</span>          <span class="orange">DIM_PARTNER</span>
            <span class="orange">DIM_PRODUCT</span>   <span class="orange">DIM_PAYMENT_METHOD</span>   <span class="orange">DIM_STATUS</span>

<span class="gold">DIM_DATE</span> ──── <span class="green">FACT_WALLET_LEDGER</span> ──── <span class="cyan">DIM_CUSTOMER</span>
                  │
           <span class="red">DIM_BUSINESS</span>, <span class="orange">DIM_PRODUCT</span>, <span class="orange">DIM_CURRENCY</span>

<span class="gold">DIM_DATE</span> ──── <span class="green">FACT_CARD_TRANSACTION</span> ──── <span class="cyan">DIM_CUSTOMER</span>
                  │
           <span class="red">DIM_BUSINESS</span>, <span class="orange">DIM_MERCHANT</span>, <span class="orange">DIM_CHANNEL</span></div>

  <div class="highlight-box warning">
    <strong>Anti-pattern to avoid:</strong> Never join FACT_REMITTANCE_TRANSFER to FACT_WALLET_LEDGER directly. This creates a many-to-many join that inflates row counts and causes incorrect totals. Always filter through DIM_CUSTOMER or DIM_DATE.
  </div>
</div>

<!-- ══ CHAPTER 5 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 05</div>
    <div class="ch-title">KPI Framework</div>
    <div class="ch-subtitle">The complete metric library for remittance, FX, wallet, card, lending, insurance, and risk</div>
  </div>

  <h2>5.1 Executive KPIs</h2>
  <table>
    <tr><th>KPI</th><th>Formula</th><th>Frequency</th><th>Owner</th></tr>
    <tr><td>Remittance Volume (ZAR)</td><td>SUM(send_amount_zar) WHERE is_completed</td><td>Daily</td><td>CEO / CFO</td></tr>
    <tr><td>Completed Transfers</td><td>COUNT(transfer_id) WHERE is_completed</td><td>Daily</td><td>CEO / COO</td></tr>
    <tr><td>Monthly Active Senders</td><td>DISTINCTCOUNT(customer_id) in period</td><td>Monthly</td><td>CEO / CMO</td></tr>
    <tr><td>Transfer Success Rate</td><td>Completed ÷ Initiated</td><td>Daily</td><td>COO / Product</td></tr>
    <tr><td>Net Revenue (ZAR)</td><td>SUM(fee + fx_margin − partner_cost − refund)</td><td>Daily</td><td>CFO</td></tr>
    <tr><td>Revenue per Active Customer</td><td>Net Revenue ÷ Monthly Active Senders</td><td>Monthly</td><td>CFO / CMO</td></tr>
    <tr><td>Average Transfer Value</td><td>SUM(send_amount_zar) ÷ COUNT(completed)</td><td>Weekly</td><td>Product</td></tr>
    <tr><td>Repeat Sender Rate</td><td>Customers with ≥2 completed TFRs ÷ All active</td><td>Monthly</td><td>CMO</td></tr>
    <tr><td>Digital Adoption Rate</td><td>Digital channel TFRs ÷ All TFRs</td><td>Monthly</td><td>Product / CMO</td></tr>
    <tr><td>Customer Acquisition Cost</td><td>Acquisition spend ÷ Newly activated customers</td><td>Monthly</td><td>CMO / CFO</td></tr>
  </table>

  <h2>5.2 Corridor &amp; FX KPIs</h2>
  <table>
    <tr><th>KPI</th><th>Key Insight</th></tr>
    <tr><td>Transfer Value by Corridor</td><td>Identify which corridors drive 80% of volume (Pareto)</td></tr>
    <tr><td>Average FX Spread %</td><td>Price competitiveness vs. market; revenue driver</td></tr>
    <tr><td>FX Margin Revenue</td><td>Hidden revenue stream; often 30-50% of total revenue</td></tr>
    <tr><td>Corridor Success Rate</td><td>Partner reliability; highlights SLA gaps</td></tr>
    <tr><td>Corridor Completion Time</td><td>Customer experience; competitive differentiator</td></tr>
    <tr><td>Cash Collection Ageing</td><td>Uncollected payouts represent both customer and partner risk</td></tr>
    <tr><td>Partner Settlement Variance</td><td>Reconciliation KPI: what was disbursed vs. what was settled</td></tr>
  </table>

  <h2>5.3 Risk &amp; Compliance KPIs</h2>
  <table>
    <tr><th>KPI</th><th>Target</th><th>Alert Threshold</th></tr>
    <tr><td>KYC Completion Rate</td><td>&gt;90%</td><td>&lt;80%</td></tr>
    <tr><td>Fraud Loss (basis points)</td><td>&lt;5 bps of volume</td><td>&gt;10 bps</td></tr>
    <tr><td>Sanctions Screening False-Positive Rate</td><td>&lt;2%</td><td>&gt;5%</td></tr>
    <tr><td>Suspicious Transfer Rate</td><td>&lt;0.5%</td><td>&gt;1%</td></tr>
    <tr><td>Account Takeover Rate</td><td>&lt;0.1%</td><td>&gt;0.3%</td></tr>
    <tr><td>High-Risk Corridor Exposure %</td><td>&lt;15% of volume</td><td>&gt;25%</td></tr>
    <tr><td>KYC Review Backlog (days)</td><td>&lt;2 days</td><td>&gt;5 days</td></tr>
  </table>

  <h2>5.4 Vanity Metrics — What NOT to Use</h2>
  <div class="highlight-box warning">
    <strong>The following metrics appear impressive but are analytically incomplete without paired context metrics:</strong>
    <ul style="margin-top:8px;margin-left:20px;line-height:2">
      <li>"17 million customers served" — paired with: monthly active rate, transacting rate, and definition of "served"</li>
      <li>"Total registered customers" — paired with: % transacting in last 90 days (active rate)</li>
      <li>"Total transactions since launch" — paired with: current-period rate and month-on-month growth</li>
      <li>"50+ countries" — paired with: countries with at least 100 transactions in the last 30 days</li>
      <li>"Number of locations" — paired with: active locations with transactions</li>
    </ul>
  </div>
</div>

<!-- ══ CHAPTER 6 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 06</div>
    <div class="ch-title">Machine Learning Pipeline</div>
    <div class="ch-subtitle">Five production-grade models for fraud, churn, credit risk, transfer success, and revenue</div>
  </div>

  <h2>6.1 ML Architecture Overview</h2>
  <p>The platform deploys five machine learning models, each addressing a distinct business problem. All models are trained on the 40M+ row synthetic dataset and are designed for production deployment on Databricks MLflow, Azure ML, or Snowpark ML.</p>

  <div class="model-card">
    <h4>Model 1: Real-Time Fraud Detection</h4>
    <p><strong>Algorithm:</strong> Gradient Boosting Classifier (GBM) &nbsp;|&nbsp; <strong>Target:</strong> is_suspected_fraud</p>
    <p>Trained on 5M transfer records with temporal features (hour of day, day of week), behavioural features (amount log-transform, fee percentage, FX spread), and contextual features (corridor, channel, payment method). The model outputs a continuous fraud score that feeds a threshold-based decision engine.</p>
    <div class="metric-row">
      <span class="metric-chip">AUC-ROC: ~0.90+</span>
      <span class="metric-chip">Threshold: 0.40</span>
      <span class="metric-chip">Fraud Rate: ~0.8% of transfers</span>
      <span class="metric-chip">Real-time inference: &lt;50ms</span>
    </div>
    <p style="margin-top:10px"><strong>Top features:</strong> send_amount_log, corridor_code, payment_method, hour_of_day, fx_spread_pct, customer_fx_rate</p>
  </div>

  <div class="model-card">
    <h4>Model 2: Customer Churn Prediction</h4>
    <p><strong>Algorithm:</strong> Random Forest Classifier &nbsp;|&nbsp; <strong>Target:</strong> no transfer in next 90 days</p>
    <p>Uses the full customer behavioural history: recency (days since last transfer), frequency (monthly transfer rate), monetary (total volume), corridor diversity, channel diversity, and demographic features. Outputs a churn probability segmented into five risk bands (very_low to very_high).</p>
    <div class="metric-row">
      <span class="metric-chip">AUC-ROC: ~0.85+</span>
      <span class="metric-chip">Churn Rate: ~45% at 90 days</span>
      <span class="metric-chip">5 Risk Bands</span>
      <span class="metric-chip">Batch inference: weekly</span>
    </div>
    <p style="margin-top:10px"><strong>Business use:</strong> Target "high" and "very_high" churn customers with retention incentives (fee waiver, promotional FX rate) before they transfer to a competitor.</p>
  </div>

  <div class="model-card">
    <h4>Model 3: Credit Risk — Probability of Default</h4>
    <p><strong>Algorithm:</strong> GBM Classifier &nbsp;|&nbsp; <strong>Target:</strong> loan defaults (DPD &gt; 90 or written off)</p>
    <p>Mukuru-specific model trained on 200K loan applications with repayment history. Features include card account age, average monthly card spend, salary deposit indicator, and bureau signals. Outputs a PD score used for both origination decisions and Expected Credit Loss (ECL) calculations under IFRS 9.</p>
    <div class="metric-row">
      <span class="metric-chip">AUC-ROC: ~0.78+</span>
      <span class="metric-chip">Default Rate: ~10-15%</span>
      <span class="metric-chip">5 Risk Grades (A-E)</span>
      <span class="metric-chip">ECL: PD × LGD × EAD</span>
    </div>
  </div>

  <div class="model-card">
    <h4>Model 4: Transfer Success Prediction</h4>
    <p><strong>Algorithm:</strong> Random Forest Classifier &nbsp;|&nbsp; <strong>Target:</strong> is_completed</p>
    <p>Predicts the probability of a transfer completing successfully at initiation time. Used in real-time to route transfers to the most reliable payout partner and to set customer expectations on timing. Low-probability transfers can be flagged for human review before processing costs are incurred.</p>
    <div class="metric-row">
      <span class="metric-chip">AUC-ROC: ~0.82+</span>
      <span class="metric-chip">Completion Rate: ~78%</span>
      <span class="metric-chip">Used for: routing, expectations</span>
    </div>
  </div>

  <div class="model-card">
    <h4>Model 5: Revenue / FX Margin Regression</h4>
    <p><strong>Algorithm:</strong> GBM Regressor &nbsp;|&nbsp; <strong>Target:</strong> net_revenue_zar per completed transfer</p>
    <p>Predicts the net revenue attributable to each transfer based on corridor, channel, send amount, and FX spread. Used for pricing optimisation, promotional planning, and dynamic FX spread adjustment. A/B testing on spread changes can be evaluated against the model baseline.</p>
    <div class="metric-row">
      <span class="metric-chip">R² Score: ~0.75+</span>
      <span class="metric-chip">MAE: ~R 15 per transfer</span>
      <span class="metric-chip">Used for: pricing strategy</span>
    </div>
  </div>

  <h2>6.2 MLOps Architecture</h2>
  <table>
    <tr><th>Stage</th><th>Tool</th><th>Frequency</th></tr>
    <tr><td>Feature Store</td><td>Databricks Feature Store / Azure ML</td><td>Real-time + batch</td></tr>
    <tr><td>Model Training</td><td>Databricks MLflow / sklearn pipelines</td><td>Weekly retraining</td></tr>
    <tr><td>Model Registry</td><td>MLflow Model Registry</td><td>On each training run</td></tr>
    <tr><td>A/B Testing</td><td>DIM_EXPERIMENT + random assignment</td><td>Per campaign</td></tr>
    <tr><td>Model Monitoring</td><td>Evidently AI / Azure ML Monitor</td><td>Daily drift checks</td></tr>
    <tr><td>Inference</td><td>REST API (fraud) + batch scoring (churn/credit)</td><td>Real-time + nightly</td></tr>
    <tr><td>Explainability</td><td>SHAP values for all models</td><td>On demand (credit decisions)</td></tr>
  </table>

  <div class="highlight-box">
    <strong>Regulatory note:</strong> Credit decisions (Model 3) must be <em>explainable</em> under the National Credit Act (NCA) of South Africa. Every declined application must be backed by human-readable reasons derivable from SHAP values — "declined due to high monthly payment relative to income" — not just a score.
  </div>
</div>

<!-- ══ CHAPTER 7 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 07</div>
    <div class="ch-title">Data Quality &amp; Governance</div>
    <div class="ch-subtitle">PII tokenisation, lineage, dbt tests, and POPIA/GDPR compliance</div>
  </div>

  <h2>7.1 PII Classification &amp; Tokenisation</h2>
  <table>
    <tr><th>Field</th><th>Classification</th><th>Bronze Layer</th><th>Silver / Gold Layer</th></tr>
    <tr><td>Full name</td><td>PII — Personal</td><td>Plaintext</td><td>Hash (SHA-256)</td></tr>
    <tr><td>National ID / Passport</td><td>PII — Sensitive</td><td>Encrypted AES-256</td><td>Tokenised reference</td></tr>
    <tr><td>Mobile number</td><td>PII — Personal</td><td>Plaintext</td><td>Reversible token (vault)</td></tr>
    <tr><td>Bank account</td><td>PII — Financial</td><td>Encrypted AES-256</td><td>Masked (last 4 digits)</td></tr>
    <tr><td>Email address</td><td>PII — Personal</td><td>Plaintext</td><td>Hash (SHA-256)</td></tr>
    <tr><td>Transaction amounts</td><td>Financial — Non-PII</td><td>Plaintext</td><td>Plaintext (required for analytics)</td></tr>
    <tr><td>Transfer reference</td><td>Operational — Non-PII</td><td>Plaintext</td><td>Plaintext</td></tr>
  </table>

  <h2>7.2 dbt Data Quality Tests</h2>
  <p>The following dbt tests are applied at the Silver layer before any data is promoted to Gold:</p>

  <table>
    <tr><th>Test</th><th>Table</th><th>Severity</th></tr>
    <tr><td>not_null(transfer_id)</td><td>fact_remittance_transfer</td><td>Error</td></tr>
    <tr><td>unique(transfer_id)</td><td>fact_remittance_transfer</td><td>Error</td></tr>
    <tr><td>accepted_values(transfer_status)</td><td>fact_remittance_transfer</td><td>Error</td></tr>
    <tr><td>relationships(sender_customer_id → dim_customer)</td><td>fact_remittance_transfer</td><td>Error</td></tr>
    <tr><td>not_null(send_amount_zar)</td><td>fact_remittance_transfer</td><td>Error</td></tr>
    <tr><td>expression_is_true(send_amount_zar &gt; 0)</td><td>fact_remittance_transfer</td><td>Error</td></tr>
    <tr><td>expression_is_true(net_revenue_zar &lt; send_amount_zar)</td><td>fact_remittance_transfer</td><td>Warning</td></tr>
    <tr><td>not_null(customer_id)</td><td>dim_customer</td><td>Error</td></tr>
    <tr><td>unique(customer_id + scd_start_date)</td><td>dim_customer</td><td>Error</td></tr>
    <tr><td>at_most_one_current_row(customer_id)</td><td>dim_customer</td><td>Error</td></tr>
    <tr><td>no_future_dates(completed_datetime)</td><td>fact_remittance_transfer</td><td>Warning</td></tr>
    <tr><td>completed_after_created</td><td>fact_remittance_transfer</td><td>Error</td></tr>
  </table>

  <h2>7.3 POPIA &amp; GDPR Compliance</h2>
  <div class="highlight-box">
    <p>South Africa's <strong>Protection of Personal Information Act (POPIA)</strong> came into full effect on 1 July 2021. Key obligations for this platform:</p>
    <ul style="margin-top:10px;margin-left:20px;line-height:2">
      <li><strong>Lawful basis:</strong> Every personal data field must have a documented lawful basis (contract, legal obligation, or consent)</li>
      <li><strong>Data minimisation:</strong> The analytics layer must not contain more PII than necessary for the analytical purpose</li>
      <li><strong>Right to erasure:</strong> A "right to be forgotten" request must trigger pseudonymisation of all PII fields across Bronze, Silver, and Gold, while preserving aggregate analytics</li>
      <li><strong>Cross-border transfers:</strong> Sending customer data to cloud regions outside South Africa requires an adequacy assessment or binding corporate rules</li>
      <li><strong>Breach notification:</strong> Data breaches must be reported to the Information Regulator within 72 hours</li>
    </ul>
  </div>
</div>

<!-- ══ CHAPTER 8 ══════════════════════════════════════════════════════════ -->
<div class="chapter">
  <div class="chapter-header">
    <div class="ch-num">Chapter 08</div>
    <div class="ch-title">Implementation Roadmap</div>
    <div class="ch-subtitle">A three-phase plan from data foundation to real-time ML</div>
  </div>

  <h2>8.1 Phase 1 — Foundation (Months 1–3)</h2>
  <table>
    <tr><th>Month</th><th>Deliverable</th><th>Team</th></tr>
    <tr><td>1</td><td>Bronze layer: all source system connectors live; raw data flowing daily</td><td>Data Engineering</td></tr>
    <tr><td>1</td><td>DIM_DATE, DIM_BUSINESS, DIM_COUNTRY, DIM_CURRENCY loaded</td><td>Data Engineering</td></tr>
    <tr><td>2</td><td>Silver: STG_CUSTOMER, STG_TRANSFER with dbt tests passing at &gt;99.5%</td><td>Analytics Engineering</td></tr>
    <tr><td>2</td><td>PII tokenisation pipeline deployed; Bronze access controls locked down</td><td>Security / Platform</td></tr>
    <tr><td>3</td><td>MART_REMITTANCE, MART_CUSTOMER_360 in Gold; Power BI connected</td><td>Analytics Engineering</td></tr>
    <tr><td>3</td><td>Executive dashboard live: volume, revenue, MAC, success rate</td><td>BI / Analytics</td></tr>
  </table>

  <h2>8.2 Phase 2 — Analytics (Months 4–6)</h2>
  <table>
    <tr><th>Month</th><th>Deliverable</th><th>Team</th></tr>
    <tr><td>4</td><td>MART_FX_PROFITABILITY: spread analysis, margin by corridor live</td><td>Analytics Engineering</td></tr>
    <tr><td>4</td><td>MART_WALLET_CARD: wallet balances, card spend, salary deposits</td><td>Analytics Engineering</td></tr>
    <tr><td>5</td><td>MART_LOANS_MUKURU: credit portfolio, delinquency, ECL reporting</td><td>Analytics / Risk</td></tr>
    <tr><td>5</td><td>MART_INSURANCE_MUKURU: policy, premium, claims dashboard</td><td>Analytics</td></tr>
    <tr><td>6</td><td>MART_RISK_COMPLIANCE: fraud dashboard, KYC funnel, AML alerts</td><td>Risk / Compliance</td></tr>
    <tr><td>6</td><td>Partner network performance dashboard; settlement reconciliation</td><td>Operations</td></tr>
  </table>

  <h2>8.3 Phase 3 — ML &amp; Real-Time (Months 7–12)</h2>
  <table>
    <tr><th>Month</th><th>Deliverable</th><th>Team</th></tr>
    <tr><td>7</td><td>Fraud Detection Model v1: batch scoring nightly; threshold tuning</td><td>Data Science</td></tr>
    <tr><td>8</td><td>Fraud Model real-time API: &lt;50ms inference at transfer initiation</td><td>Data Science / MLOps</td></tr>
    <tr><td>9</td><td>Churn Prediction: weekly batch scores; CRM integration for campaigns</td><td>Data Science / CRM</td></tr>
    <tr><td>10</td><td>Credit PD Model: live at loan application; SHAP explanations for NCA</td><td>Data Science / Risk</td></tr>
    <tr><td>11</td><td>Transfer Success Model: real-time partner routing logic</td><td>Data Science / Ops</td></tr>
    <tr><td>12</td><td>Revenue Model: dynamic FX spread testing; A/B framework live</td><td>Data Science / Finance</td></tr>
  </table>

  <h2>8.4 Technology Stack Recommendations</h2>
  <table>
    <tr><th>Layer</th><th>Primary Option</th><th>Alternative</th></tr>
    <tr><td>Ingestion</td><td>Azure Data Factory / Fivetran</td><td>Apache NiFi, Airbyte</td></tr>
    <tr><td>Storage</td><td>Azure Data Lake Gen2 (Delta format)</td><td>AWS S3 + Iceberg, Snowflake</td></tr>
    <tr><td>Transformation</td><td>dbt + Databricks SQL</td><td>dbt + Snowflake, Synapse</td></tr>
    <tr><td>Orchestration</td><td>Apache Airflow (MWAA)</td><td>Azure Data Factory, Prefect</td></tr>
    <tr><td>ML Platform</td><td>Databricks MLflow</td><td>Azure ML, SageMaker</td></tr>
    <tr><td>BI / Reporting</td><td>Power BI Premium</td><td>Tableau, Looker</td></tr>
    <tr><td>Data Quality</td><td>dbt tests + Great Expectations</td><td>Monte Carlo, Soda Core</td></tr>
    <tr><td>Data Catalogue</td><td>Microsoft Purview</td><td>DataHub, Collibra</td></tr>
  </table>
</div>

<!-- ══ FOOTER ════════════════════════════════════════════════════════════ -->
<div class="footer">
  <p><strong>African Fintech Intelligence Platform</strong> — Technical Ebook &amp; Data Architecture Guide</p>
  <p style="margin-top:8px">Prepared by: <strong>Anthony Apollis</strong> &nbsp;|&nbsp; {TODAY} &nbsp;|&nbsp; Portfolio Project</p>
  <p style="margin-top:8px">Mukuru + Mama Money Unified Data Model &nbsp;|&nbsp; 40M+ rows &nbsp;|&nbsp; 5 ML models &nbsp;|&nbsp; Bronze → Silver → Gold</p>
  <p style="margin-top:12px;font-size:10px;color:#546E7A">
    This document is a portfolio demonstration using synthetic data. All figures, customer data, and business metrics are fictitious and generated for educational purposes. No confidential business information from Mukuru or Mama Money is used or reproduced.
  </p>
</div>

</body>
</html>
"""

# Write HTML ebook
out_html = EBOOK / "African_Fintech_Intelligence_Platform_Ebook.html"
with open(out_html, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"[SAVED] Ebook: {out_html}")
print(f"  Size: {out_html.stat().st_size / 1024:.0f} KB")
print(f"  Chapters: 8")
print(f"  Sections: 30+")
