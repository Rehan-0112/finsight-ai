import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import textwrap
import json
import re
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSight AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Google Fonts (separate call — never mix with <style>) ─────────────────────
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
    '&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">',
    unsafe_allow_html=True
)

# ── CSS (own call, nothing else inside) ───────────────────────────────────────
st.markdown("""<style>
*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{
    background:#07090f;
    font-family:'Inter',sans-serif;
    color:#e8eef8;
}
.stApp::before{
    content:'';position:fixed;inset:0;
    background-image:
        linear-gradient(rgba(14,165,233,.03) 1px,transparent 1px),
        linear-gradient(90deg,rgba(14,165,233,.03) 1px,transparent 1px);
    background-size:48px 48px;
    pointer-events:none;z-index:0;
}
.block-container{
    padding:1.2rem 1.5rem 3rem;
    max-width:100%;
    position:relative;z-index:1;
}
#MainMenu,footer{visibility:hidden;}
header{background:transparent !important;}

/* Sidebar */
[data-testid="stSidebar"]{background:#0a0d18 !important;border-right:1px solid #1a2744;}
[data-testid="stSidebar"] .block-container{padding:0;}
.sb-logo{
    display:flex;align-items:center;gap:.6rem;
    padding:1.2rem 1rem .9rem;border-bottom:1px solid #1a2744;
    margin-bottom:.4rem;
}
.sb-mark{
    width:30px;height:30px;
    background:linear-gradient(135deg,#0ea5e9,#2563eb);
    border-radius:7px;display:flex;align-items:center;
    justify-content:center;flex-shrink:0;
}
.sb-name{font-size:.9rem;font-weight:700;color:#e8eef8;line-height:1.1;}
.sb-tag{font-size:.58rem;color:#7b92b8;}
.sb-sec{
    font-size:.58rem;font-weight:600;color:#3d5270;
    text-transform:uppercase;letter-spacing:.1em;
    padding:.8rem 1rem .25rem;
}
.sb-item{
    display:flex;align-items:center;gap:.55rem;
    padding:.4rem 1rem;font-size:.79rem;color:#7b92b8;
    cursor:pointer;transition:all .15s;
}
.sb-item.active{
    color:#0ea5e9;border-right:2px solid #0ea5e9;
    background:rgba(14,165,233,.08);
}
.sb-div{height:1px;background:#1a2744;margin:.4rem 1rem;}
.sb-tick{
    display:flex;align-items:center;justify-content:space-between;
    padding:.33rem 1rem;
}
.sb-sym{font-size:.75rem;font-family:'DM Mono',monospace;color:#c8d8f0;font-weight:500;}
.sb-chg{font-size:.7rem;font-family:'DM Mono',monospace;}
.up{color:#10b981;}.dn{color:#ef4444;}

/* Controls */
.stSelectbox>div>div{
    background:#0d1424 !important;border:1px solid #1a2744 !important;
    border-radius:6px !important;color:#e8eef8 !important;
    font-family:'Inter',sans-serif !important;font-size:.87rem !important;
}
.stButton>button{
    background:#0d1424 !important;color:#7b92b8 !important;
    font-weight:500 !important;font-size:.79rem !important;
    border:1px solid transparent !important;border-radius:6px !important;
    padding:.55rem 1rem !important;text-align:center !important;
    box-shadow:none !important;
}
.stButton>button:hover{
    background:rgba(14,165,233,.08) !important;
    color:#0ea5e9 !important;
    border-color:transparent !important;
}
/* Primary Analyse button */
.stButton>button[kind="primary"]{
    background:#0ea5e9 !important;color:#07090f !important;
    border:1px solid #0ea5e9 !important;border-radius:6px !important;
    font-weight:600 !important;text-align:center !important;
}
.stButton>button[kind="primary"]:hover{
    background:#38bdf8 !important;color:#07090f !important;
}
/* Sidebar navigation buttons */
[data-testid="stSidebar"] .stButton>button{
    width:100% !important;
    justify-content:flex-start !important;
    min-height:38px !important;
    text-align:left !important;
    border-radius:0 !important;
    font-size:.79rem !important;
}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{
    background:rgba(14,165,233,.08) !important;
    color:#0ea5e9 !important;
    border-top:1px solid transparent !important;
    border-bottom:1px solid transparent !important;
    border-left:0 !important;
    border-right:2px solid #0ea5e9 !important;
    text-align:left !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
    gap:0;background:#0d1424;
    border:1px solid #1a2744;border-radius:8px;
    padding:3px;margin-bottom:1rem;width:fit-content;
}
.stTabs [data-baseweb="tab"]{
    background:transparent;color:#7b92b8;
    border-radius:6px;padding:.35rem 1.1rem;
    font-size:.8rem;font-weight:500;
}
.stTabs [aria-selected="true"]{
    background:#1a2744 !important;color:#e8eef8 !important;
}

/* Company header */
.co-hdr{
    background:#0d1424;border:1px solid #1a2744;
    border-radius:10px;padding:.9rem 1.4rem;
    margin-bottom:1rem;
    display:flex;align-items:center;gap:1.75rem;flex-wrap:wrap;
}
.co-name{font-size:1.35rem;font-weight:700;color:#e8eef8;letter-spacing:-.3px;}
.co-sym{font-family:'DM Mono',monospace;font-size:.68rem;color:#7b92b8;margin-top:.1rem;}
.co-badge{
    padding:.14rem .5rem;border-radius:4px;font-size:.64rem;font-weight:600;
    font-family:'DM Mono',monospace;
    background:rgba(14,165,233,.12);color:#0ea5e9;
    border:1px solid rgba(14,165,233,.25);
}
.co-price{font-size:1.5rem;font-weight:500;font-family:'DM Mono',monospace;color:#e8eef8;}
.co-chg{font-size:.78rem;font-family:'DM Mono',monospace;}
.co-divr{width:1px;height:34px;background:#1a2744;flex-shrink:0;}
.co-lbl{font-size:.6rem;color:#7b92b8;text-transform:uppercase;letter-spacing:.07em;margin-bottom:.18rem;}

/* Metric cards */
.mc{
    background:#0d1424;border:1px solid #1a2744;
    border-radius:8px;padding:.78rem .9rem .62rem;
}
.mc-lbl{font-size:.58rem;font-weight:600;color:#7b92b8;text-transform:uppercase;letter-spacing:.09em;margin-bottom:.28rem;}
.mc-val{font-size:1.28rem;font-weight:600;font-family:'DM Mono',monospace;color:#e8eef8;line-height:1.1;}
.mc-sub{font-size:.68rem;font-family:'DM Mono',monospace;margin-top:.16rem;}
.mc-sp{margin-top:.35rem;line-height:0;}

/* Section label */
.sec{
    font-size:.58rem;font-weight:600;color:#7b92b8;
    text-transform:uppercase;letter-spacing:.12em;
    margin:1rem 0 .55rem;
    display:flex;align-items:center;gap:.5rem;
}
.sec::after{content:'';flex:1;height:1px;background:#1a2744;}

/* Pills */
.pill{
    display:inline-flex;align-items:center;gap:.26rem;
    padding:.18rem .6rem;border-radius:4px;
    font-size:.72rem;font-weight:600;font-family:'DM Mono',monospace;
}
.pill-up{background:rgba(16,185,129,.12);color:#10b981;border:1px solid rgba(16,185,129,.25);}
.pill-dn{background:rgba(239,68,68,.12);color:#ef4444;border:1px solid rgba(239,68,68,.25);}
.pill-ok{background:rgba(16,185,129,.12);color:#10b981;border:1px solid rgba(16,185,129,.25);}
.pill-warn{background:rgba(245,158,11,.12);color:#f59e0b;border:1px solid rgba(245,158,11,.25);}

/* Info panels (HTML-only, no chart inside) */
.pnl{background:#0d1424;border:1px solid #1a2744;border-radius:8px;padding:.95rem 1.05rem;}
.pnl-title{
    font-size:.62rem;font-weight:600;color:#7b92b8;
    text-transform:uppercase;letter-spacing:.09em;
    margin-bottom:.72rem;padding-bottom:.4rem;border-bottom:1px solid #1a2744;
}
.prow{
    display:flex;justify-content:space-between;align-items:center;
    padding:.34rem 0;border-bottom:1px solid #111827;font-size:.76rem;
}
.prow:last-child{border-bottom:none;}
.pk{color:#7b92b8;} .pv{font-family:'DM Mono',monospace;color:#e8eef8;font-weight:500;}

/* SHAP rows */
.sf-row{
    display:flex;align-items:center;justify-content:space-between;
    padding:.38rem 0;border-bottom:1px solid #111827;
}
.sf-row:last-child{border-bottom:none;}
.sf-name{display:flex;align-items:center;gap:.42rem;font-size:.79rem;color:#c8d8f0;}
.sf-icon{
    width:16px;height:16px;border-radius:3px;
    display:flex;align-items:center;justify-content:center;
    flex-shrink:0;font-size:.56rem;font-weight:700;
}
.sf-pos{background:rgba(16,185,129,.15);color:#10b981;}
.sf-neg{background:rgba(239,68,68,.15);color:#ef4444;}
.sf-val{font-size:.74rem;font-family:'DM Mono',monospace;font-weight:600;}
.sf-bar{height:2px;border-radius:2px;margin-top:.1rem;opacity:.4;}

/* SHAP explanation panel */
.shap-panel{padding-top:.05rem;}
.shap-title{
    font-size:1.05rem;font-weight:700;color:#e8eef8;
    line-height:1.15;margin:0 0 .85rem;letter-spacing:-.3px;
}
.shap-row{padding:.42rem 0 .5rem;border-bottom:1px solid #111827;}
.shap-row:last-child{border-bottom:none;}
.shap-top{display:flex;align-items:center;justify-content:space-between;gap:.5rem;}
.shap-feature{font-size:.79rem;color:#c8d8f0;font-weight:500;}
.shap-value{font-size:.74rem;font-family:'DM Mono',monospace;font-weight:600;color:#e8eef8;flex-shrink:0;}
.shap-impact{font-size:.68rem;color:#7b92b8;margin:.25rem 0 .28rem;}
.shap-track{width:100%;height:4px;background:#1a1f2d;border-radius:4px;overflow:hidden;}
.shap-fill{height:100%;border-radius:4px;opacity:.9;}

/* Competitor table */
.ct{width:100%;border-collapse:collapse;font-size:.76rem;}
.ct th{
    font-size:.58rem;font-weight:600;color:#3d5270;text-transform:uppercase;
    letter-spacing:.07em;padding:.38rem .5rem;text-align:right;
    border-bottom:1px solid #1a2744;
}
.ct th:first-child{text-align:left;}
.ct td{
    padding:.38rem .5rem;text-align:right;border-bottom:1px solid #111827;
    font-family:'DM Mono',monospace;color:#b8c8e0;font-size:.74rem;
}
.ct td:first-child{text-align:left;color:#e8eef8;font-family:'Inter',sans-serif;font-weight:500;font-size:.76rem;}
.ct tr.hl td{background:rgba(14,165,233,.06);}
.ct tr:last-child td{border-bottom:none;}

/* LLM analysis */
.llm-box{background:#0d1424;border:1px solid #1a2744;border-radius:8px;padding:1.35rem 1.55rem;}
.llm-h1{
    font-size:.9rem;font-weight:700;color:#e8eef8;text-transform:uppercase;
    letter-spacing:.05em;border-bottom:1px solid #1a2744;
    padding-bottom:.26rem;margin:1rem 0 .48rem;
}
.llm-h1:first-child{margin-top:0;}
.llm-h2{font-size:.84rem;font-weight:700;color:#e8eef8;margin:.85rem 0 .36rem;}
.llm-h3{font-size:.8rem;font-weight:600;color:#c8d8f0;margin:.7rem 0 .3rem;}
.llm-p{font-size:.82rem;line-height:1.8;color:#b8c8e0;margin:0 0 .6rem;}
.llm-p:last-child{margin-bottom:0;}
.llm-p strong{color:#e8eef8;font-weight:600;}

.llm-table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

.llm-table th {
    text-align: left;
    padding: .7rem .8rem;
    border-bottom: 1px solid #273653;
    color: #e8eef8;
    font-weight: 600;
}

.llm-table td {
    padding: .7rem .8rem;
    border-bottom: 1px solid #1a2744;
    color: #b8c7dc;
    vertical-align: top;
}

.llm-bullet {
    margin: .45rem 0;
    color: #b8c7dc;
    line-height: 1.6;
}

.llm-number {
    margin: .45rem 0;
    color: #b8c7dc;
    line-height: 1.6;
}

.llm-number span {
    color: #0ea5e9;
    font-family: 'DM Mono', monospace;
}

.llm-hr {
    border: none;
    border-top: 1px solid #1a2744;
    margin: 1rem 0;
}

.llm-p {
    margin: .55rem 0;
    line-height: 1.7;
}

.llm-h1 {
    font-size: 1.05rem;
    font-weight: 700;
    color: #e8eef8;
    margin: .8rem 0;
}

.llm-h2 {
    font-size: .95rem;
    font-weight: 700;
    color: #e8eef8;
    margin: 1rem 0 .6rem;
}

.llm-h3 {
    font-size: .85rem;
    font-weight: 700;
    color: #c8d8f0;
    margin: .8rem 0 .5rem;
}

.llm-table code,
.llm-p code {
    font-family: 'DM Mono', monospace;
    color: #0ea5e9;
}

/* Papers */
.pr{
    display:flex;gap:.75rem;padding:.72rem .9rem;background:#0d1424;
    border-left:1px solid #1a2744;border-right:1px solid #1a2744;
    border-bottom:1px solid #111827;
}
.pr-first{border-top:1px solid #1a2744;border-radius:8px 8px 0 0;}
.pr-last{border-radius:0 0 8px 8px;border-bottom:1px solid #1a2744;}
.pr-only{border:1px solid #1a2744;border-radius:8px;}
.pr-idx{font-size:.64rem;font-family:'DM Mono',monospace;color:#0ea5e9;min-width:1.3rem;padding-top:.05rem;}
.pr-title{font-size:.8rem;font-weight:500;color:#c8d8f0;line-height:1.4;margin-bottom:.26rem;}
.pr-meta{display:flex;gap:.75rem;flex-wrap:wrap;}
.pr-tag{font-size:.64rem;font-family:'DM Mono',monospace;color:#7b92b8;}
.pr-link{font-size:.64rem;font-family:'DM Mono',monospace;color:#0ea5e9;text-decoration:none;}

/* Chat */
.stChatMessage{background:#0d1424 !important;border:1px solid #1a2744 !important;border-radius:8px !important;}
.stChatInputContainer{background:#0d1424 !important;border:1px solid #1a2744 !important;border-radius:8px !important;}
.stChatInputContainer textarea{color:#e8eef8 !important;background:transparent !important;}


/* ── Dashboard polish ─────────────────────────────────────────────────────── */
.stPlotlyChart {
    background:#0d1424 !important;
    border:1px solid #17243c !important;
    border-radius:10px !important;
    overflow:hidden !important;
    box-shadow:0 8px 24px rgba(0,0,0,.10);
}
[data-testid="stVerticalBlock"] > div:has(> .stPlotlyChart) { min-width:0; }
.dashboard-card{
    background:#0d1424;
    border:1px solid #17243c;
    border-radius:10px;
    padding:1rem 1.05rem;
    box-shadow:0 8px 24px rgba(0,0,0,.10);
}
.dashboard-card-title{
    display:flex;align-items:center;justify-content:space-between;
    font-size:.62rem;font-weight:600;color:#7b92b8;
    text-transform:uppercase;letter-spacing:.1em;
    padding-bottom:.65rem;margin-bottom:.7rem;
    border-bottom:1px solid #1a2744;
}
.dashboard-card-sub{font-size:.66rem;color:#3d5270;font-family:'DM Mono',monospace;}
.dashboard-gap{height:.25rem;}
.section-tight{margin-top:.65rem !important;margin-bottom:.5rem !important;}
.metric-strip{margin-top:.15rem;}

/* ── Page layout refinement ─────────────────────────────────────────────── */
.main .block-container{padding-top:1rem !important;}
.stPlotlyChart{margin:0 !important;}
div[data-testid="stHorizontalBlock"]{gap:1rem !important;align-items:stretch !important;}
div[data-testid="column"]{min-width:0 !important;}
.nav-spacer{height:.2rem;}
.page-intro{margin-bottom:.9rem;}
.page-card{background:#0d1424;border:1px solid #17243c;border-radius:10px;padding:1rem 1.05rem;box-shadow:0 8px 24px rgba(0,0,0,.10);height:100%;}
.page-card.compact{padding:.85rem .95rem;}
.page-card-title{display:flex;align-items:center;justify-content:space-between;font-size:.62rem;font-weight:600;color:#7b92b8;text-transform:uppercase;letter-spacing:.1em;padding-bottom:.58rem;margin-bottom:.65rem;border-bottom:1px solid #1a2744;}
.page-card-sub{font-size:.62rem;color:#3d5270;font-family:'DM Mono',monospace;}
.page-kpi{background:#0d1424;border:1px solid #17243c;border-radius:9px;padding:.8rem .9rem;min-height:82px;}
.page-kpi .mc-lbl{margin-bottom:.35rem;}
.page-kpi .mc-val{font-size:1.15rem;}
.page-kpi .mc-sub{margin-top:.25rem;}
.page-grid-gap{margin-top:1rem;}
.chart-card{background:#0d1424;border:1px solid #17243c;border-radius:10px;padding:.55rem .65rem .15rem;box-shadow:0 8px 24px rgba(0,0,0,.10);}
.chart-card .chart-head{padding:.2rem .35rem .5rem;}
.chart-head{display:flex;justify-content:space-between;align-items:center;color:#7b92b8;font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;}
.chart-head span:last-child{font-family:'DM Mono',monospace;color:#3d5270;font-size:.6rem;}
.shap-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.7rem;}
.shap-mini{background:#0b1220;border:1px solid #17243c;border-radius:8px;padding:.65rem .7rem;min-width:0;}
.shap-mini .shap-feature{font-size:.72rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.shap-mini .shap-impact{font-size:.62rem;margin:.18rem 0 .3rem;}
.health-layout{display:grid;grid-template-columns:1.05fr .95fr;gap:.75rem;align-items:center;}
.health-chart-wrap{height:100%;min-height:170px;padding:.35rem .45rem 0;}
.health-details{min-height:170px;box-sizing:border-box;}
.financial-health-card{background:#0d1424;border:1px solid #17243c;border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.10);overflow:hidden;}
.financial-health-head{display:flex;justify-content:space-between;align-items:center;padding:.78rem .95rem .68rem;border-bottom:1px solid #1a2744;color:#7b92b8;font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;}
.financial-health-head span:last-child{color:#3d5270;font-family:'DM Mono',monospace;font-size:.58rem;}
.financial-health-body{display:grid;grid-template-columns:1.15fr .85fr;gap:.85rem;padding:.75rem .85rem .85rem;align-items:center;}
.financial-gauge{position:relative;height:155px;display:flex;align-items:flex-end;justify-content:center;overflow:hidden;}
.financial-gauge svg{width:100%;height:145px;display:block;}
.gauge-value{position:absolute;left:0;right:0;bottom:28px;text-align:center;color:#e8eef8;font:700 1.45rem 'DM Mono',monospace;}
.gauge-value span{font-size:.58rem;color:#3d5270;font-weight:600;}
.gauge-label{position:absolute;left:0;right:0;bottom:8px;text-align:center;font:600 .62rem 'DM Mono',monospace;}
.financial-health-details{min-width:0;}
.health-detail-heading{font-size:.6rem;color:#7b92b8;text-transform:uppercase;letter-spacing:.1em;font-weight:600;margin-bottom:.3rem;}
.health-detail-score{font:700 1.35rem 'DM Mono',monospace;line-height:1.1;}
.health-detail-score span{font-size:.62rem;color:#3d5270;}
.health-detail-status{font-size:.65rem;color:#7b92b8;margin:.25rem 0 .55rem;}
.health-stat-row{display:flex;justify-content:space-between;gap:.75rem;padding:.48rem 0;border-top:1px solid #18243a;font-size:.68rem;}
.health-stat-row span{color:#7b92b8;}
.health-stat-row strong{color:#d9e3f2;font-family:'DM Mono',monospace;font-weight:600;}
.risk-interpretation{min-height:135px;box-sizing:border-box;}
.risk-layout{display:grid;grid-template-columns:1.05fr .95fr;gap:1rem;}
@media(max-width:1100px){.shap-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.risk-layout,.health-layout{grid-template-columns:1fr;} .financial-health-body{grid-template-columns:1fr 1fr;}}
@media(max-width:800px){.shap-grid{grid-template-columns:1fr;} .financial-health-body{grid-template-columns:1fr;} .financial-gauge{height:145px;}}

/* ── Financial health / signal cards ───────────────────────────────────── */
.sec-title-row{display:flex;justify-content:space-between;align-items:center;color:#7b92b8;font-size:.62rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;margin:.1rem 0 .65rem;padding-bottom:.55rem;border-bottom:1px solid #1a2744;}
.sec-title-row span:last-child{color:#3d5270;font-family:'DM Mono',monospace;font-size:.58rem;}
.inner-card-title{display:flex;justify-content:space-between;align-items:center;color:#7b92b8;font-size:.61rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;padding-bottom:.5rem;margin-bottom:.25rem;border-bottom:1px solid #1a2744;}
.inner-card-title span:last-child{color:#3d5270;font-family:'DM Mono',monospace;font-size:.57rem;}
.health-detail-card{padding:.1rem 0 .15rem;}
.health-score{font:700 1.65rem 'DM Mono',monospace;color:#e8eef8;margin-top:.15rem;}
.health-score span{font-size:.68rem;color:#3d5270;font-weight:500;}
.health-label{font-size:.68rem;color:#7b92b8;margin:.1rem 0 .55rem;}
.health-row,.signal-row{display:flex;justify-content:space-between;align-items:center;padding:.58rem 0;border-top:1px solid #17243c;font-size:.7rem;color:#7b92b8;}
.health-row strong,.signal-row strong{font:600 .72rem 'DM Mono',monospace;color:#d8e2f2;}
/* Empty state */
.empty{
    text-align:center;padding:4.5rem 2rem;
    border:1px dashed #1a2744;border-radius:8px;margin-top:1rem;
}
.empty-t{font-size:.92rem;font-weight:600;color:#b8c8e0;margin-bottom:.32rem;}
.empty-s{font-size:.74rem;color:#7b92b8;}
.stat-g{display:flex;gap:2rem;justify-content:center;margin-top:1.8rem;flex-wrap:wrap;}
.stat-v{font-size:1.3rem;font-weight:700;font-family:'DM Mono',monospace;color:#0ea5e9;}
.stat-l{font-size:.6rem;color:#7b92b8;text-transform:uppercase;letter-spacing:.08em;}
</style>""", unsafe_allow_html=True)

