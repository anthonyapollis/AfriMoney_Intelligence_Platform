"""
AfriMoney Intelligence Platform
Ebook Generator — bright African palette, Snowflake-first narrative,
illustrated UI screenshots, step-by-step explanations.
"""
from pathlib import Path
import datetime

BASE  = Path(r"C:\Users\Anthony.DESKTOP-ES5HL78\Documents\Fintech_Intelligence_Platform")
EBOOK = BASE / "ebook"
TODAY = datetime.date.today().isoformat()

CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
:root {
  --green:   #00A86B;
  --gold:    #F5A623;
  --coral:   #FF6B6B;
  --sky:     #4ECDC4;
  --navy:    #1B4F72;
  --cream:   #FFFDF7;
  --white:   #FFFFFF;
  --grey-lt: #F4F6F8;
  --grey-md: #DDE1E7;
  --text:    #1A2332;
  --text-lt: #5A6A7A;
  --snow-blue: #29B5E8;
  --snow-dark: #11567F;
  --dbt-orange: #FF694A;
}
body {
  font-family:'Segoe UI',system-ui,Arial,sans-serif;
  font-size:14px; line-height:1.75;
  color:var(--text); background:var(--cream);
}

/* ── COVER ── */
.cover {
  background: linear-gradient(145deg,#00A86B 0%,#4ECDC4 40%,#F5A623 100%);
  min-height:100vh; display:flex; flex-direction:column;
  justify-content:center; align-items:center; text-align:center;
  padding:60px 40px; page-break-after:always;
}
.cover-icon { font-size:80px; margin-bottom:16px; filter:drop-shadow(0 4px 12px rgba(0,0,0,0.2)); }
.cover-brand {
  font-size:56px; font-weight:900; letter-spacing:3px;
  color:#FFFFFF; text-shadow:0 4px 20px rgba(0,0,0,0.15);
  margin-bottom:6px;
}
.cover-tagline {
  font-size:20px; color:rgba(255,255,255,0.90); font-weight:300;
  margin-bottom:48px;
}
.cover-pills { display:flex; gap:14px; justify-content:center; flex-wrap:wrap; margin-bottom:40px; }
.pill {
  background:rgba(255,255,255,0.25); border:2px solid rgba(255,255,255,0.6);
  color:white; border-radius:50px; padding:8px 22px;
  font-weight:700; font-size:14px; backdrop-filter:blur(4px);
}
.pill.active { background:white; color:var(--green); }
.cover-stats {
  display:grid; grid-template-columns:repeat(3,1fr); gap:16px;
  max-width:780px; width:100%; margin-top:20px;
}
.stat-card {
  background:rgba(255,255,255,0.20); border:1px solid rgba(255,255,255,0.35);
  border-radius:16px; padding:22px 16px; backdrop-filter:blur(8px);
}
.stat-num { font-size:30px; font-weight:900; color:#FFFFFF; }
.stat-lbl { font-size:11px; color:rgba(255,255,255,0.85); text-transform:uppercase;
             letter-spacing:1.2px; margin-top:4px; }
.cover-meta { margin-top:48px; color:rgba(255,255,255,0.75); font-size:12px; }

/* ── TOC ── */
.toc {
  max-width:880px; margin:60px auto; background:white;
  border-radius:20px; padding:50px 60px;
  box-shadow:0 8px 40px rgba(0,168,107,0.10);
}
.toc h2 { font-size:26px; color:var(--navy); margin-bottom:28px;
           border-bottom:3px solid var(--green); padding-bottom:12px; }
.toc-item { display:flex; justify-content:space-between; padding:10px 0;
             border-bottom:1px dotted var(--grey-md); }
.toc-ch { color:var(--navy); font-weight:700; font-size:14px; }
.toc-sub { padding:5px 0 5px 22px; border-bottom:1px dotted #eee;
            font-size:13px; color:var(--text-lt); }

/* ── CHAPTER ── */
.chapter {
  max-width:880px; margin:0 auto 60px; background:white;
  border-radius:20px; padding:50px 60px;
  box-shadow:0 4px 24px rgba(0,0,0,0.06);
}
.ch-header {
  margin:-50px -60px 40px; padding:40px 60px; border-radius:20px 20px 0 0;
}
.ch-header.green  { background:linear-gradient(135deg,var(--green),#00d48a); }
.ch-header.gold   { background:linear-gradient(135deg,#D4890A,var(--gold)); }
.ch-header.coral  { background:linear-gradient(135deg,#E84040,var(--coral)); }
.ch-header.sky    { background:linear-gradient(135deg,#1A9E98,var(--sky)); }
.ch-header.navy   { background:linear-gradient(135deg,var(--navy),#2E86AB); }
.ch-header.snow   { background:linear-gradient(135deg,var(--snow-dark),var(--snow-blue)); }
.ch-header.dbt    { background:linear-gradient(135deg,#C0392B,var(--dbt-orange)); }
.ch-header.purple { background:linear-gradient(135deg,#6C3483,#A569BD); }
.ch-num  { font-size:11px; text-transform:uppercase; letter-spacing:3px;
           color:rgba(255,255,255,0.75); margin-bottom:8px; }
.ch-title   { font-size:30px; font-weight:900; color:white; line-height:1.2; }
.ch-subtitle{ font-size:15px; color:rgba(255,255,255,0.85); margin-top:8px; }

h2 { font-size:21px; color:var(--navy); margin:36px 0 14px;
     padding-bottom:8px; border-bottom:2px solid #E8F4FD; }
h3 { font-size:16px; color:var(--green); margin:24px 0 10px; font-weight:700; }
h4 { font-size:14px; color:var(--text); margin:18px 0 8px; font-weight:700; }
p  { margin-bottom:14px; }

/* ── CALLOUT BOXES ── */
.box {
  border-radius:12px; padding:18px 22px; margin:20px 0;
  border-left:5px solid;
}
.box.info   { background:#EBF8F3; border-color:var(--green); }
.box.warn   { background:#FFF8E8; border-color:var(--gold); }
.box.tip    { background:#EAF6FF; border-color:var(--sky); }
.box.danger { background:#FFEBEB; border-color:var(--coral); }
.box.snow   { background:#E8F6FF; border-color:var(--snow-blue); }
.box strong { font-weight:700; }

/* ── KPI CARDS ── */
.kpi-row { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:22px 0; }
.kpi-card {
  border-radius:14px; padding:20px; text-align:center;
  background:linear-gradient(135deg,var(--green),#00d48a);
  color:white;
}
.kpi-card.gold-card  { background:linear-gradient(135deg,#D4890A,var(--gold)); }
.kpi-card.sky-card   { background:linear-gradient(135deg,#1A9E98,var(--sky)); }
.kpi-card.coral-card { background:linear-gradient(135deg,#E84040,var(--coral)); }
.kpi-card.navy-card  { background:linear-gradient(135deg,var(--navy),#2E86AB); }
.kpi-card.snow-card  { background:linear-gradient(135deg,var(--snow-dark),var(--snow-blue)); }
.kpi-val { font-size:28px; font-weight:900; }
.kpi-lbl { font-size:10px; text-transform:uppercase; letter-spacing:1px;
            color:rgba(255,255,255,0.85); margin-top:5px; }

/* ── TABLES ── */
table { width:100%; border-collapse:collapse; margin:18px 0; font-size:13px; }
th { background:var(--navy); color:white; padding:10px 13px;
     text-align:left; font-weight:700; }
td { padding:9px 13px; border-bottom:1px solid var(--grey-md); vertical-align:top; }
tr:nth-child(even) td { background:var(--grey-lt); }

/* ── CODE BLOCKS ── */
.code {
  background:#0F2027; color:#E0E0E0; font-family:'Courier New',monospace;
  font-size:12px; padding:24px 28px; border-radius:12px; margin:18px 0;
  white-space:pre; overflow-x:auto; line-height:1.7;
  border:1px solid #1A3A4A;
}
.code .kw  { color:#4ECDC4; font-weight:bold; }
.code .str { color:#F5A623; }
.code .cm  { color:#6A8A9A; font-style:italic; }
.code .fn  { color:#FF6B6B; }
.code .val { color:#A8E6CF; }

/* ── SNOWFLAKE UI MOCKUPS ── */
.sf-window {
  border-radius:12px; overflow:hidden; margin:24px 0;
  box-shadow:0 8px 32px rgba(0,0,0,0.15);
  border:1px solid var(--grey-md);
}
.sf-titlebar {
  background:#11567F; padding:10px 16px; display:flex; align-items:center; gap:8px;
  color:white; font-size:12px; font-weight:600;
}
.sf-dot { width:12px; height:12px; border-radius:50%; }
.sf-dot.red { background:#FF5F57; }
.sf-dot.yellow { background:#FEBC2E; }
.sf-dot.green { background:#28C840; }
.sf-sidebar {
  background:#1B4F72; width:200px; float:left; min-height:320px;
  padding:16px 0; font-size:12px; color:#B0D4F1;
}
.sf-sidebar-item {
  padding:8px 20px; cursor:pointer; border-left:3px solid transparent;
}
.sf-sidebar-item.active { background:rgba(41,181,232,0.2); border-color:#29B5E8; color:white; }
.sf-body { margin-left:200px; padding:20px; background:#F8FAFB; min-height:320px; overflow:hidden; }
.sf-query-area {
  background:white; border:1px solid var(--grey-md); border-radius:8px;
  padding:14px; font-family:'Courier New',monospace; font-size:12px;
  color:#1A2332; line-height:1.8; margin-bottom:12px;
}
.sf-result-header {
  background:var(--snow-blue); color:white; padding:6px 12px;
  font-size:11px; font-weight:700; border-radius:6px 6px 0 0;
  display:flex; gap:16px;
}
.sf-result-table {
  background:white; border:1px solid var(--grey-md); border-radius:0 0 6px 6px;
}
.sf-result-table tr:first-child th { background:#E8F6FF; color:var(--navy); font-size:11px; }
.sf-result-table td { font-size:11px; padding:6px 10px; }
.sf-badge {
  display:inline-block; padding:2px 8px; border-radius:4px;
  font-size:10px; font-weight:700;
}
.sf-badge.success { background:#D5F5E3; color:#1E8449; }
.sf-badge.run     { background:#D6EAF8; color:#1A5276; }
.sf-badge.warn    { background:#FEF9E7; color:#9A7D0A; }

/* ── DBT DAG DIAGRAM ── */
.dag { background:#0F2027; border-radius:12px; padding:28px; margin:20px 0;
       font-family:'Courier New',monospace; font-size:12px; color:#A8E6CF;
       line-height:1.8; overflow-x:auto; white-space:pre; }
.dag .src  { color:#4ECDC4; }
.dag .stg  { color:#F5A623; }
.dag .int  { color:#FF6B6B; }
.dag .mart { color:#A8E6CF; font-weight:bold; }
.dag .arrow{ color:#5A6A7A; }

/* ── ARCH FLOW ── */
.flow { display:flex; gap:0; align-items:stretch; margin:24px 0; flex-wrap:wrap; }
.flow-box {
  flex:1; min-width:120px; padding:18px 14px; text-align:center;
  font-size:12px; font-weight:700; color:white; position:relative;
}
.flow-arrow {
  display:flex; align-items:center; color:var(--grey-md); font-size:20px;
  padding:0 4px;
}
.flow-box.src    { background:#1B4F72; border-radius:10px 0 0 10px; }
.flow-box.bronze { background:#C0392B; }
.flow-box.silver { background:#5D6D7E; }
.flow-box.gold   { background:#D4890A; border-radius:0 10px 10px 0; }

/* ── PIPELINE STEPS ── */
.step { display:flex; gap:16px; margin:16px 0; align-items:flex-start; }
.step-num {
  background:var(--green); color:white; border-radius:50%;
  width:32px; height:32px; display:flex; align-items:center; justify-content:center;
  font-weight:900; font-size:14px; flex-shrink:0; margin-top:2px;
}
.step-num.gold   { background:var(--gold); }
.step-num.coral  { background:var(--coral); }
.step-num.sky    { background:var(--sky); }
.step-num.navy   { background:var(--navy); }
.step-num.snow   { background:var(--snow-blue); }
.step-content h4 { margin:0 0 4px; color:var(--navy); }
.step-content p  { margin:0; color:var(--text-lt); font-size:13px; }

/* ── MODEL CARD ── */
.model-card {
  border:2px solid var(--grey-md); border-radius:14px; padding:20px;
  margin:16px 0; background:var(--grey-lt);
}
.model-card.active { border-color:var(--green); background:#EBF8F3; }
.metric-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
.chip {
  background:white; border:1px solid var(--grey-md); border-radius:20px;
  padding:3px 12px; font-size:11px; font-weight:600; color:var(--navy);
}
.chip.green-chip { background:#D5F5E3; border-color:var(--green); color:#1E8449; }

.footer {
  background:var(--navy); color:rgba(255,255,255,0.7); text-align:center;
  padding:36px; font-size:12px; margin-top:60px;
}
.footer strong { color:var(--gold); }
@media print { body{background:white;} .chapter{box-shadow:none;} }
"""

# ── SVG DIAGRAMS ──────────────────────────────────────────────

SNOWFLAKE_ARCH_SVG = """
<svg viewBox="0 0 800 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;border-radius:12px;margin:16px 0">
  <rect width="800" height="280" fill="#0F2027" rx="12"/>
  <!-- Layer labels -->
  <text x="80"  y="28" fill="#4ECDC4" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">SOURCE</text>
  <text x="220" y="28" fill="#FF6B6B" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">BRONZE</text>
  <text x="380" y="28" fill="#BDC3C7" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">SILVER (dbt)</text>
  <text x="550" y="28" fill="#F5A623" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">GOLD (dbt)</text>
  <text x="700" y="28" fill="#29B5E8" font-size="11" font-family="monospace" font-weight="bold" text-anchor="middle">CONSUME</text>

  <!-- Source boxes -->
  <rect x="20" y="42" width="120" height="28" rx="6" fill="#1B4F72"/>
  <text x="80" y="61" fill="white" font-size="10" font-family="monospace" text-anchor="middle">Mobile App</text>
  <rect x="20" y="76" width="120" height="28" rx="6" fill="#1B4F72"/>
  <text x="80" y="95" fill="white" font-size="10" font-family="monospace" text-anchor="middle">WhatsApp/USSD</text>
  <rect x="20" y="110" width="120" height="28" rx="6" fill="#1B4F72"/>
  <text x="80" y="129" fill="white" font-size="10" font-family="monospace" text-anchor="middle">Card Processor</text>
  <rect x="20" y="144" width="120" height="28" rx="6" fill="#1B4F72"/>
  <text x="80" y="163" fill="white" font-size="10" font-family="monospace" text-anchor="middle">FX Provider</text>
  <rect x="20" y="178" width="120" height="28" rx="6" fill="#1B4F72"/>
  <text x="80" y="197" fill="white" font-size="10" font-family="monospace" text-anchor="middle">Loan Platform</text>
  <rect x="20" y="212" width="120" height="28" rx="6" fill="#1B4F72"/>
  <text x="80" y="231" fill="white" font-size="10" font-family="monospace" text-anchor="middle">KYC/AML</text>

  <!-- Arrow S→B -->
  <text x="158" y="140" fill="#5A6A7A" font-size="18" font-family="Arial">→</text>

  <!-- Bronze boxes -->
  <rect x="170" y="42" width="100" height="28" rx="6" fill="#C0392B"/>
  <text x="220" y="61" fill="white" font-size="9" font-family="monospace" text-anchor="middle">COPY INTO stage</text>
  <rect x="170" y="76" width="100" height="28" rx="6" fill="#C0392B"/>
  <text x="220" y="95" fill="white" font-size="9" font-family="monospace" text-anchor="middle">dim_customer (SCD2)</text>
  <rect x="170" y="110" width="100" height="28" rx="6" fill="#C0392B"/>
  <text x="220" y="129" fill="white" font-size="9" font-family="monospace" text-anchor="middle">fact_transfer (5M)</text>
  <rect x="170" y="144" width="100" height="28" rx="6" fill="#C0392B"/>
  <text x="220" y="163" fill="white" font-size="9" font-family="monospace" text-anchor="middle">fact_fx_rate</text>
  <rect x="170" y="178" width="100" height="28" rx="6" fill="#C0392B"/>
  <text x="220" y="197" fill="white" font-size="9" font-family="monospace" text-anchor="middle">fact_wallet</text>
  <rect x="170" y="212" width="100" height="28" rx="6" fill="#C0392B"/>
  <text x="220" y="231" fill="white" font-size="9" font-family="monospace" text-anchor="middle">fact_loan_app</text>

  <!-- Arrow B→S -->
  <text x="278" y="140" fill="#5A6A7A" font-size="18" font-family="Arial">→</text>

  <!-- Silver boxes -->
  <rect x="298" y="42" width="110" height="28" rx="6" fill="#5D6D7E"/>
  <text x="353" y="61" fill="white" font-size="9" font-family="monospace" text-anchor="middle">stg_transfers</text>
  <rect x="298" y="76" width="110" height="28" rx="6" fill="#5D6D7E"/>
  <text x="353" y="95" fill="white" font-size="9" font-family="monospace" text-anchor="middle">stg_customers</text>
  <rect x="298" y="110" width="110" height="28" rx="6" fill="#5D6D7E"/>
  <text x="353" y="129" fill="white" font-size="9" font-family="monospace" text-anchor="middle">int_transfer_profit</text>
  <rect x="298" y="144" width="110" height="28" rx="6" fill="#5D6D7E"/>
  <text x="353" y="163" fill="white" font-size="9" font-family="monospace" text-anchor="middle">int_customer_stats</text>
  <rect x="298" y="178" width="110" height="28" rx="6" fill="#5D6D7E"/>
  <text x="353" y="197" fill="white" font-size="9" font-family="monospace" text-anchor="middle">int_risk_features</text>
  <rect x="298" y="212" width="110" height="28" rx="6" fill="#5D6D7E"/>
  <text x="353" y="231" fill="white" font-size="9" font-family="monospace" text-anchor="middle">stg_loans</text>

  <!-- Arrow S→G -->
  <text x="416" y="140" fill="#5A6A7A" font-size="18" font-family="Arial">→</text>

  <!-- Gold boxes -->
  <rect x="435" y="42" width="118" height="28" rx="6" fill="#D4890A"/>
  <text x="494" y="61" fill="white" font-size="9" font-family="monospace" text-anchor="middle">mart_remittance</text>
  <rect x="435" y="76" width="118" height="28" rx="6" fill="#D4890A"/>
  <text x="494" y="95" fill="white" font-size="9" font-family="monospace" text-anchor="middle">mart_customer_360</text>
  <rect x="435" y="110" width="118" height="28" rx="6" fill="#D4890A"/>
  <text x="494" y="129" fill="white" font-size="9" font-family="monospace" text-anchor="middle">mart_fx_profitability</text>
  <rect x="435" y="144" width="118" height="28" rx="6" fill="#D4890A"/>
  <text x="494" y="163" fill="white" font-size="9" font-family="monospace" text-anchor="middle">mart_wallet_card</text>
  <rect x="435" y="178" width="118" height="28" rx="6" fill="#D4890A"/>
  <text x="494" y="197" fill="white" font-size="9" font-family="monospace" text-anchor="middle">mart_loans_mukuru</text>
  <rect x="435" y="212" width="118" height="28" rx="6" fill="#D4890A"/>
  <text x="494" y="231" fill="white" font-size="9" font-family="monospace" text-anchor="middle">mart_risk_compliance</text>

  <!-- Arrow G→C -->
  <text x="561" y="140" fill="#5A6A7A" font-size="18" font-family="Arial">→</text>

  <!-- Consume boxes -->
  <rect x="580" y="56" width="110" height="28" rx="6" fill="#29B5E8"/>
  <text x="635" y="75" fill="white" font-size="9" font-family="monospace" text-anchor="middle">Power BI</text>
  <rect x="580" y="92" width="110" height="28" rx="6" fill="#29B5E8"/>
  <text x="635" y="111" fill="white" font-size="9" font-family="monospace" text-anchor="middle">Snowpark ML</text>
  <rect x="580" y="128" width="110" height="28" rx="6" fill="#29B5E8"/>
  <text x="635" y="147" fill="white" font-size="9" font-family="monospace" text-anchor="middle">Streamlit App</text>
  <rect x="580" y="164" width="110" height="28" rx="6" fill="#29B5E8"/>
  <text x="635" y="183" fill="white" font-size="9" font-family="monospace" text-anchor="middle">REST API (fraud)</text>
  <rect x="580" y="200" width="110" height="28" rx="6" fill="#29B5E8"/>
  <text x="635" y="219" fill="white" font-size="9" font-family="monospace" text-anchor="middle">Excel / CSV</text>

  <!-- Snowflake logo area -->
  <text x="748" y="260" fill="#29B5E8" font-size="10" font-family="monospace" text-anchor="middle">❄ Snowflake</text>
</svg>
"""

DBT_DAG_SVG = """
<svg viewBox="0 0 760 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;border-radius:12px;margin:16px 0">
  <rect width="760" height="200" fill="#0F2027" rx="12"/>
  <text x="20" y="22" fill="#6A8A9A" font-size="10" font-family="monospace">-- dbt run --select staging+ intermediate+ marts+ (green=success, orange=running)</text>

  <!-- SOURCE nodes -->
  <rect x="20" y="40" width="110" height="26" rx="5" fill="#1B4F72"/>
  <text x="75" y="57" fill="#4ECDC4" font-size="10" font-family="monospace" text-anchor="middle">source:bronze</text>
  <rect x="20" y="72" width="110" height="26" rx="5" fill="#1B4F72"/>
  <text x="75" y="89" fill="#4ECDC4" font-size="10" font-family="monospace" text-anchor="middle">source:bronze</text>
  <rect x="20" y="104" width="110" height="26" rx="5" fill="#1B4F72"/>
  <text x="75" y="121" fill="#4ECDC4" font-size="10" font-family="monospace" text-anchor="middle">source:bronze</text>

  <!-- Arrows S→stg -->
  <line x1="130" y1="53" x2="165" y2="53" stroke="#4ECDC4" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="130" y1="85" x2="165" y2="85" stroke="#4ECDC4" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="130" y1="117" x2="165" y2="117" stroke="#4ECDC4" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- STAGING nodes -->
  <rect x="165" y="40" width="120" height="26" rx="5" fill="#27AE60"/>
  <text x="225" y="57" fill="white" font-size="10" font-family="monospace" text-anchor="middle">stg_transfers ✓</text>
  <rect x="165" y="72" width="120" height="26" rx="5" fill="#27AE60"/>
  <text x="225" y="89" fill="white" font-size="10" font-family="monospace" text-anchor="middle">stg_customers ✓</text>
  <rect x="165" y="104" width="120" height="26" rx="5" fill="#27AE60"/>
  <text x="225" y="121" fill="white" font-size="10" font-family="monospace" text-anchor="middle">stg_fx_rates ✓</text>

  <!-- Arrows stg→int -->
  <line x1="285" y1="53" x2="315" y2="83" stroke="#27AE60" stroke-width="1.5"/>
  <line x1="285" y1="85" x2="315" y2="85" stroke="#27AE60" stroke-width="1.5"/>
  <line x1="285" y1="117" x2="315" y2="97" stroke="#27AE60" stroke-width="1.5"/>

  <!-- INTERMEDIATE nodes -->
  <rect x="315" y="48" width="140" height="26" rx="5" fill="#D4890A"/>
  <text x="385" y="65" fill="white" font-size="10" font-family="monospace" text-anchor="middle">int_transfer_profit ✓</text>
  <rect x="315" y="80" width="140" height="26" rx="5" fill="#D4890A"/>
  <text x="385" y="97" fill="white" font-size="10" font-family="monospace" text-anchor="middle">int_customer_stats ✓</text>
  <rect x="315" y="112" width="140" height="26" rx="5" fill="#D4890A"/>
  <text x="385" y="129" fill="white" font-size="10" font-family="monospace" text-anchor="middle">int_risk_features ✓</text>

  <!-- Arrows int→mart -->
  <line x1="455" y1="61" x2="490" y2="61" stroke="#D4890A" stroke-width="1.5"/>
  <line x1="455" y1="93" x2="490" y2="75" stroke="#D4890A" stroke-width="1.5"/>
  <line x1="455" y1="125" x2="490" y2="107" stroke="#D4890A" stroke-width="1.5"/>

  <!-- MART nodes -->
  <rect x="490" y="40" width="130" height="26" rx="5" fill="#00A86B"/>
  <text x="555" y="57" fill="white" font-size="10" font-family="monospace" text-anchor="middle">mart_remittance ✓</text>
  <rect x="490" y="72" width="130" height="26" rx="5" fill="#00A86B"/>
  <text x="555" y="89" fill="white" font-size="10" font-family="monospace" text-anchor="middle">mart_customer_360 ✓</text>
  <rect x="490" y="104" width="130" height="26" rx="5" fill="#00A86B"/>
  <text x="555" y="121" fill="white" font-size="10" font-family="monospace" text-anchor="middle">mart_fx_profit ✓</text>
  <rect x="490" y="136" width="130" height="26" rx="5" fill="#00A86B"/>
  <text x="555" y="153" fill="white" font-size="10" font-family="monospace" text-anchor="middle">mart_risk_compliance ✓</text>

  <!-- dbt legend -->
  <rect x="640" y="40" width="12" height="12" rx="2" fill="#1B4F72"/>
  <text x="656" y="51" fill="#B0BEC5" font-size="9" font-family="monospace">source</text>
  <rect x="640" y="58" width="12" height="12" rx="2" fill="#27AE60"/>
  <text x="656" y="69" fill="#B0BEC5" font-size="9" font-family="monospace">staging (view)</text>
  <rect x="640" y="76" width="12" height="12" rx="2" fill="#D4890A"/>
  <text x="656" y="87" fill="#B0BEC5" font-size="9" font-family="monospace">intermediate (table)</text>
  <rect x="640" y="94" width="12" height="12" rx="2" fill="#00A86B"/>
  <text x="656" y="105" fill="#B0BEC5" font-size="9" font-family="monospace">mart (table)</text>
  <text x="640" y="130" fill="#4ECDC4" font-size="9" font-family="monospace">✓ = test passed</text>

  <defs>
    <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
      <path d="M0,0 L0,6 L6,3 z" fill="#4ECDC4"/>
    </marker>
  </defs>
</svg>
"""

SNOWFLAKE_WORKSHEET_HTML = """
<div class="sf-window">
  <div class="sf-titlebar">
    <span class="sf-dot red"></span><span class="sf-dot yellow"></span><span class="sf-dot green"></span>
    &nbsp;&nbsp;Snowflake — AfriMoney Intelligence Platform — Worksheets
  </div>
  <div style="overflow:hidden">
    <div class="sf-sidebar">
      <div class="sf-sidebar-item">Databases</div>
      <div class="sf-sidebar-item" style="padding-left:28px">▼ AFRIMONEY_DB</div>
      <div class="sf-sidebar-item" style="padding-left:40px">● BRONZE</div>
      <div class="sf-sidebar-item" style="padding-left:40px">● SILVER</div>
      <div class="sf-sidebar-item active" style="padding-left:40px">● GOLD</div>
      <div class="sf-sidebar-item" style="padding-left:28px">▶ AFRIMONEY_ML_DB</div>
      <div class="sf-sidebar-item">Warehouses</div>
      <div class="sf-sidebar-item" style="padding-left:28px;color:#29B5E8">⚡ TRANSFORM_WH</div>
      <div class="sf-sidebar-item">Worksheets</div>
      <div class="sf-sidebar-item active" style="padding-left:28px">📋 mart_remittance</div>
      <div class="sf-sidebar-item" style="padding-left:28px">📋 customer_360</div>
      <div class="sf-sidebar-item" style="padding-left:28px">📋 fraud_analysis</div>
    </div>
    <div class="sf-body">
      <div class="sf-query-area">
<span style="color:#29B5E8;font-weight:bold">SELECT</span>
  business_key,
  corridor_code,
  created_month,
  initiated_count,
  completed_count,
  <span style="color:#00A86B">ROUND</span>(success_rate_pct, 2)      <span style="color:#6A8A9A">AS success_rate</span>,
  <span style="color:#00A86B">ROUND</span>(total_net_revenue_zar/1e6, 2) <span style="color:#6A8A9A">AS revenue_M_ZAR</span>,
  avg_fx_spread_pct,
  median_completion_minutes
<span style="color:#29B5E8;font-weight:bold">FROM</span> AFRIMONEY_DB.GOLD.MART_REMITTANCE
<span style="color:#29B5E8;font-weight:bold">WHERE</span> created_month <span style="color:#29B5E8;font-weight:bold">BETWEEN</span> <span style="color:#F5A623">'2026-01'</span> <span style="color:#29B5E8;font-weight:bold">AND</span> <span style="color:#F5A623">'2026-06'</span>
  <span style="color:#29B5E8;font-weight:bold">AND</span> completed_count > 100
<span style="color:#29B5E8;font-weight:bold">ORDER BY</span> revenue_M_ZAR <span style="color:#29B5E8;font-weight:bold">DESC</span>
<span style="color:#29B5E8;font-weight:bold">LIMIT</span> 20;
      </div>
      <div class="sf-result-header">
        <span>✓ Query succeeded &nbsp;|&nbsp; 18 rows &nbsp;|&nbsp; 0.3s &nbsp;|&nbsp; TRANSFORM_WH (LARGE)</span>
        <span style="margin-left:auto"><span class="sf-badge run">COMPLETED</span></span>
      </div>
      <div class="sf-result-table">
        <table style="margin:0;font-size:11px">
          <tr><th>BUSINESS_KEY</th><th>CORRIDOR_CODE</th><th>CREATED_MONTH</th><th>INITIATED</th><th>COMPLETED</th><th>SUCCESS%</th><th>REVENUE_M_ZAR</th><th>FX_SPREAD%</th></tr>
          <tr><td>MKR</td><td>ZA-ZW</td><td>2026-06</td><td>28,412</td><td>22,156</td><td>78.0</td><td>4.82</td><td>5.41</td></tr>
          <tr><td>MKR</td><td>ZA-MZ</td><td>2026-06</td><td>18,930</td><td>14,772</td><td>78.0</td><td>3.21</td><td>5.38</td></tr>
          <tr><td>MMY</td><td>ZA-ZW</td><td>2026-06</td><td>11,240</td><td>8,767</td><td>78.0</td><td>1.91</td><td>5.45</td></tr>
          <tr><td>MKR</td><td>ZA-ZM</td><td>2026-06</td><td>9,810</td><td>7,652</td><td>78.0</td><td>1.66</td><td>5.39</td></tr>
          <tr><td>MMY</td><td>ZA-MZ</td><td>2026-06</td><td>7,544</td><td>5,884</td><td>78.0</td><td>1.28</td><td>5.42</td></tr>
        </table>
      </div>
    </div>
  </div>
</div>
"""

SNOWFLAKE_ML_HTML = """
<div class="sf-window">
  <div class="sf-titlebar">
    <span class="sf-dot red"></span><span class="sf-dot yellow"></span><span class="sf-dot green"></span>
    &nbsp;&nbsp;Snowflake ML — Model Registry — AfriMoney Models
  </div>
  <div style="padding:20px;background:#F8FAFB">
    <div style="background:white;border-radius:10px;padding:16px;border:1px solid #DDE1E7;margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div style="font-weight:800;color:#11567F;font-size:14px">FRAUD_DETECTION</div>
          <div style="font-size:11px;color:#6A8A9A">v1_20260628 &nbsp;|&nbsp; GradientBoostingClassifier &nbsp;|&nbsp; Snowpark ML</div>
        </div>
        <span class="sf-badge success">PRODUCTION</span>
      </div>
      <div style="display:flex;gap:16px;margin-top:10px;font-size:12px">
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">AUC: 0.9124</span>
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">Avg Precision: 0.7831</span>
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">Features: 15</span>
        <span style="background:#D5F5E3;color:#1E8449;padding:3px 10px;border-radius:6px">Latency: 42ms p99</span>
      </div>
    </div>
    <div style="background:white;border-radius:10px;padding:16px;border:1px solid #DDE1E7;margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div style="font-weight:800;color:#11567F;font-size:14px">CUSTOMER_CHURN</div>
          <div style="font-size:11px;color:#6A8A9A">v1_20260628 &nbsp;|&nbsp; RandomForestClassifier &nbsp;|&nbsp; Weekly batch</div>
        </div>
        <span class="sf-badge success">PRODUCTION</span>
      </div>
      <div style="display:flex;gap:16px;margin-top:10px;font-size:12px">
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">AUC: 0.8612</span>
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">Churn Rate: 44.8%</span>
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">Features: 21</span>
        <span style="background:#FEF9E7;color:#9A7D0A;padding:3px 10px;border-radius:6px">Drift: monitoring</span>
      </div>
    </div>
    <div style="background:white;border-radius:10px;padding:16px;border:1px solid #DDE1E7">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div style="font-weight:800;color:#11567F;font-size:14px">CREDIT_RISK_PD</div>
          <div style="font-size:11px;color:#6A8A9A">v1_20260628 &nbsp;|&nbsp; GradientBoostingClassifier &nbsp;|&nbsp; Mukuru only</div>
        </div>
        <span class="sf-badge success">PRODUCTION</span>
      </div>
      <div style="display:flex;gap:16px;margin-top:10px;font-size:12px">
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">AUC: 0.7841</span>
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">Default Rate: 11.2%</span>
        <span style="background:#E8F6FF;color:#11567F;padding:3px 10px;border-radius:6px">SHAP: enabled</span>
        <span style="background:#FFEBEB;color:#C0392B;padding:3px 10px;border-radius:6px">NCA compliant</span>
      </div>
    </div>
  </div>
</div>
"""

DBT_TERMINAL_HTML = """
<div style="background:#0F2027;border-radius:12px;padding:24px;margin:20px 0;font-family:'Courier New',monospace;font-size:12px;line-height:1.9">
  <div style="color:#6A8A9A;margin-bottom:8px">$ dbt run --select staging+ intermediate+ marts+ --target prod</div>
  <div style="color:#4ECDC4">Running with dbt=1.8.0</div>
  <div style="color:#6A8A9A">Found 14 models, 28 tests, 13 sources, 4 macros</div>
  <div style="color:#6A8A9A">Concurrency: 16 threads (target='prod')</div>
  <br>
  <div style="color:#6A8A9A">1 of 14 START view model SILVER.stg_transfers ........... [<span style="color:#F5A623">RUN</span>]</div>
  <div style="color:#6A8A9A">1 of 14 OK created view SILVER.stg_transfers ............. [<span style="color:#27AE60">OK</span> in 0.8s]</div>
  <div style="color:#6A8A9A">2 of 14 START view model SILVER.stg_customers ........... [<span style="color:#F5A623">RUN</span>]</div>
  <div style="color:#6A8A9A">2 of 14 OK created view SILVER.stg_customers ............. [<span style="color:#27AE60">OK</span> in 0.7s]</div>
  <div style="color:#6A8A9A">3 of 14 START table model SILVER.int_transfer_profitability [<span style="color:#F5A623">RUN</span>]</div>
  <div style="color:#6A8A9A">3 of 14 OK created table SILVER.int_transfer_profitability [<span style="color:#27AE60">OK</span> in 18.4s]</div>
  <div style="color:#6A8A9A">4 of 14 START table model SILVER.int_customer_transfer_stats [<span style="color:#F5A623">RUN</span>]</div>
  <div style="color:#6A8A9A">4 of 14 OK created table SILVER.int_customer_transfer_stats [<span style="color:#27AE60">OK</span> in 22.1s]</div>
  <div style="color:#6A8A9A">...</div>
  <div style="color:#6A8A9A">12 of 14 START table model GOLD.mart_remittance .......... [<span style="color:#F5A623">RUN</span>]</div>
  <div style="color:#6A8A9A">12 of 14 OK created table GOLD.mart_remittance ........... [<span style="color:#27AE60">OK</span> in 31.7s]</div>
  <div style="color:#6A8A9A">13 of 14 START table model GOLD.mart_customer_360 ....... [<span style="color:#F5A623">RUN</span>]</div>
  <div style="color:#6A8A9A">13 of 14 OK created table GOLD.mart_customer_360 ......... [<span style="color:#27AE60">OK</span> in 44.2s]</div>
  <div style="color:#6A8A9A">14 of 14 START table model GOLD.mart_risk_compliance .... [<span style="color:#F5A623">RUN</span>]</div>
  <div style="color:#6A8A9A">14 of 14 OK created table GOLD.mart_risk_compliance ...... [<span style="color:#27AE60">OK</span> in 19.8s]</div>
  <br>
  <div style="color:#27AE60;font-weight:bold">Finished running 14 models in 2 minutes 18.3 seconds.</div>
  <br>
  <div style="color:#27AE60">✓  14 of 14 models OK</div>
  <div style="color:#27AE60">✓  28 of 28 tests passed</div>
  <div style="color:#E74C3C">✗   0 errors &nbsp; 0 warnings</div>
  <br>
  <div style="color:#29B5E8">Done. PASS=14 WARN=0 ERROR=0 SKIP=0 TOTAL=14</div>
</div>
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AfriMoney Intelligence Platform — Technical Ebook</title>
<style>{CSS}</style>
</head>
<body>

<!-- ══ COVER ══ -->
<div class="cover">
  <div class="cover-icon">🌍</div>
  <div class="cover-brand">AfriMoney</div>
  <div class="cover-tagline">Intelligence Platform &nbsp;|&nbsp; Mukuru + Mama Money Unified on Snowflake</div>
  <div class="cover-pills">
    <span class="pill active">Snowflake</span>
    <span class="pill">dbt</span>
    <span class="pill">Snowpark ML</span>
    <span class="pill">Power BI</span>
    <span class="pill">Bronze→Silver→Gold</span>
  </div>
  <div class="cover-stats">
    <div class="stat-card"><div class="stat-num">40M+</div><div class="stat-lbl">Rows in Snowflake</div></div>
    <div class="stat-card"><div class="stat-num">5M</div><div class="stat-lbl">Transfer Orders</div></div>
    <div class="stat-card"><div class="stat-num">500K</div><div class="stat-lbl">Customers SCD2</div></div>
    <div class="stat-card"><div class="stat-num">14</div><div class="stat-lbl">dbt Models</div></div>
    <div class="stat-card"><div class="stat-num">3</div><div class="stat-lbl">Snowpark ML Models</div></div>
    <div class="stat-card"><div class="stat-num">28</div><div class="stat-lbl">dbt Tests Passing</div></div>
  </div>
  <div class="cover-meta">Anthony Apollis &nbsp;|&nbsp; {TODAY} &nbsp;|&nbsp; Data Engineering Portfolio</div>
</div>

<!-- ══ TOC ══ -->
<div class="toc">
  <h2>Table of Contents</h2>
  <div class="toc-item"><span class="toc-ch">Chapter 1 — What is AfriMoney?</span></div>
  <div class="toc-sub">1.1 The business problem · 1.2 Mukuru deep-dive · 1.3 Mama Money deep-dive · 1.4 Why one platform?</div>
  <div class="toc-item"><span class="toc-ch">Chapter 2 — Snowflake Account Architecture</span></div>
  <div class="toc-sub">2.1 Virtual warehouses · 2.2 Databases & schemas · 2.3 RBAC & network policies · 2.4 Internal stages</div>
  <div class="toc-item"><span class="toc-ch">Chapter 3 — Bronze Layer: Raw Ingestion</span></div>
  <div class="toc-sub">3.1 Source systems · 3.2 File format & stage · 3.3 COPY INTO · 3.4 Load verification · 3.5 Snowflake UI walkthrough</div>
  <div class="toc-item"><span class="toc-ch">Chapter 4 — Silver Layer with dbt</span></div>
  <div class="toc-sub">4.1 Why dbt? · 4.2 Project structure · 4.3 Staging models · 4.4 Intermediate models · 4.5 Testing & freshness · 4.6 DAG walkthrough</div>
  <div class="toc-item"><span class="toc-ch">Chapter 5 — Gold Layer: Analytical Marts</span></div>
  <div class="toc-sub">5.1 mart_remittance · 5.2 mart_customer_360 · 5.3 mart_fx_profitability · 5.4 mart_risk_compliance · 5.5 Power BI connection</div>
  <div class="toc-item"><span class="toc-ch">Chapter 6 — Snowpark ML Pipeline</span></div>
  <div class="toc-sub">6.1 Why Snowpark? · 6.2 Feature Store · 6.3 Fraud detection · 6.4 Churn prediction · 6.5 Credit risk PD · 6.6 Model Registry · 6.7 UDFs & stored procedures</div>
  <div class="toc-item"><span class="toc-ch">Chapter 7 — KPI Framework & Business Intelligence</span></div>
  <div class="toc-item"><span class="toc-ch">Chapter 8 — Data Governance, PII & Compliance</span></div>
  <div class="toc-item"><span class="toc-ch">Chapter 9 — Implementation Roadmap</span></div>
</div>

<!-- ══ CH 1 ══ -->
<div class="chapter">
  <div class="ch-header green">
    <div class="ch-num">Chapter 01</div>
    <div class="ch-title">What is AfriMoney?</div>
    <div class="ch-subtitle">The African remittance market and the case for a unified intelligence platform</div>
  </div>

  <h2>1.1 The Business Problem</h2>
  <p>South Africa is home to an estimated <strong>3.5 million foreign nationals</strong> from neighbouring countries — primarily Zimbabwe, Mozambique, Zambia, and Malawi. These workers send money home regularly to support families, pay school fees, and fund small businesses. The remittance corridor from South Africa to sub-Saharan Africa moves <strong>billions of rand every month</strong>.</p>

  <div class="kpi-row">
    <div class="kpi-card"><div class="kpi-val">R 78B+</div><div class="kpi-lbl">Annual SA Outbound Volume</div></div>
    <div class="kpi-card gold-card"><div class="kpi-val">17</div><div class="kpi-lbl">Active Corridors Modelled</div></div>
    <div class="kpi-card sky-card"><div class="kpi-val">6–8%</div><div class="kpi-lbl">Avg Transfer Cost (World Bank)</div></div>
  </div>

  <p>Despite this volume, most remittance operators lack a unified data platform. Customer data lives in siloed CRMs, transfer records are in separate operational databases, KYC documents are stored in a different system, and FX rates come from yet another feed. The result: <em>no single view of the customer, the corridor, or the business.</em></p>

  <div class="box info">
    <strong>AfriMoney's answer:</strong> One Snowflake data platform that ingests from every source system across both brands (Mukuru and Mama Money), standardises the data through a Bronze → Silver → Gold medallion architecture, powers 14 dbt models, and runs 3 Snowpark ML models — all without data leaving Snowflake.
  </div>

  <h2>1.2 Mukuru — Africa's Largest Money Transfer Operator</h2>
  <p>Founded in 2004 in Zimbabwe, Mukuru has grown to serve over 17 million customers across 50+ countries. Its product suite extends well beyond money transfers:</p>
  <table>
    <tr><th>Product</th><th>Description</th><th>Data Domain</th></tr>
    <tr><td>International Remittances</td><td>Cash, bank, mobile wallet payouts to 15+ countries</td><td>FACT_REMITTANCE_TRANSFER</td></tr>
    <tr><td>Mukuru Card</td><td>Prepaid Mastercard; salary, spending, cash access</td><td>FACT_CARD_TRANSACTION</td></tr>
    <tr><td>Mukuru Fast Loan</td><td>Short-term credit linked to Card eligibility</td><td>FACT_LOAN_APPLICATION</td></tr>
    <tr><td>Mukuru Funeral Cover</td><td>Micro-insurance with repatriation service</td><td>FACT_INSURANCE_POLICY</td></tr>
    <tr><td>MukuruPay</td><td>Bill payments, merchant payments, cash e-commerce</td><td>FACT_BILL_PAYMENT</td></tr>
    <tr><td>Dollar Savings</td><td>USD-denominated savings product</td><td>FACT_USD_SAVINGS</td></tr>
  </table>

  <h2>1.3 Mama Money — Wallet-First Fintech Challenger</h2>
  <p>Founded in 2015 with a focus on transparency and affordability, Mama Money's ISO 9001 certified platform puts the <strong>wallet at the centre</strong> of everything. Every product — transfers, card, savings — flows through the wallet.</p>
  <table>
    <tr><th>Product</th><th>Unique Feature</th><th>Data Domain</th></tr>
    <tr><td>Mama Money Send</td><td>Transfers to 13+ countries via mobile wallet, cash, bank</td><td>FACT_REMITTANCE_TRANSFER</td></tr>
    <tr><td>Mama Wallet</td><td>ZAR digital wallet — hub of all activity</td><td>FACT_WALLET_LEDGER</td></tr>
    <tr><td>Mama Card</td><td>Salary deposits, card spend, airtime, electricity</td><td>FACT_CARD_TRANSACTION</td></tr>
    <tr><td>Save in USD</td><td><strong>USDC-backed stablecoin</strong> savings — not a bank account</td><td>FACT_USD_SAVINGS</td></tr>
    <tr><td>Send More with Mama</td><td>Structured limit uplift via document submission</td><td>CUSTOMER_LIMIT_PROFILE</td></tr>
  </table>

  <div class="box warn">
    <strong>Important modelling note:</strong> Mama Money's "Save in USD" product is backed by USDC (USD Coin), a regulated stablecoin. The data model must distinguish the <em>displayed currency (USD)</em> from the <em>underlying digital asset (USDC)</em>. It carries different regulatory obligations than a standard bank account.
  </div>

  <h2>1.4 Why One Platform?</h2>
  <p>The strongest architecture is <strong>one shared Snowflake database with a <code>BUSINESS_KEY</code> dimension</strong> (MKR / MMY) distinguishing the two brands. This enables:</p>
  <ul style="margin-left:22px;line-height:2.2">
    <li>Executive reporting across both brands from a single Power BI dataset</li>
    <li>Cross-brand fraud signals (a customer flagged on Mukuru is detectable on Mama Money)</li>
    <li>Shared KYC cost — one verification framework, two brand touchpoints</li>
    <li>Unified customer 360 for product cross-sell analytics</li>
    <li>Consistent ML features — fraud and churn models benefit from full transaction history</li>
  </ul>
</div>

<!-- ══ CH 2 ══ -->
<div class="chapter">
  <div class="ch-header snow">
    <div class="ch-num">Chapter 02</div>
    <div class="ch-title">Snowflake Account Architecture</div>
    <div class="ch-subtitle">Warehouses, databases, schemas, roles, and the internal stage setup</div>
  </div>

  <h2>2.1 Why Snowflake?</h2>
  <p>AfriMoney chose Snowflake as its cloud data platform for four reasons:</p>
  <ol style="margin-left:22px;line-height:2.2">
    <li><strong>Separation of compute and storage</strong> — the 40M-row dataset costs nothing when no query is running; warehouses auto-suspend after 60–120 seconds of inactivity.</li>
    <li><strong>Zero-copy cloning</strong> — the Bronze layer can be cloned instantly for testing without duplicating 500 GB of storage.</li>
    <li><strong>Snowpark ML</strong> — Python ML code runs <em>inside</em> Snowflake; raw PII never leaves the platform to an external training server.</li>
    <li><strong>Time Travel &amp; Fail-Safe</strong> — 90-day time travel on all fact tables means any accidental delete or bad load can be recovered with a single <code>UNDROP</code> or <code>SELECT ... AT(OFFSET)</code> query.</li>
  </ol>

  <h2>2.2 Virtual Warehouse Strategy</h2>
  <table>
    <tr><th>Warehouse</th><th>Size</th><th>Purpose</th><th>Auto-Suspend</th></tr>
    <tr><td>AFRIMONEY_INGEST_WH</td><td>MEDIUM</td><td>COPY INTO loads from stage</td><td>120s</td></tr>
    <tr><td>AFRIMONEY_TRANSFORM_WH</td><td>LARGE</td><td>dbt runs (Silver + Gold)</td><td>60s</td></tr>
    <tr><td>AFRIMONEY_ANALYTICS_WH</td><td>SMALL</td><td>Power BI queries, ad-hoc</td><td>300s</td></tr>
    <tr><td>AFRIMONEY_ML_WH</td><td>X-LARGE</td><td>Snowpark ML training (multi-cluster)</td><td>60s</td></tr>
  </table>

  <div class="box tip">
    <strong>Cost tip:</strong> The ML warehouse is X-LARGE and multi-cluster (1–4 nodes). It should only be active during scheduled training jobs (Sunday 02:00 SAST). An automated Snowflake Task calls the stored procedure and then the warehouse auto-suspends — typical cost per weekly training run: ~$8–15 USD.
  </div>

  <h2>2.3 Database &amp; Schema Layout</h2>
  <div class="code"><span class="kw">-- AFRIMONEY_DB</span>
├── BRONZE   <span class="cm">-- raw, immutable; COPY INTO lands here</span>
├── SILVER   <span class="cm">-- dbt staging views + intermediate tables</span>
├── GOLD     <span class="cm">-- dbt mart tables; Power BI connects here</span>
├── STAGING  <span class="cm">-- internal stage for CSV uploads</span>
└── UTILS    <span class="cm">-- shared UDFs, macros, stored procedures</span>

<span class="kw">-- AFRIMONEY_ML_DB</span>
├── FEATURE_STORE   <span class="cm">-- ML feature tables (refresh daily)</span>
├── EXPERIMENTS     <span class="cm">-- training run logs + metrics</span>
├── MODEL_REGISTRY  <span class="cm">-- registered model versions</span>
└── PREDICTIONS     <span class="cm">-- scored output tables</span></div>

  <h2>2.4 RBAC — Role-Based Access Control</h2>
  <p>Snowflake's RBAC system ensures that a Power BI analyst can never modify the Bronze layer, and a data engineer can never see the ML model weights. The role hierarchy looks like this:</p>
  <div class="code">ACCOUNTADMIN
└── SYSADMIN
    └── <span class="fn">AFRIMONEY_ADMIN</span>
        ├── <span class="fn">AFRIMONEY_ENG</span>     <span class="cm">-- WRITE on Bronze/Silver, CREATE on Gold</span>
        ├── <span class="fn">AFRIMONEY_ANALYST</span>  <span class="cm">-- READ on Gold only</span>
        │   └── <span class="fn">AFRIMONEY_VIEWER</span>  <span class="cm">-- READ Gold (Power BI service account)</span>
        └── <span class="fn">AFRIMONEY_ML_ENG</span>   <span class="cm">-- WRITE on ML_DB only</span></div>
</div>

<!-- ══ CH 3 ══ -->
<div class="chapter">
  <div class="ch-header coral">
    <div class="ch-num">Chapter 03</div>
    <div class="ch-title">Bronze Layer — Raw Ingestion with COPY INTO</div>
    <div class="ch-subtitle">How 40 million rows of synthetic fintech data land in Snowflake, immutably and verifiably</div>
  </div>

  <h2>3.1 Source Systems Inventory</h2>
  <p>The Bronze layer ingests from 12 source system categories. Each source system writes to its own subfolder in the Snowflake internal stage (<code>@STAGING.AFRIMONEY_STAGE/</code>), and a dedicated <code>COPY INTO</code> command loads each table.</p>

  <div class="box info">
    <strong>Bronze design rule:</strong> Bronze tables are <em>append-only and immutable</em>. We never UPDATE or DELETE in Bronze. If a record is wrong, the correction happens in Silver (dbt). This means we always have a full audit trail back to the raw source data.
  </div>

  <h2>3.2 The ETL Pipeline — Step by Step</h2>

  <div class="step">
    <div class="step-num">1</div>
    <div class="step-content">
      <h4>Generate synthetic data (Python)</h4>
      <p>40M+ rows across 20 table types generated with realistic distributions — lognormal transfer amounts, correlated fraud patterns, seasonal transfer volumes.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num gold">2</div>
    <div class="step-content">
      <h4>Upload CSVs to Snowflake internal stage</h4>
      <p><code>PUT file://data/bronze/*.csv @STAGING.AFRIMONEY_STAGE AUTO_COMPRESS=TRUE</code> — Snowflake compresses and stores in its own S3/Azure Blob; you pay storage, not egress.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num coral">3</div>
    <div class="step-content">
      <h4>COPY INTO Bronze tables</h4>
      <p>The <code>COPY INTO</code> command reads from the stage and loads into the Bronze table. The <code>AFRIMONEY_CSV_FORMAT</code> file format handles nulls, quoted fields, and type casting automatically.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num sky">4</div>
    <div class="step-content">
      <h4>Verify via COPY_HISTORY &amp; INFORMATION_SCHEMA</h4>
      <p>Snowflake records every COPY INTO in <code>INFORMATION_SCHEMA.COPY_HISTORY</code>. Query it to confirm row counts, check for errors, and audit the load time.</p>
    </div>
  </div>
  <div class="step">
    <div class="step-num navy">5</div>
    <div class="step-content">
      <h4>Cluster keys applied automatically</h4>
      <p>All large fact tables are clustered by <code>BUSINESS_KEY</code> and <code>TO_DATE(created_datetime)</code>. Snowflake automatically reclusters over time — queries that filter by date scan only the relevant micro-partitions.</p>
    </div>
  </div>

  <h2>3.3 Snowflake Worksheet — Bronze Query</h2>
  {SNOWFLAKE_WORKSHEET_HTML}

  <h2>3.4 COPY INTO Performance</h2>
  <table>
    <tr><th>Table</th><th>Rows</th><th>File Size</th><th>Load Time (LARGE WH)</th></tr>
    <tr><td>dim_customer</td><td>500,000</td><td>114 MB</td><td>~12s</td></tr>
    <tr><td>dim_recipient</td><td>1,000,000</td><td>120 MB</td><td>~15s</td></tr>
    <tr><td>fact_remittance_transfer</td><td>5,000,000</td><td>~900 MB</td><td>~65s</td></tr>
    <tr><td>fact_wallet_ledger</td><td>~10,000,000</td><td>~1.6 GB</td><td>~120s</td></tr>
    <tr><td>fact_transfer_status_history</td><td>~7,500,000</td><td>~800 MB</td><td>~90s</td></tr>
    <tr><td><strong>All tables</strong></td><td><strong>~40M+</strong></td><td><strong>~5 GB</strong></td><td><strong>~8 min total</strong></td></tr>
  </table>
</div>

<!-- ══ CH 4 ══ -->
<div class="chapter">
  <div class="ch-header dbt">
    <div class="ch-num">Chapter 04</div>
    <div class="ch-title">Silver Layer with dbt</div>
    <div class="ch-subtitle">Transforming raw Bronze data into clean, tested, canonical Silver models using dbt on Snowflake</div>
  </div>

  <h2>4.1 Why dbt?</h2>
  <p>dbt (data build tool) is the industry standard for SQL-first data transformation. On Snowflake it compiles your <code>.sql</code> model files into <code>CREATE TABLE AS SELECT</code> or <code>CREATE VIEW AS</code> statements and runs them in the right order based on the DAG (Directed Acyclic Graph) of <code>ref()</code> calls.</p>

  <div class="box tip">
    <strong>Key benefit:</strong> Every dbt model is <em>version-controlled in Git</em>, <em>tested automatically</em>, and <em>documented inline</em>. When a business analyst asks "where does the revenue figure in the dashboard come from?", the answer is traceable all the way back to a line in a Bronze CSV.
  </div>

  <h2>4.2 Project Structure</h2>
  <div class="code">afrimoney/
├── dbt_project.yml         <span class="cm"># project config — materialisations, warehouses</span>
├── profiles.yml            <span class="cm"># Snowflake connection (dev + prod targets)</span>
├── models/
│   ├── staging/            <span class="cm"># SILVER schema — VIEWs over Bronze</span>
│   │   ├── stg_transfers.sql
│   │   ├── stg_customers.sql
│   │   ├── stg_fx_rates.sql
│   │   └── stg_loans.sql
│   ├── intermediate/       <span class="cm"># SILVER schema — TABLEs with business logic</span>
│   │   ├── int_transfer_profitability.sql
│   │   ├── int_customer_transfer_stats.sql
│   │   └── int_risk_features.sql
│   └── marts/              <span class="cm"># GOLD schema — TABLEs for Power BI</span>
│       ├── mart_remittance.sql
│       ├── mart_customer_360.sql
│       ├── mart_fx_profitability.sql
│       └── mart_risk_compliance.sql
├── tests/
│   └── generic_tests.yml   <span class="cm"># not_null, unique, accepted_values, relationships</span>
└── macros/
    └── afrimoney_macros.sql <span class="cm"># div0, safe_divide, business_day helpers</span></div>

  <h2>4.3 Materialisation Strategy</h2>
  <table>
    <tr><th>Layer</th><th>Materialisation</th><th>Why?</th></tr>
    <tr><td>Staging</td><td><strong>view</strong></td><td>No storage cost; always reads fresh from Bronze. Fast to iterate during development.</td></tr>
    <tr><td>Intermediate</td><td><strong>table</strong></td><td>Heavy joins and aggregations (5M transfer × 500K customer). Pay compute once, reuse many times.</td></tr>
    <tr><td>Marts</td><td><strong>table</strong></td><td>Power BI connects here. Sub-second query response requires pre-materialised tables.</td></tr>
  </table>

  <h2>4.4 dbt DAG — Full Pipeline</h2>
  {DBT_DAG_SVG}

  <h2>4.5 dbt Run Output</h2>
  {DBT_TERMINAL_HTML}

  <h2>4.6 Key dbt Tests</h2>
  <p>28 tests run automatically after every <code>dbt run</code>. The most important ones:</p>
  <table>
    <tr><th>Test</th><th>Model</th><th>What it catches</th></tr>
    <tr><td>unique(transfer_id)</td><td>stg_transfers</td><td>Duplicate records from source — a common ETL bug</td></tr>
    <tr><td>not_null(send_amount_zar)</td><td>stg_transfers</td><td>Missing amounts that would corrupt revenue totals</td></tr>
    <tr><td>relationships(sender_customer_id)</td><td>stg_transfers</td><td>Orphaned transfers with no customer record</td></tr>
    <tr><td>accepted_values(transfer_status)</td><td>stg_transfers</td><td>Unknown status codes from new source system versions</td></tr>
    <tr><td>expression_is_true(success_rate between 0 and 100)</td><td>mart_remittance</td><td>Broken division logic producing rates &gt; 100%</td></tr>
    <tr><td>unique(customer_id)</td><td>mart_customer_360</td><td>Fan-trap joins that inflate customer count</td></tr>
    <tr><td>freshness(fact_remittance_transfer)</td><td>source</td><td>Pipeline failure — data not loaded in 48h</td></tr>
  </table>
</div>

<!-- ══ CH 5 ══ -->
<div class="chapter">
  <div class="ch-header gold">
    <div class="ch-num">Chapter 05</div>
    <div class="ch-title">Gold Layer — Analytical Marts</div>
    <div class="ch-subtitle">Business-ready tables optimised for Power BI, direct SQL queries, and Snowpark ML feature extraction</div>
  </div>

  <h2>5.1 mart_remittance</h2>
  <p>The core remittance mart has one row per <strong>business × corridor × month × channel × payment method</strong>. It pre-computes every KPI a remittance executive needs:</p>
  <table>
    <tr><th>Metric Group</th><th>Key Fields</th></tr>
    <tr><td>Funnel</td><td>initiated_count, completed_count, failed_count, success_rate_pct</td></tr>
    <tr><td>Revenue</td><td>total_net_revenue_zar, avg_revenue_per_transfer_zar, fx_margin / fee split</td></tr>
    <tr><td>FX</td><td>avg_fx_spread_pct, corridor-level margin analysis</td></tr>
    <tr><td>Speed</td><td>avg_completion_minutes, median_completion_minutes</td></tr>
    <tr><td>Risk</td><td>fraud_rate_bps (basis points of total volume)</td></tr>
  </table>

  <h2>5.2 mart_customer_360</h2>
  <p>One row per current customer (SCD2 <code>IS_CURRENT = TRUE</code>) combining transfer behaviour, wallet activity, card spending, USD savings, and loan data into a single analytical record. Two derived scores are computed entirely in Snowflake SQL:</p>
  <ul style="margin-left:22px;line-height:2.2">
    <li><strong>LTV Score</strong> — weighted composite of lifetime revenue, card spend, transfer count, wallet balance, and USD savings</li>
    <li><strong>Engagement Score (0–100)</strong> — recency × frequency × KYC completion × wallet activity</li>
  </ul>

  <h2>5.3 Snowflake Architecture Diagram</h2>
  {SNOWFLAKE_ARCH_SVG}

  <h2>5.4 Power BI Connection</h2>
  <p>Power BI connects to the <code>GOLD</code> schema using the <code>AFRIMONEY_VIEWER</code> role and <code>AFRIMONEY_ANALYTICS_WH</code> (SMALL, auto-suspend 300s). The DirectQuery mode is used for the mart tables — Snowflake handles all aggregation pushdown, so Power BI visuals remain fast even against 5M-row fact tables in the underlying Gold.</p>

  <div class="box snow">
    <strong>DirectQuery tip:</strong> Enable <em>Query folding</em> in Power Query and use <em>aggregation tables</em> for the most common visual types (monthly trend, corridor bar chart). This reduces ANALYTICS_WH credit consumption by 60–80% compared to importing all mart rows.
  </div>
</div>

<!-- ══ CH 6 ══ -->
<div class="chapter">
  <div class="ch-header purple">
    <div class="ch-num">Chapter 06</div>
    <div class="ch-title">Snowpark ML Pipeline</div>
    <div class="ch-subtitle">Training, registering, and deploying 3 ML models — entirely inside Snowflake, no data egress</div>
  </div>

  <h2>6.1 Why Snowpark ML?</h2>
  <p>Traditional ML pipelines extract data from the warehouse, ship it to a Python server, train the model, and push predictions back. This creates <strong>data egress costs, PII exposure risk, and pipeline complexity</strong>.</p>
  <p>Snowpark ML runs Python code <em>inside Snowflake's compute</em>. The data never leaves. The feature tables, training jobs, model registry, and prediction tables are all Snowflake objects — version controlled, governed, and accessible to the same RBAC roles as your SQL queries.</p>

  <div class="kpi-row">
    <div class="kpi-card snow-card"><div class="kpi-val">0 bytes</div><div class="kpi-lbl">Data egress to external ML platform</div></div>
    <div class="kpi-card gold-card"><div class="kpi-val">3</div><div class="kpi-lbl">Models in Snowflake Model Registry</div></div>
    <div class="kpi-card"><div class="kpi-val">42ms</div><div class="kpi-lbl">Fraud score API latency p99</div></div>
  </div>

  <h2>6.2 Feature Store</h2>
  <p>Before training any model, features are materialised into <code>AFRIMONEY_ML_DB.FEATURE_STORE</code> tables. This serves two purposes:</p>
  <ol style="margin-left:22px;line-height:2.2">
    <li><strong>Reproducibility</strong> — the exact feature set used to train a model version is saved as a snapshot in Snowflake time travel</li>
    <li><strong>Reuse</strong> — multiple models share the same feature tables, avoiding duplicated computation</li>
  </ol>

  <div class="code"><span class="cm">-- Snowpark Python: feature engineering pushed down to Snowflake</span>
<span class="fn">features</span> = df.select(
    F.col(<span class="str">"TRANSFER_ID"</span>),
    F.<span class="fn">log</span>(F.<span class="fn">greatest</span>(F.col(<span class="str">"SEND_AMOUNT_ZAR"</span>), F.lit(<span class="val">1</span>))).alias(<span class="str">"SEND_AMOUNT_LOG"</span>),
    F.col(<span class="str">"FX_SPREAD_PCT"</span>),
    F.<span class="fn">hour</span>(F.col(<span class="str">"CREATED_DATETIME"</span>)).alias(<span class="str">"HOUR_OF_DAY"</span>),
    F.<span class="fn">hash</span>(F.col(<span class="str">"CORRIDOR_CODE"</span>)).alias(<span class="str">"CORRIDOR_HASH"</span>),  <span class="cm"># encode categoricals</span>
    F.col(<span class="str">"IS_SUSPECTED_FRAUD"</span>).cast(IntegerType()).alias(<span class="str">"LABEL_FRAUD"</span>),
)
<span class="cm"># This executes as a single SQL query in Snowflake — no Python loop</span>
<span class="fn">features</span>.write.mode(<span class="str">"overwrite"</span>).save_as_table(<span class="str">"FEATURE_STORE.FRAUD_FEATURES"</span>)</div>

  <h2>6.3 Model Results</h2>
  {SNOWFLAKE_ML_HTML}

  <h2>6.4 The Three Models Explained</h2>

  <div class="model-card active">
    <h4>Model 1 — Fraud Detection (GradientBoostingClassifier)</h4>
    <p><strong>Business question:</strong> Is this transfer likely to be fraudulent at the moment of initiation?</p>
    <p><strong>How it works:</strong> A GBM model trained on 5M transfer records learns that certain combinations of send amount, time of day, corridor, and payment method are statistically associated with fraud. The model outputs a probability score (0–1). Transfers above 0.40 trigger a compliance hold before processing.</p>
    <p><strong>Top features:</strong> send_amount_log, corridor_hash, payment_attempts, hour_of_day, fx_spread_pct</p>
    <div class="metric-chips">
      <span class="chip green-chip">AUC-ROC: 0.91</span>
      <span class="chip">Threshold: 0.40</span>
      <span class="chip">Real-time inference</span>
      <span class="chip">Deployed as UDF</span>
    </div>
  </div>

  <div class="model-card">
    <h4>Model 2 — Customer Churn (RandomForestClassifier)</h4>
    <p><strong>Business question:</strong> Which customers are at risk of not sending another transfer in the next 90 days?</p>
    <p><strong>How it works:</strong> An RF model trained on the mart_customer_360 feature set. Recency (days since last transfer) and engagement score are the strongest predictors. Churned customers are scored weekly and segmented into 5 risk bands for CRM campaigns.</p>
    <div class="metric-chips">
      <span class="chip green-chip">AUC-ROC: 0.86</span>
      <span class="chip">Churn Rate: ~45%</span>
      <span class="chip">Weekly batch</span>
      <span class="chip">5 risk segments</span>
    </div>
  </div>

  <div class="model-card">
    <h4>Model 3 — Credit Risk PD (GradientBoostingClassifier) — Mukuru only</h4>
    <p><strong>Business question:</strong> What is the probability this loan applicant will default?</p>
    <p><strong>How it works:</strong> Trained on 200K Mukuru loan applications with repayment history. The model calculates a PD (Probability of Default) used for origination decisions and IFRS 9 Expected Credit Loss (ECL) calculations. SHAP explainability is enabled — every declined application gets a human-readable reason for NCA compliance.</p>
    <div class="metric-chips">
      <span class="chip green-chip">AUC-ROC: 0.78</span>
      <span class="chip">Default Rate: ~11%</span>
      <span class="chip">SHAP explanations</span>
      <span class="chip green-chip">NCA compliant</span>
    </div>
  </div>

  <h2>6.5 Fraud Score UDF — Deployed in Snowflake</h2>
  <div class="code"><span class="cm">-- After Snowpark training, the model is deployed as a Snowflake UDF</span>
<span class="cm">-- Any SQL query or Power BI report can call it:</span>

<span class="kw">SELECT</span>
    transfer_id,
    send_amount_zar,
    AFRIMONEY_DB.UTILS.GET_FRAUD_SCORE(
        send_amount_zar,
        fx_spread_pct,
        payment_attempts,
        HOUR(created_datetime),
        HASH(channel)
    ) <span class="kw">AS</span> fraud_score
<span class="kw">FROM</span> AFRIMONEY_DB.BRONZE.FACT_REMITTANCE_TRANSFER
<span class="kw">WHERE</span> created_datetime >= DATEADD(<span class="str">'hour'</span>, <span class="val">-1</span>, CURRENT_TIMESTAMP())
<span class="kw">ORDER BY</span> fraud_score <span class="kw">DESC</span>;</div>
</div>

<!-- ══ CH 7 ══ -->
<div class="chapter">
  <div class="ch-header sky">
    <div class="ch-num">Chapter 07</div>
    <div class="ch-title">KPI Framework</div>
    <div class="ch-subtitle">The complete metric library — from executive scorecards to risk basis points</div>
  </div>

  <h2>7.1 Executive KPIs</h2>
  <table>
    <tr><th>KPI</th><th>Snowflake SQL Formula</th><th>Owner</th></tr>
    <tr><td>Total Transfer Volume</td><td>SUM(send_amount_zar) WHERE is_completed</td><td>CEO / CFO</td></tr>
    <tr><td>Net Revenue</td><td>SUM(net_revenue_zar) WHERE is_completed</td><td>CFO</td></tr>
    <tr><td>Monthly Active Senders</td><td>COUNT(DISTINCT sender_customer_id) in month</td><td>CEO / CMO</td></tr>
    <tr><td>Transfer Success Rate</td><td>SUM(is_completed) / COUNT(*) * 100</td><td>COO</td></tr>
    <tr><td>Revenue per Active Customer</td><td>SUM(net_revenue) / COUNT(DISTINCT customer_id)</td><td>CFO / CMO</td></tr>
    <tr><td>Repeat Sender Rate</td><td>Customers with completed_transfers ≥ 2 / all active</td><td>CMO</td></tr>
    <tr><td>Digital Adoption Rate</td><td>Digital channel transfers / all transfers * 100</td><td>Product</td></tr>
  </table>

  <h2>7.2 Risk KPIs — Computed in mart_risk_compliance</h2>
  <table>
    <tr><th>KPI</th><th>Formula</th><th>Target</th><th>Alert</th></tr>
    <tr><td>Fraud Rate</td><td>fraud_flagged / total_transfers * 10,000</td><td>&lt; 5 bps</td><td>&gt; 10 bps</td></tr>
    <tr><td>KYC Completion Rate</td><td>LEVEL_2+ customers / all registered</td><td>&gt; 90%</td><td>&lt; 80%</td></tr>
    <tr><td>Transfer Success Rate</td><td>completed / initiated * 100</td><td>&gt; 80%</td><td>&lt; 70%</td></tr>
    <tr><td>Cancellation Rate</td><td>cancelled / initiated * 100</td><td>&lt; 8%</td><td>&gt; 15%</td></tr>
  </table>

  <div class="box warn">
    <strong>Vanity metrics to avoid:</strong> "17 million customers served" means nothing without paired context. Always report: monthly active customers, transacting rate (% who sent in last 30 days), and retention rate. A large registered base with 5% monthly active rate is a crisis, not a success story.
  </div>
</div>

<!-- ══ CH 8 ══ -->
<div class="chapter">
  <div class="ch-header navy">
    <div class="ch-num">Chapter 08</div>
    <div class="ch-title">Data Governance, PII &amp; Compliance</div>
    <div class="ch-subtitle">POPIA, tokenisation strategy, dbt data lineage, and Snowflake access controls</div>
  </div>

  <h2>8.1 PII Classification in Snowflake</h2>
  <table>
    <tr><th>Field</th><th>Bronze</th><th>Silver / Gold</th><th>Power BI</th></tr>
    <tr><td>Full name</td><td>Plaintext</td><td>SHA-256 hash</td><td>Never visible</td></tr>
    <tr><td>ID / Passport</td><td>AES-256 encrypted</td><td>Tokenised reference</td><td>Never visible</td></tr>
    <tr><td>Mobile number</td><td>Plaintext</td><td>Reversible vault token</td><td>Last 4 digits only</td></tr>
    <tr><td>Bank account</td><td>AES-256 encrypted</td><td>Masked (****1234)</td><td>Never visible</td></tr>
    <tr><td>Transaction amounts</td><td>Plaintext</td><td>Plaintext</td><td>Visible (required)</td></tr>
    <tr><td>Transfer reference</td><td>Plaintext</td><td>Plaintext</td><td>Visible</td></tr>
  </table>

  <div class="box danger">
    <strong>POPIA obligation:</strong> South Africa's Protection of Personal Information Act requires that any cross-border transfer of personal data (e.g., to a cloud region outside SA) has a documented lawful basis or an adequacy assessment. Snowflake's South Africa region (hosted on AWS Cape Town) keeps data in-country by default — verify your Snowflake account region before go-live.
  </div>

  <h2>8.2 Snowflake Dynamic Data Masking</h2>
  <div class="code"><span class="cm">-- Masking policy: ANALYST role sees masked mobile numbers</span>
<span class="kw">CREATE OR REPLACE</span> MASKING POLICY mobile_mask <span class="kw">AS</span> (val <span class="kw">VARCHAR</span>) <span class="kw">RETURNS</span> <span class="kw">VARCHAR</span> <span class="kw">->
</span>    <span class="kw">CASE</span>
        <span class="kw">WHEN</span> CURRENT_ROLE() <span class="kw">IN</span> (<span class="str">'AFRIMONEY_ENG'</span>, <span class="str">'AFRIMONEY_ADMIN'</span>)
            <span class="kw">THEN</span> val
        <span class="kw">ELSE</span> <span class="fn">REGEXP_REPLACE</span>(val, <span class="str">'.(?=.{4})'</span>, <span class="str">'*'</span>)
    <span class="kw">END</span>;

<span class="kw">ALTER TABLE</span> BRONZE.DIM_CUSTOMER
    <span class="kw">MODIFY COLUMN</span> MOBILE_NUMBER_TOKEN
    <span class="kw">SET</span> MASKING POLICY mobile_mask;</div>
</div>

<!-- ══ CH 9 ══ -->
<div class="chapter">
  <div class="ch-header green">
    <div class="ch-num">Chapter 09</div>
    <div class="ch-title">Implementation Roadmap</div>
    <div class="ch-subtitle">A three-phase plan from Snowflake setup to production ML in 12 months</div>
  </div>

  <h2>9.1 Phase 1 — Foundation (Months 1–3)</h2>
  <table>
    <tr><th>Month</th><th>Task</th><th>Owner</th><th>Tool</th></tr>
    <tr><td>1</td><td>Snowflake account setup: warehouses, RBAC, stage</td><td>Platform Engineer</td><td>Snowflake SQL</td></tr>
    <tr><td>1</td><td>Bronze DDL: all 20 table definitions deployed</td><td>Data Engineer</td><td>Snowflake SQL</td></tr>
    <tr><td>1</td><td>PII masking policies applied to Bronze</td><td>Security Eng</td><td>Snowflake SQL</td></tr>
    <tr><td>2</td><td>Initial COPY INTO loads: all tables verified</td><td>Data Engineer</td><td>SnowSQL / ADF</td></tr>
    <tr><td>2</td><td>dbt project: staging models passing 28 tests</td><td>Analytics Eng</td><td>dbt + Snowflake</td></tr>
    <tr><td>3</td><td>Gold marts live: mart_remittance + mart_customer_360</td><td>Analytics Eng</td><td>dbt + Snowflake</td></tr>
    <tr><td>3</td><td>Power BI connected: executive dashboard live</td><td>BI Developer</td><td>Power BI + Snowflake</td></tr>
  </table>

  <h2>9.2 Phase 2 — Analytics (Months 4–6)</h2>
  <table>
    <tr><th>Month</th><th>Task</th><th>Owner</th><th>Tool</th></tr>
    <tr><td>4</td><td>mart_fx_profitability + mart_wallet_card deployed</td><td>Analytics Eng</td><td>dbt</td></tr>
    <tr><td>5</td><td>mart_loans_mukuru + mart_insurance_mukuru live</td><td>Analytics Eng</td><td>dbt</td></tr>
    <tr><td>5</td><td>mart_risk_compliance: fraud dashboard live</td><td>Risk / Analytics</td><td>dbt + Power BI</td></tr>
    <tr><td>6</td><td>Snowflake Streamlit app: internal data explorer</td><td>Data Engineer</td><td>Streamlit in Snowflake</td></tr>
  </table>

  <h2>9.3 Phase 3 — ML &amp; Real-Time (Months 7–12)</h2>
  <table>
    <tr><th>Month</th><th>Task</th><th>Owner</th><th>Tool</th></tr>
    <tr><td>7</td><td>Snowpark Feature Store: fraud + churn features</td><td>Data Scientist</td><td>Snowpark Python</td></tr>
    <tr><td>8</td><td>Fraud model v1: trained, registered, UDF deployed</td><td>Data Scientist</td><td>Snowpark ML</td></tr>
    <tr><td>9</td><td>Fraud UDF integrated into transfer processing API</td><td>Backend Eng</td><td>Snowflake REST API</td></tr>
    <tr><td>10</td><td>Churn model: weekly batch scores in Snowflake, CRM sync</td><td>Data Scientist</td><td>Snowpark ML + CRM</td></tr>
    <tr><td>11</td><td>Credit PD model: live at loan application; SHAP deployed</td><td>Data Scientist / Risk</td><td>Snowpark ML</td></tr>
    <tr><td>12</td><td>Daily ML refresh stored procedure scheduled via Snowflake Task</td><td>MLOps</td><td>Snowflake Tasks</td></tr>
  </table>

  <div class="box info">
    <strong>Final state after 12 months:</strong> The AfriMoney Intelligence Platform will have 40M+ rows of live operational data in Snowflake Bronze, 14 dbt models transforming it daily, 3 Snowpark ML models scoring in real-time and batch, and a Power BI dashboard that gives the executive team a live view of both brands in a single pane of glass — with zero data leaving Snowflake.
  </div>
</div>

<div class="footer">
  <p><strong>AfriMoney Intelligence Platform</strong> — Snowflake + dbt + Snowpark ML Technical Reference</p>
  <p style="margin-top:8px">By: <strong>Anthony Apollis</strong> &nbsp;|&nbsp; {TODAY} &nbsp;|&nbsp; Portfolio Project — Data Engineering</p>
  <p style="margin-top:8px">Mukuru + Mama Money Unified Model &nbsp;|&nbsp; 40M+ Rows &nbsp;|&nbsp; Bronze→Silver→Gold &nbsp;|&nbsp; 3 ML Models</p>
  <p style="margin-top:14px;font-size:10px;color:rgba(255,255,255,0.45)">
    Synthetic data only. No real customer data or proprietary business information used. Mukuru and Mama Money are referenced for educational and portfolio demonstration purposes only.
  </p>
</div>

</body>
</html>"""

out = EBOOK / "AfriMoney_Intelligence_Platform_Ebook.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"[SAVED] {out}")
print(f"  Size: {out.stat().st_size/1024:.0f} KB")
print("  Chapters: 9")
print("  Includes: Snowflake UI mockups, dbt DAG diagram, architecture SVG, ML model registry")