# ── SVG Icons ─────────────────────────────────────────────────────────────────
I_LOGO = '<svg width="15" height="15" viewBox="0 0 20 20" fill="none"><path d="M3 14l4-4 3 3 4-6 3 3" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="17" cy="10" r="1.5" fill="#0ea5e9"/></svg>'
I_DASH = '<svg width="13" height="13" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="9" y="1" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="1" y="9" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.3"/></svg>'
I_FORE = '<svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M2 12l4-4 3 3 5-7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
I_ANOM = '<svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M8 2l6 11H2L8 2z" stroke="currentColor" stroke-width="1.3" fill="none"/><line x1="8" y1="7" x2="8" y2="10" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="12" r=".8" fill="currentColor"/></svg>'
I_AI   = '<svg width="13" height="13" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.3"/><path d="M5 8h6M8 5v6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>'
I_UP   = '<svg width="9" height="9" viewBox="0 0 10 10"><path d="M5 1L9 7H1Z" fill="#10b981"/></svg>'
I_DN   = '<svg width="9" height="9" viewBox="0 0 10 10"><path d="M5 9L1 3H9Z" fill="#ef4444"/></svg>'
I_WARN = '<svg width="9" height="9" viewBox="0 0 10 10"><path d="M5 1L9 8H1Z" stroke="#f59e0b" stroke-width="1.2" fill="none"/><line x1="5" y1="4" x2="5" y2="6.2" stroke="#f59e0b" stroke-width="1.2"/><circle cx="5" cy="7.5" r=".5" fill="#f59e0b"/></svg>'
I_OK   = '<svg width="9" height="9" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" stroke="#10b981" stroke-width="1.2"/><path d="M3 5l1.5 1.5L7 3.5" stroke="#10b981" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# ── Constants ─────────────────────────────────────────────────────────────────
TICKERS = {
    "Apple Inc. (AAPL)"         : "AAPL",
    "Microsoft Corp. (MSFT)"    : "MSFT",
    "Infosys Ltd. (INFY)"       : "INFY",
    "Tata Consultancy (TCS.NS)" : "TCS.NS",
    "Tesla Inc. (TSLA)"         : "TSLA",
}
NAMES = {v: k.split(" (")[0] for k, v in TICKERS.items()}
EXCH  = {"AAPL":"NASDAQ","MSFT":"NASDAQ","INFY":"NYSE","TCS.NS":"BSE","TSLA":"NASDAQ"}

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_features(ticker):
    df = pd.read_csv(f"data/processed/{ticker}_features.csv")
    df["Date"] = pd.to_datetime(df["Date"], utc=True)
    return df

def load_fund(ticker):
    try:
        return pd.read_csv(f"data/raw/{ticker}_fundamentals.csv").iloc[0].to_dict()
    except Exception:
        return {}

def safe_float(v, default=0.0):
    try: return float(v)
    except: return default

def sparkline(vals, color="#0ea5e9", w=110, h=34):
    v = [float(x) for x in vals if x is not None and str(x) != "nan"]
    if len(v) < 2:
        return ""
    mn, mx = min(v), max(v)
    rng = mx - mn or 1
    n   = len(v)
    pts = " ".join(
        f"{i/(n-1)*w:.1f},{(1-(vv-mn)/rng)*(h-2)+1:.1f}"
        for i, vv in enumerate(v)
    )
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:{h}px;display:block;">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )

# ── Chart functions ───────────────────────────────────────────────────────────
BG   = "#0d1424"
GRID = "#111827"

def price_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["Close"],
        mode="lines", name="Price",
        line=dict(color="#0ea5e9", width=1.8),
        fill="tozeroy", fillcolor="rgba(14,165,233,0.06)"
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA_30"],
        mode="lines", name="MA 30",
        line=dict(color="#f59e0b", width=1.2, dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=df["Date"], y=df["MA_90"],
        mode="lines", name="MA 90",
        line=dict(color="#8b5cf6", width=1.2, dash="dot")
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color="#7b92b8", family="DM Mono", size=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                    y=1.12, font=dict(size=10)),
        xaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(size=9)),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   tickfont=dict(size=9)),
        margin=dict(l=8, r=8, t=28, b=8),
        height=205
    )
    return fig

def rsi_chart(df):
    tail = df.tail(90)
    fig  = go.Figure()
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.06)",
                  line_width=0, annotation_text="Overbought",
                  annotation_font=dict(color="#ef4444", size=9),
                  annotation_position="top left")
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(16,185,129,0.06)",
                  line_width=0, annotation_text="Oversold",
                  annotation_font=dict(color="#10b981", size=9),
                  annotation_position="bottom left")
    fig.add_hline(y=70, line=dict(color="#ef4444", width=1, dash="dot"))
    fig.add_hline(y=30, line=dict(color="#10b981", width=1, dash="dot"))
    fig.add_trace(go.Scatter(
        x=tail["Date"], y=tail["RSI_14"],
        mode="lines", name="RSI 14",
        line=dict(color="#0ea5e9", width=1.6)
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color="#7b92b8", family="DM Mono", size=10),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=9)),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   range=[0, 100], tickfont=dict(size=9)),
        margin=dict(l=8, r=8, t=10, b=8),
        height=135
    )
    return fig

def vol_chart(df):
    tail = df.tail(90)
    colors = ["#10b981" if r >= 0 else "#ef4444"
              for r in tail["Return_1d"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tail["Date"], y=tail["Volume"],
        marker_color=colors, marker_line_width=0, name="Volume"
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color="#7b92b8", family="DM Mono", size=10),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=9)),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   tickfont=dict(size=9)),
        margin=dict(l=8, r=8, t=10, b=8),
        height=135
    )
    return fig

def health_gauge(score):
    label = "Excellent" if score > 80 else "Good" if score > 60 else "Fair" if score > 40 else "Weak"
    color = "#10b981" if score > 80 else "#0ea5e9" if score > 60 else "#f59e0b" if score > 40 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(font=dict(color="#e8eef8", family="DM Mono", size=24)),
        gauge=dict(
            axis=dict(range=[0,100], tickvals=[0,50,100], tickfont=dict(color="#7b92b8",size=8)),
            bar=dict(color=color, thickness=0.28),
            bgcolor="#0d1424", borderwidth=0,
            steps=[dict(range=[0,40],color="#211722"),dict(range=[40,70],color="#211f1b"),dict(range=[70,100],color="#102622")],
            threshold=dict(line=dict(color=color,width=2),value=score)
        )
    ))
    fig.update_layout(paper_bgcolor="#0d1424",plot_bgcolor="#0d1424",font=dict(color="#e8eef8"),margin=dict(l=8,r=8,t=8,b=2),height=155,
                      annotations=[dict(text=f'<span style="color:{color};font-size:10px;font-family:DM Mono">{label}</span>',x=.5,y=.06,showarrow=False,xref="paper",yref="paper")])
    return fig

# ── LLM markdown → HTML ───────────────────────────────────────────────────────
def llm_to_html(md):
    lines = md.splitlines()
    chunks = []
    i = 0

    def format_inline(text):
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

        # Italic
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)

        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

        return text

    while i < len(lines):
        line = lines[i].strip()

        # Empty line
        if not line:
            i += 1
            continue

        # Markdown headings
        heading_line = line

        # Remove bold markers around the heading
        heading_line = re.sub(r'^\*\*\s*', '', heading_line)
        heading_line = re.sub(r'\s*\*\*$', '', heading_line)

        heading_match = re.match(r'^(#{1,3})\s+(.*)', heading_line)

        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2)

            # Remove bold wrapping from heading text too
            title = re.sub(r'^\*\*(.*?)\*\*$', r'\1', title)
            title = format_inline(title)

            chunks.append(
            f'<div class="llm-h{level}">{title}</div>'
            )

            i += 1
            continue

        # Markdown table
        if line.startswith("|") and "|" in line[1:]:

            table_rows = []

            while i < len(lines):
                row = lines[i].strip()

                if not row.startswith("|"):
                    break

                # Skip separator row
                if re.match(
                    r'^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$',
                    row
                ):
                    i += 1
                    continue

                cells = [
                    format_inline(cell.strip())
                    for cell in row.strip("|").split("|")
                ]

                table_rows.append(cells)
                i += 1

            if table_rows:
                html = '<table class="llm-table">'

                # Header
                html += "<thead><tr>"
                for cell in table_rows[0]:
                    html += f"<th>{cell}</th>"
                html += "</tr></thead>"

                # Body
                if len(table_rows) > 1:
                    html += "<tbody>"

                    for row in table_rows[1:]:
                        html += "<tr>"

                        for cell in row:
                            html += f"<td>{cell}</td>"

                        html += "</tr>"

                    html += "</tbody>"

                html += "</table>"

                chunks.append(html)

            continue

        # Bullet points
        if re.match(r'^[-*]\s+', line):
            bullet = re.sub(r'^[-*]\s+', '', line)
            bullet = format_inline(bullet)

            chunks.append(
                f'<div class="llm-bullet">• {bullet}</div>'
            )

            i += 1
            continue

        # Numbered list
        if re.match(r'^\d+\.\s+', line):
            number, text = line.split(".", 1)
            text = format_inline(text.strip())

            chunks.append(
                f'<div class="llm-number">'
                f'<span>{number}.</span> {text}'
                f'</div>'
            )

            i += 1
            continue

        # Horizontal rule
        if re.match(r'^-{3,}$', line) or re.match(r'^\*{3,}$', line):
            chunks.append('<hr class="llm-hr">')
            i += 1
            continue

        # Normal paragraph
        chunks.append(
            f'<p class="llm-p">{format_inline(line)}</p>'
        )

        i += 1

    return '\n'.join(chunks)

# ── Chat helpers ──────────────────────────────────────────────────────────────
def build_context(ticker, name, result, fund, top_f, papers):
    forecast = result["forecast"]
    horizon_days = forecast.get("horizon_days", forecast.get("horizon", 3))
    anomaly  = result["anomaly"]
    shap_str = "\n".join(
        f"  - {f['feature']}: {f['shap_value']:+.4f} ({f['impact']}) — {f['meaning']}"
        for f in top_f
    )
    pm  = safe_float(fund.get("profit_margins"))
    om  = safe_float(fund.get("operating_margins"))
    roe = safe_float(fund.get("return_on_equity"))
    de  = safe_float(fund.get("debt_to_equity"))
    rg  = safe_float(fund.get("revenue_growth"))
    research_str = "\n".join(
        f"  - {p.get('title', 'Untitled')} "
        f"(Published: {str(p.get('published', ''))[:10] or 'Unknown'}, "
        f"Feature: {p.get('feature', 'Unknown')})"
        for p in papers[:5]
    )
    return f"""
Company: {name} ({ticker})
Current Price: ${forecast['current_price']}

ML Forecast:
  Direction: {forecast['direction']}
  Confidence: {forecast['confidence_pct']}%
  Model accuracy: {round(forecast['avg_accuracy']*100,1)}%
  Horizon: {horizon_days} days

Top SHAP drivers:
{shap_str}

Anomaly status: {anomaly['status']}
{anomaly['summary']}

Key fundamentals:
  Profit margin:    {pm*100:.1f}%
  Operating margin: {om*100:.1f}%
  Return on equity: {roe*100:.1f}%
  Debt/equity:      {de:.2f}
  Revenue growth:   {rg*100:.1f}%

Research analysis summary:
{result['llm_explanation'][:1500]}

Supporting research papers:
{research_str}
""".strip()

def groq_chat(user_msg, history, context, name, ticker):
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        system = (
            f"You are FinSight AI, an intelligent financial analyst assistant. "
            f"You are currently analysing {name} ({ticker}).\n\n"

            f"ANALYSIS CONTEXT:\n{context}\n\n"

            f"Answer using ONLY the information provided in the analysis context. "
            f"Do not invent financial facts, research findings, or paper conclusions. "

            f"When explaining a prediction, clearly distinguish between: "
            f"(1) ML/SHAP evidence, "
            f"(2) fundamental evidence, and "
            f"(3) supporting research. "

            f"If research papers are listed, mention their titles when relevant. "
            f"Do not claim that a paper supports a conclusion unless the provided "
            f"research summary actually supports that claim. "

            f"Use concise Markdown with headings and bullet points where useful. "
            f"Keep responses under 300 words."
        )
        messages = [{"role": "system", "content": system}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_msg})
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.2,
            max_tokens=800
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Chat error: {e}"

# ── Session state ─────────────────────────────────────────────────────────────
if "cache" not in st.session_state:
    st.session_state.cache = {}
if "chat"  not in st.session_state:
    st.session_state.chat  = {}

# ── Navigation state ───────────────────────────────────────────────────────────
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-logo">
      <div class="sb-mark">{I_LOGO}</div>
      <div>
        <div class="sb-name">FinSight AI</div>
        <div class="sb-tag">Financial Intelligence Platform</div>
      </div>
    </div>
    <div class="sb-sec">Navigation</div>
    """, unsafe_allow_html=True)

    # Use plain text symbols here. Streamlit buttons do not parse inline SVG/HTML
    # inside their labels, which would otherwise display the raw SVG source.
    nav_items = [
        ("Dashboard", "▦"),
        ("Forecasting", "⌁"),
        ("Anomaly Detection", "△"),
        ("AI Analyst", "⊕"),
    ]

    for page_name, icon in nav_items:
        is_active = st.session_state.active_page == page_name
        label = f"{icon}  {page_name}"
        if st.button(
            label,
            key=f"nav_{page_name.lower().replace(' ', '_')}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_page = page_name
            st.rerun()

    st.markdown("""
    <div class="sb-div"></div>
    <div class="sb-sec">Watchlist</div>
    """, unsafe_allow_html=True)

    for sym in ["AAPL", "MSFT", "INFY", "TCS.NS", "TSLA"]:
        try:
            df_w = pd.read_csv(f"data/processed/{sym}_features.csv")
            chg  = float(df_w["Return_1d"].iloc[-1]) * 100
            cls  = "up" if chg >= 0 else "dn"
            arr  = "▲" if chg >= 0 else "▼"
            st.markdown(
                f'<div class="sb-tick">'
                f'<span class="sb-sym">{sym}</span>'
                f'<span class="sb-chg {cls}">{arr} {abs(chg):.2f}%</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        except Exception:
            pass

# ── Selector ──────────────────────────────────────────────────────────────────
col_sel, col_btn, col_pad = st.columns([3, 1, 5])
with col_sel:
    selected = st.selectbox("Company", list(TICKERS.keys()),
                            label_visibility="collapsed")
with col_btn:
    run = st.button("Analyse", use_container_width=True, type="primary")

# Trigger analysis
if run:
    ticker = TICKERS[selected]
    if ticker not in st.session_state.cache:
        with st.spinner(f"Running ML + RAG pipeline for {ticker}..."):
            try:
                from src.rag.rag_chain import analyze_ticker
                st.session_state.cache[ticker] = analyze_ticker(ticker)
            except Exception as e:
                st.error(f"Pipeline error: {e}")
                st.stop()
    if ticker not in st.session_state.chat:
        st.session_state.chat[ticker] = []

# ── Functional navigation pages ───────────────────────────────────────────────
ticker = TICKERS[selected]

def get_analysis_data(ticker):
    """Return the cached analysis and supporting data, or None if not analysed."""
    if ticker not in st.session_state.cache:
        return None
    result = st.session_state.cache[ticker]
    forecast = result["forecast"]
    anomaly = result["anomaly"]
    papers = result["papers_used"]
    name = NAMES[ticker]
    exch = EXCH.get(ticker, "")
    df = load_features(ticker)
    fund = load_fund(ticker)
    try:
        shap_d = json.load(open(f"data/shap/{ticker}_shap.json"))
        top_f = shap_d["top_features"]
    except Exception:
        top_f = []
    return result, forecast, anomaly, papers, name, exch, df, fund, top_f

def render_page_header(title, subtitle):
    st.markdown(
        f'<div class="sec">{title}</div>'
        f'<div style="font-size:.78rem;color:#7b92b8;margin:-.25rem 0 1rem;">{subtitle}</div>',
        unsafe_allow_html=True
    )

def render_forecasting_page(data):
    result, forecast, anomaly, papers, name, exch, df, fund, top_f = data
    direction = "UP" if "UP" in forecast["direction"] else "DOWN"
    direction_color = "#10b981" if direction == "UP" else "#ef4444"
    confidence = float(forecast.get("confidence_pct", 0))
    horizon_days = forecast.get("horizon_days", forecast.get("horizon", 3))
    accuracy = float(forecast.get("avg_accuracy", 0)) * 100
    current_price = float(forecast.get("current_price", df["Close"].iloc[-1]))

    render_page_header("Forecasting", f"{name} ({ticker}) · {horizon_days}-day machine-learning forecast")

    kpis = st.columns(4)
    vals = [
        ("Direction", direction, direction_color, "Model forecast"),
        ("Confidence", f"{confidence:.1f}%", "#0ea5e9", "Prediction confidence"),
        ("Validation Accuracy", f"{accuracy:.1f}%", "#10b981", "5-fold TimeSeries"),
        ("Current Price", f"${current_price:,.2f}", "#e8eef8", f"{horizon_days}-day horizon"),
    ]
    for col,(lab,val,colr,sub) in zip(kpis,vals):
        col.markdown(f'<div class="page-kpi"><div class="mc-lbl">{lab}</div><div class="mc-val" style="color:{colr};">{val}</div><div class="mc-sub" style="color:#7b92b8;">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec section-tight">Forecast Overview</div>', unsafe_allow_html=True)
    left,right=st.columns([7,5],gap="medium")
    with left:
        st.markdown('<div class="chart-card"><div class="chart-head"><span>Historical Price Trend</span><span>120D · MA 30 · MA 90</span></div>',unsafe_allow_html=True)
        st.plotly_chart(price_chart(df.tail(120)),use_container_width=True,config={"displayModeBar":False},key="forecast_history_chart")
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown(f'''<div class="page-card"><div class="page-card-title"><span>Prediction Summary</span><span class="page-card-sub">XGBOOST</span></div>
        <div style="display:flex;align-items:baseline;justify-content:space-between;margin:.25rem 0 .8rem;"><span style="font:700 2.05rem 'DM Mono',monospace;color:{direction_color};">{direction}</span><span style="font-size:.7rem;color:#7b92b8;">{confidence:.1f}% confidence</span></div>
        <div class="prow"><span class="pk">Current price</span><span class="pv">${current_price:,.2f}</span></div>
        <div class="prow"><span class="pk">Forecast horizon</span><span class="pv">{horizon_days} days</span></div>
        <div class="prow"><span class="pk">Validation</span><span class="pv">5-fold TimeSeries</span></div>
        <div class="prow"><span class="pk">Accuracy</span><span class="pv">{accuracy:.1f}%</span></div>
        <div class="prow"><span class="pk">Features</span><span class="pv">41 engineered</span></div></div>''',unsafe_allow_html=True)

    future = forecast.get("predictions") or forecast.get("future_predictions") or forecast.get("forecast_values")
    if isinstance(future,(list,tuple)) and future:
        try:
            future_values=[float(x) for x in future]
            last_date=pd.to_datetime(df["Date"]).iloc[-1]
            dates=pd.date_range(last_date+pd.Timedelta(days=1),periods=len(future_values),freq="D")
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=dates,y=future_values,mode="lines+markers",name="Forecast",line=dict(color=direction_color,width=2)))
            fig.add_trace(go.Scatter(x=[last_date],y=[current_price],mode="markers",name="Last Close",marker=dict(color="#0ea5e9",size=7)))
            fig.update_layout(paper_bgcolor=BG,plot_bgcolor=BG,font=dict(color="#7b92b8",family="DM Mono",size=10),margin=dict(l=8,r=8,t=18,b=8),height=220,xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor=GRID),legend=dict(orientation="h",y=1.08))
            st.markdown('<div class="sec section-tight">Forward Projection</div>',unsafe_allow_html=True)
            st.markdown('<div class="chart-card">',unsafe_allow_html=True)
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False},key="forecast_projection_chart")
            st.markdown('</div>',unsafe_allow_html=True)
        except Exception:
            pass

    if top_f:
        st.markdown('<div class="sec section-tight">Prediction Drivers</div>',unsafe_allow_html=True)
        max_abs=max(abs(float(f["shap_value"])) for f in top_f) or 1
        cards=[]
        for f in top_f[:5]:
            val=float(f["shap_value"]); color="#10b981" if val>0 else "#ef4444"; pct=min(abs(val)/max_abs,1)*100
            cards.append(f'<div class="shap-mini"><div class="shap-top"><span class="shap-feature">{f["feature"].replace("_"," ")}</span><span class="shap-value" style="color:{color};">{val:+.4f}</span></div><div class="shap-impact">{"Positive" if val>0 else "Negative"} impact</div><div class="shap-track"><div class="shap-fill" style="width:{pct:.1f}%;background:{color};"></div></div></div>')
        st.markdown('<div class="shap-grid">'+''.join(cards)+'</div>',unsafe_allow_html=True)


def render_anomaly_page(data):
    result, forecast, anomaly, papers, name, exch, df, fund, top_f = data
    is_anom=anomaly["is_anomaly"]
    status="ANOMALY DETECTED" if is_anom else "NORMAL"
    status_color="#ef4444" if is_anom else "#10b981"
    deviations=anomaly.get("deviations",[])
    latest_return=float(df["Return_1d"].iloc[-1])*100
    latest_vol=float(df["Volatility_7d"].iloc[-1])
    latest_rsi=float(df["RSI_14"].iloc[-1])

    render_page_header("Anomaly Detection",f"{name} ({ticker}) · Isolation Forest risk monitoring")
    kpis=st.columns(4)
    vals=[("Status",status,status_color,"Isolation Forest"),("1-Day Return",f"{latest_return:+.2f}%","#10b981" if latest_return>=0 else "#ef4444","Latest movement"),("Volatility 7d",f"{latest_vol:.4f}","#f59e0b","Latest reading"),("RSI 14d",f"{latest_rsi:.1f}","#0ea5e9","Momentum reading")]
    for col,(lab,val,color,sub) in zip(kpis,vals):
        col.markdown(f'<div class="page-kpi"><div class="mc-lbl">{lab}</div><div class="mc-val" style="color:{color};font-size:{"1.0rem" if lab=="Status" else "1.15rem"};">{val}</div><div class="mc-sub" style="color:#7b92b8;">{sub}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="sec section-tight">Risk Monitor</div>',unsafe_allow_html=True)
    left,right=st.columns([5,7],gap="medium")
    with left:
        dev_rows=''
        for d in deviations[:8]:
            z=float(d.get("z_score",0)); zc="#ef4444" if abs(z)>3 else "#f59e0b" if abs(z)>2 else "#7b92b8"
            dev_rows+=f'<div class="prow"><span class="pk">{d.get("feature","Unknown").replace("_"," ")}</span><span class="pv" style="color:{zc};">z = {z:+.2f}</span></div>'
        if not dev_rows: dev_rows='<div style="font-size:.72rem;color:#3d5270;padding:.3rem 0;">No significant deviations detected.</div>'
        st.markdown(f'''<div class="page-card"><div class="page-card-title"><span>Detection Summary</span><span class="page-card-sub">ISOLATION FOREST</span></div>
        <div style="display:flex;align-items:center;gap:.5rem;margin:.15rem 0 .7rem;"><span style="width:7px;height:7px;border-radius:50%;background:{status_color};box-shadow:0 0 8px {status_color};"></span><span style="font:600 .75rem 'DM Mono',monospace;color:{status_color};">{status}</span></div>
        <div style="font-size:.77rem;color:#b8c8e0;line-height:1.6;margin-bottom:.8rem;">{anomaly.get("summary","No anomaly summary available.")}</div>
        <div class="page-card-title" style="margin-bottom:.3rem;">Feature Deviations</div>{dev_rows}</div>''',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="chart-card"><div class="chart-head"><span>Recent Trading Volume</span><span>90D WINDOW</span></div>',unsafe_allow_html=True)
        st.plotly_chart(vol_chart(df),use_container_width=True,config={"displayModeBar":False},key="anomaly_volume_chart")
        st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="sec section-tight">Momentum & Volatility</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="medium")
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-head"><span>RSI · 14 Day</span><span>0 — 100</span></div>',unsafe_allow_html=True)
        st.plotly_chart(rsi_chart(df),use_container_width=True,config={"displayModeBar":False},key="anomaly_rsi_chart")
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        rsi_state="Overbought" if latest_rsi>=70 else "Oversold" if latest_rsi<=30 else "Neutral"
        vol_state="Elevated" if latest_vol>float(df["Volatility_7d"].rolling(30).median().iloc[-1]) else "Stable"
        ret_state="Positive" if latest_return>=0 else "Negative"
        rsi_color="#f59e0b" if rsi_state!="Neutral" else "#7b92b8"
        vol_color="#f59e0b" if vol_state=="Elevated" else "#10b981"
        ret_color="#10b981" if latest_return>=0 else "#ef4444"
        with st.container(border=True):
            st.markdown(
                '<div class="inner-card-title"><span>Risk Interpretation</span><span>SIGNALS</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="signal-row"><span>RSI state</span><strong style="color:{rsi_color};">{rsi_state}</strong></div>'
                f'<div class="signal-row"><span>Volatility</span><strong style="color:{vol_color};">{vol_state}</strong></div>'
                f'<div class="signal-row"><span>Latest return</span><strong style="color:{ret_color};">{ret_state}</strong></div>',
                unsafe_allow_html=True,
            )


def render_ai_analyst_page(data):
    result, forecast, anomaly, papers, name, exch, df, fund, top_f = data
    direction = "UP" if "UP" in forecast["direction"] else "DOWN"

    render_page_header(
        "AI Analyst",
        f"Ask questions about {name} ({ticker}) using the complete analysis context"
    )

    st.markdown(f"""
    <div style="background:#0d1424;border:1px solid #1a2744;
      border-radius:8px;padding:.9rem 1rem;margin-bottom:1rem;">
      <div style="font-size:.62rem;font-weight:600;color:#7b92b8;
        text-transform:uppercase;letter-spacing:.09em;margin-bottom:.3rem;">
        AI Analyst · {name} ({ticker})
      </div>
      <div style="font-size:.78rem;color:#b8c8e0;line-height:1.5;">
        Ask about the prediction, SHAP drivers, anomaly status, fundamentals,
        or supporting research. Answers are restricted to the current analysis context.
      </div>
    </div>
    """, unsafe_allow_html=True)

    if ticker not in st.session_state.chat:
        st.session_state.chat[ticker] = []

    ctx = build_context(ticker, name, result, fund, top_f, papers)

    for msg in st.session_state.chat[ticker]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(f"Ask about {name}...")
    if user_input:
        st.session_state.chat[ticker].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = groq_chat(
                    user_input,
                    st.session_state.chat[ticker][:-1],
                    ctx, name, ticker
                )
            st.markdown(reply)
        st.session_state.chat[ticker].append({"role": "assistant", "content": reply})

    if not st.session_state.chat[ticker]:
        st.markdown('<div class="sec">Suggested questions</div>', unsafe_allow_html=True)
        for q in [
            f"Why is the model predicting {direction.lower()} for {ticker}?",
            f"What are the biggest risk factors for {name}?",
            f"How healthy is {name}'s balance sheet?",
            "What do the SHAP values tell us about this prediction?",
            "Are there any anomalies I should be concerned about?",
        ]:
            st.markdown(
                f'<div style="font-size:.78rem;color:#7b92b8;padding:.35rem 0;'
                f'border-bottom:1px solid #111827;">{q}</div>',
                unsafe_allow_html=True
            )

# Non-dashboard pages render here and stop before the original dashboard renderer.
if st.session_state.active_page != "Dashboard":
    data = get_analysis_data(ticker)
    if data is None:
        render_page_header(
            st.session_state.active_page,
            f"No analysis is loaded for {NAMES[ticker]} ({ticker}) yet."
        )
        st.info("Select a company above and click **Analyse** first. Then return to this section.")
        st.stop()

    if st.session_state.active_page == "Forecasting":
        render_forecasting_page(data)
    elif st.session_state.active_page == "Anomaly Detection":
        render_anomaly_page(data)
    elif st.session_state.active_page == "AI Analyst":
        render_ai_analyst_page(data)
    st.stop()

if ticker in st.session_state.cache:
    # ── Main content (Dashboard) ─────────────────────────────────────────────────
    result   = st.session_state.cache[ticker]
    forecast = result["forecast"]
    horizon_days = forecast.get("horizon_days", forecast.get("horizon", 3))
    anomaly  = result["anomaly"]
    papers   = result["papers_used"]
    name     = NAMES[ticker]
    exch     = EXCH.get(ticker, "")
    df       = load_features(ticker)
    fund     = load_fund(ticker)

    # Load SHAP data
    try:
        shap_d  = json.load(open(f"data/shap/{ticker}_shap.json"))
        top_f   = shap_d["top_features"]
    except Exception:
        top_f = []

    is_up   = "UP" in forecast["direction"]
    is_anom = anomaly["is_anomaly"]
    price   = float(df["Close"].iloc[-1])
    ret1d   = float(df["Return_1d"].iloc[-1]) * 100
    health  = safe_float(
        fund.get("financial_health_score") or df["financial_health_score"].iloc[-1]
    )
    direction  = "UP" if is_up else "DOWN"
    chg_col    = "#10b981" if ret1d >= 0 else "#ef4444"
    chg_arr    = "▲" if ret1d >= 0 else "▼"
    dir_cls    = "pill-up" if is_up else "pill-dn"
    dir_icon   = I_UP if is_up else I_DN
    anom_cls   = "pill-warn" if is_anom else "pill-ok"
    anom_icon  = I_WARN if is_anom else I_OK
    anom_text  = "Anomaly" if is_anom else "Normal"
    pm  = safe_float(fund.get("profit_margins"))
    om  = safe_float(fund.get("operating_margins"))
    roe = safe_float(fund.get("return_on_equity"))
    de  = safe_float(fund.get("debt_to_equity"))

    # ── Company header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="co-hdr">
      <div>
        <div class="co-name">{name}</div>
        <div class="co-sym">{ticker}</div>
      </div>
      <span class="co-badge">{exch}</span>
      <div class="co-divr"></div>
      <div>
        <div class="co-lbl">Price</div>
        <div style="display:flex;align-items:baseline;gap:.4rem;">
          <span class="co-price">${price:,.2f}</span>
          <span class="co-chg" style="color:{chg_col};">{chg_arr} {abs(ret1d):.2f}%</span>
        </div>
      </div>
      <div class="co-divr"></div>
      <div>
        <div class="co-lbl">3-day Forecast</div>
        <span class="pill {dir_cls}">{dir_icon}&nbsp;{direction}&nbsp;&nbsp;{forecast['confidence_pct']}%</span>
      </div>
      <div class="co-divr"></div>
      <div>
        <div class="co-lbl">Risk Status</div>
        <span class="pill {anom_cls}">{anom_icon}&nbsp;{anom_text}</span>
      </div>
      <div class="co-divr"></div>
      <div>
        <div class="co-lbl">Model Accuracy</div>
        <span style="font-size:1.05rem;font-weight:600;
          font-family:'DM Mono',monospace;color:#e8eef8;">
          {round(forecast['avg_accuracy']*100,1)}%
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric cards ──────────────────────────────────────────────────────
    st.markdown('<div class="sec">Key Metrics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Current Price",    f"${price:,.2f}",
         f"{chg_arr} {abs(ret1d):.2f}% today", chg_col,
         df["Close"].tail(30).tolist(), "#0ea5e9"),
        (c2, "Profit Margin",    f"{pm*100:.1f}%",
         "Net profit margin",
         "#10b981" if pm > 0.1 else "#f59e0b",
         df["Return_30d"].tail(30).tolist(), "#10b981"),
        (c3, "Operating Margin", f"{om*100:.1f}%",
         "Operating efficiency",
         "#10b981" if om > 0.15 else "#f59e0b",
         df["Volatility_30d"].tail(30).tolist(), "#8b5cf6"),
        (c4, "Return on Equity", f"{roe*100:.1f}%",
         "Shareholder returns",
         "#10b981" if roe > 0.15 else "#f59e0b",
         df["RSI_14"].tail(30).tolist(), "#f59e0b"),
        (c5, "Financial Health", f"{health:.0f} / 100",
         "Excellent" if health > 80 else "Good" if health > 60 else "Fair",
         "#10b981" if health > 80 else "#0ea5e9" if health > 60 else "#f59e0b",
         df["financial_health_score"].tail(30).tolist(), "#0ea5e9"),
    ]
    for col, lbl, val, sub, sub_c, sp_vals, sp_col in cards:
        col.markdown(f"""
        <div class="mc">
          <div class="mc-lbl">{lbl}</div>
          <div class="mc-val">{val}</div>
          <div class="mc-sub" style="color:{sub_c};">{sub}</div>
          <div class="mc-sp">{sparkline(sp_vals, sp_col)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_analysis, tab_chat = st.tabs(["Analysis", "AI Chat"])

    # ═══════════════════════════════════════════════════════
    # ANALYSIS TAB
    # ═══════════════════════════════════════════════════════
    with tab_analysis:
        st.markdown('<div class="sec section-tight">Market Analysis</div>', unsafe_allow_html=True)

        # Balanced first row: chart and summary have similar visual weight.
        market_col, summary_col = st.columns([7,5], gap="medium")
        with market_col:
            st.markdown('<div class="chart-card"><div class="chart-head"><span>Price Trend · 120 Days</span><span>PRICE · MA 30 · MA 90</span></div>', unsafe_allow_html=True)
            st.plotly_chart(price_chart(df.tail(120)), use_container_width=True, config={"displayModeBar":False}, key="dashboard_price_chart")
            st.markdown('</div>', unsafe_allow_html=True)
        with summary_col:
            fc_color="#10b981" if is_up else "#ef4444"
            st.markdown(f'''<div class="page-card"><div class="page-card-title"><span>Model Summary</span><span class="page-card-sub">XGBOOST</span></div>
            <div style="display:flex;align-items:baseline;justify-content:space-between;margin:.2rem 0 .8rem;"><span style="font:700 2.05rem 'DM Mono',monospace;color:{fc_color};">{direction}</span><span style="font-size:.7rem;color:#7b92b8;">{forecast['confidence_pct']}% confidence</span></div>
            <div class="prow"><span class="pk">Current price</span><span class="pv">${price:,.2f}</span></div>
            <div class="prow"><span class="pk">Validation</span><span class="pv">5-fold TimeSeries</span></div>
            <div class="prow"><span class="pk">Accuracy</span><span class="pv">{round(forecast['avg_accuracy']*100,1)}%</span></div>
            <div class="prow"><span class="pk">Horizon</span><span class="pv">{horizon_days} days</span></div>
            <div class="prow"><span class="pk">Features</span><span class="pv">41 engineered</span></div></div>''',unsafe_allow_html=True)

        if top_f:
            st.markdown('<div class="sec section-tight">Top Prediction Drivers</div>', unsafe_allow_html=True)
            max_abs=max(abs(float(f["shap_value"])) for f in top_f) or 1
            cards=[]
            for f in top_f[:5]:
                val=float(f["shap_value"]); color="#10b981" if val>0 else "#ef4444"; pct=min(abs(val)/max_abs,1)*100
                cards.append(f'<div class="shap-mini"><div class="shap-top"><span class="shap-feature">{f["feature"].replace("_"," ")}</span><span class="shap-value" style="color:{color};">{val:+.4f}</span></div><div class="shap-impact">{"Positive" if val>0 else "Negative"} impact</div><div class="shap-track"><div class="shap-fill" style="width:{pct:.1f}%;background:{color};"></div></div></div>')
            st.markdown('<div class="shap-grid">'+''.join(cards)+'</div>',unsafe_allow_html=True)

        st.markdown('<div class="sec section-tight">Technical Indicators</div>', unsafe_allow_html=True)
        tech_left,tech_right=st.columns(2,gap="medium")
        with tech_left:
            st.markdown('<div class="chart-card"><div class="chart-head"><span>RSI · 14 Day</span><span>90D WINDOW</span></div>',unsafe_allow_html=True)
            st.plotly_chart(rsi_chart(df),use_container_width=True,config={"displayModeBar":False},key="dashboard_rsi_chart")
            st.markdown('</div>',unsafe_allow_html=True)
        with tech_right:
            st.markdown('<div class="chart-card"><div class="chart-head"><span>Trading Volume</span><span>90D WINDOW</span></div>',unsafe_allow_html=True)
            st.plotly_chart(vol_chart(df),use_container_width=True,config={"displayModeBar":False},key="dashboard_volume_chart")
            st.markdown('</div>',unsafe_allow_html=True)

        st.markdown('<div class="sec section-tight">Risk &amp; Financial Health</div>', unsafe_allow_html=True)
        risk_left,risk_right=st.columns([1,1],gap="medium")
        with risk_left:
            devs=anomaly.get("deviations",[]); status_color="#ef4444" if is_anom else "#10b981"; status_label="ANOMALY DETECTED" if is_anom else "NORMAL"
            dev_rows=''
            for d in devs[:4]:
                z=float(d.get("z_score",0)); zc="#ef4444" if abs(z)>3 else "#f59e0b" if abs(z)>2 else "#7b92b8"
                dev_rows+=f'<div class="prow"><span class="pk">{d.get("feature","Unknown").replace("_"," ")}</span><span class="pv" style="color:{zc};">z = {z:+.2f}</span></div>'
            st.markdown(f'''<div class="page-card"><div class="page-card-title"><span>Detection Summary</span><span class="page-card-sub">ISOLATION FOREST</span></div>
            <div style="display:flex;align-items:center;gap:.5rem;margin:.1rem 0 .6rem;"><span style="width:7px;height:7px;border-radius:50%;background:{status_color};box-shadow:0 0 8px {status_color};"></span><span style="font:600 .75rem 'DM Mono',monospace;color:{status_color};">{status_label}</span></div>
            <div style="font-size:.75rem;color:#b8c8e0;line-height:1.55;margin-bottom:.7rem;">{anomaly.get('summary','No anomaly summary available.')}</div>
            <div class="page-card-title" style="margin-bottom:.25rem;">Feature Deviations</div>{dev_rows or '<div style="font-size:.72rem;color:#3d5270;">No significant deviations detected.</div>'}</div>''',unsafe_allow_html=True)
        with risk_right:
            health_label='Excellent' if health>80 else 'Good' if health>60 else 'Fair' if health>40 else 'Weak'
            health_color="#10b981" if health>80 else "#0ea5e9" if health>60 else "#f59e0b" if health>40 else "#ef4444"
            # Financial Health uses a real Streamlit bordered container.
            # This keeps the Plotly gauge and the metrics physically inside one card.
            current_ratio=fund.get("current_ratio") or "N/A"
            with st.container(border=True):
                st.markdown(
                    '<div class="inner-card-title"><span>Financial Health</span><span>BALANCE SHEET</span></div>',
                    unsafe_allow_html=True,
                )
                gauge_col, details_col = st.columns([1.15, 0.85], gap="medium")
                with gauge_col:
                    st.plotly_chart(
                        health_gauge(health),
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key="dashboard_health_gauge_final",
                    )
                with details_col:
                    st.markdown(
                        f'<div class="mc-lbl">Health Score</div>'
                        f'<div class="health-score">{health:.0f}<span> / 100</span></div>'
                        f'<div class="health-label">{health_label}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="health-row"><span>Debt / Equity</span><strong>{de:.2f}</strong></div>'
                        f'<div class="health-row"><span>Current Ratio</span><strong>{current_ratio}</strong></div>'
                        f'<div class="health-row"><span>ROE</span><strong>{roe*100:.1f}%</strong></div>',
                        unsafe_allow_html=True,
                    )
        st.markdown('<div class="sec section-tight">Peer Comparison</div>', unsafe_allow_html=True)
        comp_rows=''
        for sym,nm in [("AAPL","Apple"),("MSFT","Microsoft"),("INFY","Infosys"),("TCS.NS","TCS"),("TSLA","Tesla")]:
            try:
                f2=load_fund(sym); pm2=safe_float(f2.get("profit_margins")); om2=safe_float(f2.get("operating_margins")); roe2=safe_float(f2.get("return_on_equity")); de2=safe_float(f2.get("debt_to_equity")); hl="hl" if sym==ticker else ""
                try:
                    fus=json.load(open(f"data/fusion/{sym}_fusion.json")); d2=fus["forecast"]["direction"]; dcl="up" if "UP" in d2 else "dn"; dlb="▲ UP" if "UP" in d2 else "▼ DN"
                except Exception: dcl,dlb="","—"
                comp_rows+=f'<tr class="{hl}"><td>{nm}</td><td>{pm2*100:.1f}%</td><td>{om2*100:.1f}%</td><td>{roe2*100:.1f}%</td><td>{de2:.2f}</td><td class="{dcl}">{dlb}</td></tr>'
            except Exception: pass
        st.markdown(f'<div class="page-card" style="padding:.55rem .7rem;"><table class="ct"><thead><tr><th>Company</th><th>Profit Margin</th><th>Op. Margin</th><th>ROE</th><th>Debt / Eq.</th><th>Forecast</th></tr></thead><tbody>{comp_rows}</tbody></table></div>',unsafe_allow_html=True)

        st.markdown('<div class="sec">Research Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="llm-box">{llm_to_html(result["llm_explanation"])}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec">Supporting Research Papers</div>',unsafe_allow_html=True)
        visible=papers[:5]
        for i,p in enumerate(visible):
            n=len(visible); cls=("pr pr-only" if n==1 else "pr pr-first" if i==0 else "pr pr-last" if i==n-1 else "pr")
            pub=str(p.get("published",""))[:10] or "—"; feat=p.get("feature","—"); url=p.get("url","#"); title=p.get("title","Untitled"); idx=f"0{i+1}" if i<9 else str(i+1)
            st.markdown(f'<div class="{cls}"><div class="pr-idx">{idx}</div><div><div class="pr-title">{title}</div><div class="pr-meta"><span class="pr-tag">Published {pub}</span><span class="pr-tag">Feature: {feat}</span><a href="{url}" target="_blank" class="pr-link">View paper &rarr;</a></div></div></div>',unsafe_allow_html=True)

        st.markdown("<div style=\"margin-top:2rem;padding-top:1rem;border-top:1px solid #1a2744;text-align:center;font-size:.65rem;color:#3d5270;font-family:'DM Mono',monospace;\">FinSight AI · Not financial advice · XGBoost · SHAP · Isolation Forest · LangChain · ChromaDB · Groq</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════
    # AI CHAT TAB
    # ═══════════════════════════════════════════════════════
    with tab_chat:
        st.markdown(f"""
        <div style="background:#0d1424;border:1px solid #1a2744;
          border-radius:8px;padding:.75rem 1rem;margin-bottom:1rem;">
          <div style="font-size:.62rem;font-weight:600;color:#7b92b8;
            text-transform:uppercase;letter-spacing:.09em;margin-bottom:.3rem;">
            AI Analyst · {name} ({ticker})
          </div>
          <div style="font-size:.78rem;color:#b8c8e0;line-height:1.5;">
            Ask anything about {name} — the model's prediction, SHAP drivers,
            anomaly status, fundamentals, or research findings.
            The AI has full context of the analysis above.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Initialise chat history for this ticker
        if ticker not in st.session_state.chat:
            st.session_state.chat[ticker] = []

        # Build context once
        ctx = build_context(ticker, name, result, fund, top_f, papers)

        # Render chat history
        for msg in st.session_state.chat[ticker]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input
        user_input = st.chat_input(f"Ask about {name}...")
        if user_input:
            st.session_state.chat[ticker].append(
                {"role": "user", "content": user_input}
            )
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = groq_chat(
                        user_input,
                        st.session_state.chat[ticker][:-1],
                        ctx, name, ticker
                    )
                st.markdown(reply)

            st.session_state.chat[ticker].append(
                {"role": "assistant", "content": reply}
            )

        # Suggested questions (only when chat is empty)
        if not st.session_state.chat[ticker]:
            st.markdown("""
            <div style="margin-top:1rem;">
              <div style="font-size:.62rem;font-weight:600;color:#3d5270;
                text-transform:uppercase;letter-spacing:.09em;margin-bottom:.5rem;">
                Suggested questions
              </div>
            </div>""", unsafe_allow_html=True)
            suggestions = [
                f"Why is the model predicting {direction.lower()} for {ticker}?",
                f"What are the biggest risk factors for {name}?",
                f"How healthy is {name}'s balance sheet?",
                "What do the SHAP values tell us about this prediction?",
                "Are there any anomalies I should be concerned about?",
            ]
            for q in suggestions:
                st.markdown(
                    f'<div style="font-size:.78rem;color:#7b92b8;'
                    f'padding:.3rem 0;border-bottom:1px solid #111827;">'
                    f'{q}</div>',
                    unsafe_allow_html=True
                )

# ── Empty / landing state ─────────────────────────────────────────────────────
else:
        st.markdown("""
        <div class="empty">
          <svg width="42" height="42" viewBox="0 0 48 48" fill="none"
               style="margin-bottom:.85rem;">
            <path d="M6 34l10-10 8 8 10-14 8 8"
                  stroke="#1a2744" stroke-width="2.5"
                  stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="42" cy="26" r="3" fill="#0ea5e9" opacity=".5"/>
          </svg>
          <div class="empty-t">Select a company and click Analyse</div>
          <div class="empty-s">
            ML forecasting · SHAP explainability · arXiv RAG ·
            Anomaly detection · Competitor benchmarking · AI chat
          </div>
          <div class="stat-g">
            <div><div class="stat-v">5</div><div class="stat-l">Tickers</div></div>
            <div><div class="stat-v">41</div><div class="stat-l">Features</div></div>
            <div><div class="stat-v">200</div><div class="stat-l">arXiv papers</div></div>
            <div><div class="stat-v">5.8k</div><div class="stat-l">Training rows</div></div>
            <div><div class="stat-v">5</div><div class="stat-l">ML models</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)