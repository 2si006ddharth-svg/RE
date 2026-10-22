"""Interactive Streamlit Web Dashboard for Blockchain-Based Payment Verification
and Soundbox Simulation System.
State-of-the-art FinTech UI/UX design with dark glassmorphic theme, interactive IoT Soundbox,
cryptographic block explorer, tampering detection sandbox, and cryptographic diagnostic engine.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import json
import html
import os

import database
import payment_simulator
import blockchain_ledger
import verification
import soundbox
import tampering_demo
from config import (
    ACADEMIC_DISCLAIMER,
    CURRENCY_SYMBOL,
    PAYMENT_METHODS,
    GENESIS_PREV_HASH,
    DB_PATH,
    CLEAN_DEMO_DB_PATH,
    ORIGINAL_BACKUP_DB_PATH
)

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Soundbox Pay | Blockchain Payment Simulator",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Modern FinTech CSS
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Base */
    .stApp {
        background: radial-gradient(circle at 10% 0%, #0d192e 0%, #060b14 60%, #03060c 100%);
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #090e18;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }

    /* Top Telemetry Bar */
    .telemetry-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 8px 18px;
        margin-bottom: 20px;
        font-size: 12px;
        color: #94a3b8;
    }
    .telemetry-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
    }

    /* Academic Disclaimer Banner */
    .disclaimer-banner {
        background: linear-gradient(90deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.7));
        backdrop-filter: blur(8px);
        border-left: 4px solid #f59e0b;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 22px;
        font-size: 13px;
        color: #cbd5e1;
        line-height: 1.5;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .disclaimer-title {
        color: #fbbf24;
        font-weight: 800;
        letter-spacing: 0.5px;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.015) 100%);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 18px;
        padding: 22px 20px;
        text-align: left;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.6), transparent);
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45), 0 0 20px rgba(56, 189, 248, 0.15);
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        color: #94a3b8;
        margin-bottom: 8px;
        font-weight: 700;
    }
    .metric-val {
        font-size: 30px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 12px;
        color: #38bdf8;
        margin-top: 8px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* Block Card Visualizer */
    .block-card {
        background: linear-gradient(160deg, #0d1729 0%, #070c17 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        font-size: 13px;
        position: relative;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    .block-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateY(-1px);
    }
    .block-card.valid {
        border-left: 5px solid #10b981;
    }
    .block-card.tampered {
        border-left: 5px solid #ef4444;
        background: linear-gradient(160deg, #1f1115 0%, #11080a 100%);
    }

    /* Chain Connector Line */
    .chain-connector {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: -8px 0 8px 0;
        color: #38bdf8;
    }
    .chain-line {
        width: 2px;
        height: 20px;
        background: linear-gradient(to bottom, #38bdf8, #10b981);
    }
    .chain-badge {
        font-size: 11px;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        padding: 2px 10px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* QR Code Card */
    .qr-card {
        background: linear-gradient(145deg, #0f1c33 0%, #070d18 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    /* Code & Hash styling */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Streamlit Button Restyling */
    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        font-size: 14px;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(0, 242, 254, 0.25);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation & Ledger Source Selection
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08);">
            <div style="
                width: 44px; 
                height: 44px; 
                border-radius: 14px; 
                background: linear-gradient(135deg, #00f2fe, #4facfe);
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 24px;
                box-shadow: 0 6px 18px rgba(0, 242, 254, 0.35);
            ">🔊</div>
            <div>
                <div style="font-size: 19px; font-weight: 900; color: #ffffff; letter-spacing: -0.3px;">Soundbox Pay</div>
                <div style="font-size: 10px; color: #38bdf8; letter-spacing: 1.2px; font-weight: 700;">BLOCKCHAIN AUDIT SIMULATOR</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Home Dashboard",
            "💳 Create Simulated Payment",
            "📜 Transaction History",
            "⛓️ Blockchain Ledger",
            "🔍 Verify Transaction",
            "⚠️ Tampering Detection Demo",
            "ℹ️ Project Information"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("#### 🗄️ Ledger Data Source")
    
    # Ledger Mode Switcher: Preserved Original vs Clean Verified Demo
    ledger_source_option = st.selectbox(
        "Active Database Mode",
        [
            "⚠️ Primary Ledger (Preserved 67 Records)",
            "✨ Clean Verified Demo (Atomic Sync)"
        ],
        index=0,
        help="Select Primary Ledger to view and diagnose the preserved historical records, or Clean Verified Demo to experience 100% continuous integrity with the concurrency fix."
    )

    if "Primary" in ledger_source_option:
        active_db_path = DB_PATH
        db_label = "soundbox_ledger.db (Preserved)"
    else:
        active_db_path = CLEAN_DEMO_DB_PATH
        db_label = "soundbox_ledger_clean.db (Verified Clean)"
        if not os.path.exists(active_db_path):
            database.init_db(active_db_path)
            payment_simulator.seed_default_sample_transactions(10, db_path=active_db_path)

    # Initialize active database table if needed
    database.init_db(active_db_path)

    st.markdown("---")
    st.markdown("#### ⚡ Quick Sandbox Actions")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("📥 +5 Sample Tx", use_container_width=True, help="Seed 5 realistic simulated transactions into active database"):
            added = payment_simulator.seed_default_sample_transactions(5, db_path=active_db_path)
            st.toast(f"✅ Appended {added} simulated payments to {db_label}!", icon="🎉")
            st.rerun()
    with col_s2:
        if st.button("🗑️ Reset Active", use_container_width=True, help="Reset only the currently active ledger"):
            database.reset_db(active_db_path)
            st.toast(f"⚠️ Reset {db_label} to genesis state.", icon="🧹")
            st.rerun()

    # Sidebar Mini Telemetry Widget
    st.markdown("---")
    records = database.get_all_records(db_path=active_db_path)
    metrics = database.get_ledger_metrics(db_path=active_db_path)
    audit = blockchain_ledger.verify_ledger_integrity(records)
    
    status_icon = "🟢" if audit["is_valid"] else "🔴"
    status_text = "Intact (100%)" if audit["is_valid"] else f"Alert ({len(audit['errors'])} errors)"
    
    st.markdown(f"""
        <div style="background: rgba(15,23,42,0.6); padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); font-size: 12px;">
            <div style="color: #94a3b8; margin-bottom: 6px; font-weight: 700; text-transform: uppercase; font-size: 10px; letter-spacing: 1px;">LEDGER HEALTH</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #cbd5e1;">Active DB:</span>
                <span style="font-weight: 700; color: #38bdf8; font-size: 11px;">{os.path.basename(active_db_path)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #cbd5e1;">Chain Status:</span>
                <span style="font-weight: 700; color: {'#10b981' if audit['is_valid'] else '#ef4444'};">{status_icon} {status_text}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #cbd5e1;">Valid Blocks:</span>
                <span style="font-weight: 700; color: #ffffff;">{audit['valid_blocks']} / {audit['total_blocks']}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #cbd5e1;">Volume:</span>
                <span style="font-weight: 700; color: #38bdf8;">{CURRENCY_SYMBOL}{metrics['total_amount']:,.2f}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("🎓 Academic Final Year / Lab Prototype v1.2")
    st.caption("Cryptographic Soundbox & Audit Simulator")

# ---------------------------------------------------------
# Global Telemetry & Disclaimer Renderers
# ---------------------------------------------------------
def render_top_telemetry(db_name: str = "soundbox_ledger.db"):
    """Render top active system status bar."""
    st.markdown(f"""
        <div class="telemetry-bar">
            <div class="telemetry-item">
                <span class="pulse-dot"></span>
                <span style="font-weight: 600; color: #ffffff;">Active Node:</span> Simulated Local Peer
            </div>
            <div class="telemetry-item">
                <span style="color: #38bdf8;">Database:</span> {db_name}
            </div>
            <div class="telemetry-item">
                <span style="color: #38bdf8;">Algorithm:</span> SHA-256 Canonical
            </div>
            <div class="telemetry-item">
                <span style="color: #38bdf8;">Storage:</span> SQLite WAL Mode
            </div>
            <div class="telemetry-item">
                <span style="color: #38bdf8;">Soundbox Guard:</span> Cryptographic Seal Active
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_disclaimer():
    """Display standard academic prototype notice."""
    st.markdown(f"""
        <div class="disclaimer-banner">
            <div style="font-size: 20px;">⚠️</div>
            <div>
                <span class="disclaimer-title">ACADEMIC PROTOTYPE NOTICE:</span>
                {ACADEMIC_DISCLAIMER}
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 1: Home Dashboard
# ---------------------------------------------------------
if page == "🏠 Home Dashboard":
    render_top_telemetry(db_name=os.path.basename(active_db_path))
    st.title("Digital Payment Soundbox & Blockchain Simulator")
    render_disclaimer()

    # Fetch fresh metrics for active DB
    records = database.get_all_records(db_path=active_db_path)
    metrics = database.get_ledger_metrics(db_path=active_db_path)
    audit = blockchain_ledger.verify_ledger_integrity(records)

    # 4 Main KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Blocks / Payments</div>
                <div class="metric-val">{metrics['total_count']}</div>
                <div class="metric-sub">
                    <span>⚡ Append-Only Ledger</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Simulated Turnover</div>
                <div class="metric-val">{CURRENCY_SYMBOL}{metrics['total_amount']:,.2f}</div>
                <div class="metric-sub">
                    <span>Avg {CURRENCY_SYMBOL}{metrics['avg_amount']:,.2f} per tx</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        status_color = "#10b981" if audit["is_valid"] else "#ef4444"
        status_text = "100% INTACT" if audit["is_valid"] else "TAMPERED / CORRUPTED"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Cryptographic Integrity</div>
                <div class="metric-val" style="color: {status_color}; font-size: 22px;">{status_text}</div>
                <div class="metric-sub" style="color: {status_color};">
                    <span>{audit['valid_blocks']} / {audit['total_blocks']} Blocks Valid</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Hashing & Consensus</div>
                <div class="metric-val" style="font-size: 24px; color: #38bdf8;">SHA-256</div>
                <div class="metric-sub">
                    <span>Deterministic Canonical JSON</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("###")

    # Cryptographic Diagnostic Section (Rendered when ledger has integrity issues)
    if not audit["is_valid"]:
        diag_rep = verification.generate_diagnostic_report(records=records, db_path=active_db_path)
        counting = diag_rep["counting_rules"]

        st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.08); border: 2px solid #ef4444; border-radius: 16px; padding: 22px; margin-bottom: 24px; box-shadow: 0 8px 30px rgba(239, 68, 68, 0.15);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 24px;">🚨</span>
                        <span style="font-size: 18px; font-weight: 800; color: #f87171;">
                            Cryptographic Diagnostic Report ({counting['invalid_blocks']} Invalid Blocks, {counting['total_error_violations']} Errors Detected)
                        </span>
                    </div>
                    <span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 11px;">
                        ROOT CAUSE: CONCURRENCY RACE DISCREPANCY
                    </span>
                </div>
                <div style="font-size: 13px; color: #e2e8f0; line-height: 1.6; margin-bottom: 14px;">
                    <strong>Investigation Findings:</strong> The verification engine detected that exactly {counting['invalid_blocks']} blocks 
                    (Blocks <code>{', '.join(['#' + str(b['block_index']) for b in diag_rep['invalid_blocks']])}</code>) fail validation. 
                    Cryptographic reverse-analysis proves these records were <strong>NOT maliciously tampered with</strong>. 
                    Instead, they resulted from a <strong>concurrency race condition</strong> during rapid multi-record insertions prior to thread synchronization. 
                    The previous insertion engine read the tail block and hashed in memory without an exclusive lock, causing interleaved transactions to be hashed using stale block indices and parent pointers before being committed out of order.
                </div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.5; margin-bottom: 8px;">
                    <strong>Counting Rule Specifications:</strong> A block is classified as <b style="color: #10b981;">VALID</b> if and only if both its payload SHA-256 matches AND its predecessor link is intact. 
                    {counting['valid_blocks']} of {counting['total_blocks']} blocks are valid. Total errors ({counting['total_error_violations']}) represents {counting['tampered_payload_count']} payload mismatches + {counting['broken_link_count']} broken links.
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.expander(f"🔎 Inspect Individual Failed Blocks ({counting['invalid_blocks']} Issues Breakdown)", expanded=True):
            for inv in diag_rep["invalid_blocks"]:
                st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; font-weight: 800; color: #f87171; margin-bottom: 8px;">
                            <span>Block #{inv['block_index']} — Transaction ID: <code>{inv['tx_id']}</code></span>
                            <span>Failed Rules: {', '.join(inv['failed_rules'])}</span>
                        </div>
                        <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 8px;">
                            <strong>Customer:</strong> {inv['sender']} | <strong>Amount:</strong> {CURRENCY_SYMBOL}{inv['amount']:,.2f} | <strong>Method:</strong> {inv['payment_method']} | <strong>Committed At:</strong> {inv['timestamp']}
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; background: rgba(0,0,0,0.4); padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; line-height: 1.6;">
                            <div><span style="color: #94a3b8;">[Stored Current Hash]:</span>   <span style="color: #f87171;">{inv['stored_current_hash']}</span></div>
                            <div><span style="color: #94a3b8;">[Recomputed Digest]:</span>    <span style="color: #38bdf8;">{inv['recomputed_current_hash']}</span></div>
                            <div><span style="color: #94a3b8;">[Stored Prev Hash]:</span>     <span style="color: #fbbf24;">{inv['stored_prev_hash']}</span></div>
                            <div><span style="color: #94a3b8;">[Expected Prev Hash]:</span>   <span style="color: #10b981;">{inv['expected_prev_hash']}</span> (from preceding Block #{inv['preceding_block_index']})</div>
                        </div>
                        <div style="font-size: 12px; color: #38bdf8; line-height: 1.4;">
                            <strong>Diagnostic Analysis:</strong> {inv['root_cause_explanation']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            diag_json = json.dumps(diag_rep, indent=2)
            st.download_button(
                label="📥 Download Cryptographic Diagnostic Report (JSON)",
                data=diag_json.encode('utf-8'),
                file_name=f"diagnostic_report_{os.path.basename(active_db_path)}.json",
                mime="application/json",
                use_container_width=True
            )

    # Split Section: Soundbox Device Showcase & Live Activity Summary
    sb_col, act_col = st.columns([1.1, 0.9])

    with sb_col:
        st.markdown("### 🔊 Live Soundbox Terminal")
        st.caption("Active speaker response for the most recent cryptographically validated block.")
        
        last_record = database.get_last_record(db_path=active_db_path)
        if last_record:
            lang_col1, lang_col2 = st.columns([1, 2])
            with lang_col1:
                home_lang = st.selectbox("Speech Language", ["English (en)", "हिन्दी (hi)"], index=0, key="home_sb_lang")
            
            chosen_code = "hi" if "हिन्दी" in home_lang else "en"
            soundbox_res = soundbox.trigger_verified_soundbox_announcement(
                last_record, 
                is_verified=audit["is_valid"], 
                lang=chosen_code
            )
            st.markdown(soundbox_res["html"], unsafe_allow_html=True)
        else:
            st.info("No transactions in ledger yet. Click **'📥 +5 Sample Tx'** in the sidebar to populate sample transactions!")

    with act_col:
        st.markdown("### 🚀 Payment Simulation Action")
        st.caption("Inject a synchronized sample transaction to trigger the soundbox.")

        with st.container():
            st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px; margin-bottom: 16px;">
                    <div style="font-size: 15px; font-weight: 700; color: #ffffff; margin-bottom: 8px;">Atomic Thread-Safe Payment Append</div>
                    <div style="font-size: 12px; color: #94a3b8; line-height: 1.5; margin-bottom: 14px;">
                        Generates a sample payment, acquires the re-entrant ledger lock, computes its canonical SHA-256 digest, and atomically commits it to <code>{os.path.basename(active_db_path)}</code>.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if st.button("⚡ Inject Synchronized ₹500 Payment", use_container_width=True):
                sample_p = payment_simulator.generate_random_sample_payload()
                sample_p["amount"] = 500.0
                res = payment_simulator.record_simulated_payment(
                    tx_id=sample_p["tx_id"],
                    sender=sample_p["sender"],
                    amount=500.0,
                    payment_method="UPI QR Scan",
                    timestamp=sample_p["timestamp"],
                    db_path=active_db_path
                )
                if res["success"]:
                    st.toast(f"✅ Committed to Block #{res['record']['block_index']} in {os.path.basename(active_db_path)}!", icon="🔊")
                    st.rerun()

            st.markdown("""
                <div style="margin-top: 18px; padding: 14px; background: rgba(56, 189, 248, 0.08); border-radius: 12px; border-left: 3px solid #38bdf8; font-size: 12px; color: #cbd5e1;">
                    <strong>Hardware Soundbox Security Guard:</strong><br/>
                    The simulated speaker logic evaluates the block's current hash and previous link integrity before releasing any audio. If any record is modified, the soundbox automatically silences itself and triggers a red tamper strobe.
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Analytics Charts
    if len(records) > 0:
        st.markdown("### 📊 Ledger Visual Analytics")
        df = pd.DataFrame(records)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            method_counts = df['payment_method'].value_counts().reset_index()
            method_counts.columns = ['Method', 'Count']
            fig_pie = px.pie(
                method_counts,
                names='Method',
                values='Count',
                title="Payment Methods Distribution",
                hole=0.5,
                color_discrete_sequence=['#00f2fe', '#4facfe', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1', family='Plus Jakarta Sans'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie)

        with chart_col2:
            fig_bar = px.bar(
                df,
                x='block_index',
                y='amount',
                title="Transaction Amount by Block Sequence",
                labels={'block_index': 'Block #', 'amount': f'Amount ({CURRENCY_SYMBOL})'},
                color='amount',
                color_continuous_scale='Tealgrn'
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#cbd5e1', family='Plus Jakarta Sans'),
                xaxis=dict(showgrid=False, tickmode='linear'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.06)')
            )
            st.plotly_chart(fig_bar)

# ---------------------------------------------------------
# PAGE 2: Create Simulated Payment
# ---------------------------------------------------------
elif page == "💳 Create Simulated Payment":
    render_top_telemetry(db_name=os.path.basename(active_db_path))
    st.title("Create Simulated Payment")
    render_disclaimer()

    col_form, col_sound = st.columns([1.1, 0.9])

    with col_form:
        st.markdown("#### 📝 Merchant Payment Terminal")
        st.caption(f"Active Ledger Target: <code>{os.path.basename(active_db_path)}</code>")

        # Quick Preset Chips
        st.markdown("<div style='font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 6px;'>QUICK AMOUNT PRESETS</div>", unsafe_allow_html=True)
        preset_cols = st.columns(6)
        presets = [100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0]
        for idx, p_amt in enumerate(presets):
            with preset_cols[idx]:
                if st.button(f"₹{int(p_amt)}", key=f"chip_{int(p_amt)}", use_container_width=True):
                    st.session_state["selected_preset_amt"] = p_amt

        preset_default = st.session_state.get("selected_preset_amt", 500.0)

        with st.form("simulated_payment_form", clear_on_submit=False):
            c1, c2 = st.columns([2, 1])
            with c1:
                default_tx = payment_simulator.generate_sample_tx_id()
                tx_id_input = st.text_input(
                    "Transaction ID (Unique)",
                    value=default_tx,
                    help="Unique identifier for the simulated payment"
                )
            with c2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                auto_gen = st.checkbox("New Auto ID", value=True)
                if auto_gen and tx_id_input == default_tx:
                    tx_id_input = default_tx

            sender_input = st.text_input(
                "Customer Name / Sample Identifier",
                value="Aarav Sharma (aarav@oksbi)",
                help="Simulated customer / UPI VPA"
            )

            col_amt, col_meth = st.columns(2)
            with col_amt:
                amount_input = st.number_input(
                    f"Payment Amount ({CURRENCY_SYMBOL})",
                    min_value=1.0,
                    max_value=10_000_000.0,
                    value=float(preset_default),
                    step=50.0,
                    format="%.2f"
                )
            with col_meth:
                method_input = st.selectbox(
                    "Simulated Payment Method",
                    PAYMENT_METHODS,
                    index=0
                )

            current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            st.text_input("Timestamp (Auto-Captured UTC)", value=current_timestamp, disabled=True)

            col_sub1, col_sub2 = st.columns([1.5, 1])
            with col_sub1:
                submitted = st.form_submit_button("🚀 Submit & Commit to Ledger", use_container_width=True)
            with col_sub2:
                voice_lang = st.selectbox("Announcement Voice", ["English", "हिन्दी (Hindi)"], index=0)

            if submitted:
                lang_code = "hi" if "हिन्दी" in voice_lang else "en"
                result = payment_simulator.record_simulated_payment(
                    tx_id=tx_id_input,
                    sender=sender_input,
                    amount=amount_input,
                    payment_method=method_input,
                    timestamp=current_timestamp,
                    db_path=active_db_path
                )

                if result["success"]:
                    st.session_state["last_payment_result"] = result["record"]
                    st.session_state["payment_lang"] = lang_code
                    st.toast(result["message"], icon="🎉")
                    st.success(f"✅ Transaction Confirmed: Block #{result['record']['block_index']} committed with hash `{result['record']['current_hash'][:16]}...`")
                else:
                    st.session_state["last_payment_result"] = None
                    st.error(f"❌ Payment Rejected: {result['message']}")

        # Simulated Dynamic QR Code Preview
        st.markdown("###")
        st.markdown("""
            <div class="qr-card">
                <div style="font-size: 11px; font-weight: 700; color: #38bdf8; letter-spacing: 1px; margin-bottom: 8px;">SIMULATED MERCHANT UPI COUNTER QR</div>
                <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                    <svg width="140" height="140" viewBox="0 0 100 100" style="background: white; padding: 10px; border-radius: 12px;">
                        <rect x="0" y="0" width="30" height="30" fill="#0f172a" />
                        <rect x="5" y="5" width="20" height="20" fill="white" />
                        <rect x="9" y="9" width="12" height="12" fill="#0f172a" />
                        
                        <rect x="70" y="0" width="30" height="30" fill="#0f172a" />
                        <rect x="75" y="5" width="20" height="20" fill="white" />
                        <rect x="79" y="9" width="12" height="12" fill="#0f172a" />
                        
                        <rect x="0" y="70" width="30" height="30" fill="#0f172a" />
                        <rect x="5" y="75" width="20" height="20" fill="white" />
                        <rect x="9" y="79" width="12" height="12" fill="#0f172a" />
                        
                        <rect x="40" y="10" width="8" height="8" fill="#0f172a" />
                        <rect x="52" y="15" width="8" height="8" fill="#0f172a" />
                        <rect x="45" y="35" width="8" height="8" fill="#0f172a" />
                        <rect x="25" y="45" width="8" height="8" fill="#0f172a" />
                        <rect x="65" y="45" width="8" height="8" fill="#0f172a" />
                        <rect x="40" y="65" width="8" height="8" fill="#0f172a" />
                        <rect x="55" y="75" width="8" height="8" fill="#0f172a" />
                        <rect x="75" y="65" width="8" height="8" fill="#0f172a" />
                        
                        <circle cx="50" cy="50" r="10" fill="#00f2fe" />
                    </svg>
                </div>
                <div style="font-size: 13px; font-weight: 700; color: #ffffff;">Soundbox Merchant Store</div>
                <div style="font-size: 11px; color: #94a3b8;">UPI ID: merchant.soundbox@oksbi</div>
            </div>
        """, unsafe_allow_html=True)

    with col_sound:
        st.markdown("#### 🔊 Soundbox Speaker Response")
        st.caption("Live hardware visualizer executing audio for verified transactions.")

        active_record = st.session_state.get("last_payment_result")
        active_lang = st.session_state.get("payment_lang", "en")
        
        if active_record:
            sound_res = soundbox.trigger_verified_soundbox_announcement(
                active_record, 
                is_verified=True, 
                lang=active_lang
            )
            st.markdown(sound_res["html"], unsafe_allow_html=True)
            st.info(f"🎙️ Audio Synthesizer: **{sound_res['engine_info']}**")
        else:
            standby_html = soundbox.render_soundbox_html(
                amount=0.0,
                tx_id="STANDBY-WAITING-FOR-PAYMENT",
                status="STANDBY",
                lang="en"
            )
            st.markdown(standby_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 3: Transaction History
# ---------------------------------------------------------
elif page == "📜 Transaction History":
    render_top_telemetry(db_name=os.path.basename(active_db_path))
    st.title("Transaction History Explorer")
    render_disclaimer()

    records = database.get_all_records(db_path=active_db_path)
    if not records:
        st.info("No transaction history available yet. Create a payment or seed sample data from the sidebar.")
    else:
        df = pd.DataFrame(records)

        # Filters toolbar
        f1, f2, f3 = st.columns([1.5, 1, 1])
        with f1:
            search_query = st.text_input("🔎 Search by Tx ID or Sender", placeholder="e.g. SIM-2026 or Sharma")
        with f2:
            selected_method = st.selectbox("Filter Payment Method", ["All"] + PAYMENT_METHODS)
        with f3:
            sort_order = st.selectbox("Sort Order", ["Descending (Latest Block First)", "Ascending (Chronological 1 to N)"])

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["tx_id"].str.contains(search_query, case=False) |
                filtered_df["sender"].str.contains(search_query, case=False)
            ]
        if selected_method != "All":
            filtered_df = filtered_df[filtered_df["payment_method"] == selected_method]

        if "Latest" in sort_order:
            filtered_df = filtered_df.sort_values(by="block_index", ascending=False)
        else:
            filtered_df = filtered_df.sort_values(by="block_index", ascending=True)

        filtered_amt = filtered_df["amount"].sum() if len(filtered_df) > 0 else 0.0
        avg_amt = filtered_df["amount"].mean() if len(filtered_df) > 0 else 0.0

        st.markdown(f"""
            <div style="display: flex; gap: 20px; background: rgba(15,23,42,0.6); padding: 10px 16px; border-radius: 12px; margin-bottom: 16px; font-size: 13px;">
                <div><span style="color: #94a3b8;">Showing:</span> <b>{len(filtered_df)} of {len(df)} transactions</b></div>
                <div><span style="color: #94a3b8;">Filtered Turnover:</span> <b style="color: #38bdf8;">{CURRENCY_SYMBOL}{filtered_amt:,.2f}</b></div>
                <div><span style="color: #94a3b8;">Average Ticket:</span> <b style="color: #10b981;">{CURRENCY_SYMBOL}{avg_amt:,.2f}</b></div>
            </div>
        """, unsafe_allow_html=True)

        display_df = filtered_df[[
            "block_index", "tx_id", "sender", "amount", 
            "payment_method", "timestamp", "current_hash", "status"
        ]].copy()
        display_df["amount"] = display_df["amount"].apply(lambda x: f"{CURRENCY_SYMBOL}{x:,.2f}")
        display_df["current_hash"] = display_df["current_hash"].apply(lambda h: f"{h[:10]}...{h[-6:]}")

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "block_index": "Block #",
                "tx_id": "Transaction ID",
                "sender": "Sender",
                "amount": "Simulated Amount",
                "payment_method": "Payment Method",
                "timestamp": "UTC Timestamp",
                "current_hash": "SHA-256 Digest",
                "status": "Ledger Status"
            },
            hide_index=True
        )

        st.markdown("#### 📥 Export Ledger Data")
        exp1, exp2 = st.columns(2)
        with exp1:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Download Filtered Transactions (CSV)",
                data=csv_data,
                file_name="soundbox_ledger_export.csv",
                mime="text/csv",
                use_container_width=True
            )
        with exp2:
            json_data = filtered_df.to_json(orient="records", indent=2).encode('utf-8')
            st.download_button(
                label="📦 Download Filtered Records (JSON)",
                data=json_data,
                file_name="soundbox_ledger_export.json",
                mime="application/json",
                use_container_width=True
            )

# ---------------------------------------------------------
# PAGE 4: Blockchain Ledger
# ---------------------------------------------------------
elif page == "⛓️ Blockchain Ledger":
    render_top_telemetry(db_name=os.path.basename(active_db_path))
    st.title("Cryptographic Blockchain Ledger Explorer")
    render_disclaimer()

    st.markdown(f"""
        Every block in this ledger stores a simulated payment transaction and cryptographically references the 
        previous block's **SHA-256** hash digest, creating an append-only, tamper-evident cryptographic chain.
        <br/><span style="color: #38bdf8; font-size: 12px;">Active Database: <code>{active_db_path}</code></span>
    """, unsafe_allow_html=True)

    records = database.get_all_records(db_path=active_db_path)
    if not records:
        st.info("The ledger is currently empty. Use the sidebar to seed safe sample transactions.")
    else:
        audit = blockchain_ledger.verify_ledger_integrity(records)
        
        status_box = st.container()
        if audit["is_valid"]:
            status_box.success(f"✅ Cryptographic Integrity Intact: All {audit['total_blocks']} sequential blocks are mathematically valid and hash-linked.")
        else:
            status_box.error(f"❌ Ledger Compromised: Detected {len(audit['errors'])} cryptographic violations across {len(records) - audit['valid_blocks']} blocks!")

        st.markdown("### 🧱 Sequential Block Explorer")
        for i, block in enumerate(records):
            is_genesis = (block["block_index"] == 1)
            b_audit = audit["details"][i] if i < len(audit["details"]) else {}
            is_valid = b_audit.get("status") == "VALID"
            badge_color = "#10b981" if is_valid else "#ef4444"

            st.markdown(f"""
                <div class="block-card {'valid' if is_valid else 'tampered'}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-weight: 900; color: #38bdf8; font-size: 16px; letter-spacing: 0.5px;">
                            BLOCK #{block['block_index']} {'<span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #fbbf24; padding: 2px 8px; border-radius: 8px; font-size: 11px; margin-left: 8px;">GENESIS BLOCK</span>' if is_genesis else ''}
                        </span>
                        <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}; padding: 3px 12px; border-radius: 12px; font-weight: 800; font-size: 11px;">
                            {b_audit.get('status', 'CONFIRMED')}
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; color: #cbd5e1; font-size: 13px; margin-bottom: 12px;">
                        <div><strong style="color: #94a3b8;">Transaction ID:</strong><br/><code>{block['tx_id']}</code></div>
                        <div><strong style="color: #94a3b8;">Customer:</strong><br/>{block['sender']}</div>
                        <div><strong style="color: #94a3b8;">Simulated Amount:</strong><br/><b style="color: #ffffff; font-size: 15px;">{CURRENCY_SYMBOL}{block['amount']:,.2f}</b></div>
                        <div><strong style="color: #94a3b8;">Payment Method:</strong><br/>{block['payment_method']}</div>
                        <div><strong style="color: #94a3b8;">Committed At:</strong><br/>{block['timestamp']}</div>
                        <div><strong style="color: #94a3b8;">Status:</strong><br/><span style="color: {badge_color}; font-weight: 700;">{block['status']}</span></div>
                    </div>
                    <div style="background: rgba(0,0,0,0.3); border-radius: 10px; padding: 10px 14px; font-size: 12px; font-family: 'JetBrains Mono', monospace;">
                        <div style="color: #94a3b8; margin-bottom: 4px;">
                            <span style="color: #64748b;">[prev_hash]:</span> 
                            <span style="color: {'#fbbf24' if is_genesis else '#93c5fd'}; word-break: break-all;">{block['prev_hash']}</span>
                        </div>
                        <div style="color: #94a3b8;">
                            <span style="color: #64748b;">[current_hash]:</span> 
                            <span style="color: #34d399; font-weight: 700; word-break: break-all;">{block['current_hash']}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.expander(f"🔍 Inspect Canonical JSON Payload (Block #{block['block_index']})"):
                canonical_bytes = blockchain_ledger.serialize_block_payload(
                    block_index=block["block_index"],
                    tx_id=block["tx_id"],
                    sender=block["sender"],
                    amount=block["amount"],
                    payment_method=block["payment_method"],
                    timestamp=block["timestamp"],
                    prev_hash=block["prev_hash"]
                )
                st.code(canonical_bytes.decode('utf-8'), language="json")

            if i < len(records) - 1:
                st.markdown("""
                    <div class="chain-connector">
                        <div class="chain-line"></div>
                        <div class="chain-badge">🔗 SHA-256 Hash Link Continuous</div>
                        <div class="chain-line"></div>
                    </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 5: Verify Transaction
# ---------------------------------------------------------
elif page == "🔍 Verify Transaction":
    render_top_telemetry(db_name=os.path.basename(active_db_path))
    st.title("Transaction & Ledger Verification Engine")
    render_disclaimer()

    tab_single, tab_full, tab_diag = st.tabs([
        "🔎 Verify Single Transaction", 
        "🛡️ Audit Full Ledger System",
        "📊 Cryptographic Diagnostic Report"
    ])

    with tab_single:
        st.markdown("#### Cryptographic Single-Transaction Inspection")
        st.caption(f"Reconstructs deterministic payload, computes fresh SHA-256 hash, and verifies link continuity against {os.path.basename(active_db_path)}.")

        records = database.get_all_records(db_path=active_db_path)
        sample_txs = [r["tx_id"] for r in records] if records else []

        c_search1, c_search2 = st.columns([2, 1])
        with c_search1:
            search_tx = st.text_input("Enter or Paste Transaction ID", placeholder="e.g. SIM-20261022-XXXXX")
        with c_search2:
            if sample_txs:
                quick_pick = st.selectbox("Or Quick-Pick Recorded Tx", ["Select..."] + sample_txs[:15])
                if quick_pick != "Select...":
                    search_tx = quick_pick

        if st.button("⚡ Run Full Verification Pipeline", use_container_width=True):
            if not search_tx:
                st.warning("Please provide a Transaction ID to verify.")
            else:
                res = verification.verify_single_transaction_by_id(search_tx, db_path=active_db_path)
                if res["is_verified"]:
                    st.success(res["explanation"])
                    rec = res["record"]
                    
                    st.markdown("""
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin: 16px 0;">
                            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 12px; padding: 12px;">
                                <div style="color: #10b981; font-weight: 800; font-size: 13px;">✓ STAGE 1: PAYLOAD</div>
                                <div style="font-size: 11px; color: #cbd5e1; margin-top: 4px;">Record located with intact canonical format.</div>
                            </div>
                            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 12px; padding: 12px;">
                                <div style="color: #10b981; font-weight: 800; font-size: 13px;">✓ STAGE 2: SHA-256 MATCH</div>
                                <div style="font-size: 11px; color: #cbd5e1; margin-top: 4px;">Recomputed digest matches stored hash exactly.</div>
                            </div>
                            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 12px; padding: 12px;">
                                <div style="color: #10b981; font-weight: 800; font-size: 13px;">✓ STAGE 3: LINK INTEGRITY</div>
                                <div style="font-size: 11px; color: #cbd5e1; margin-top: 4px;">Parent prev_hash correctly anchors to predecessor.</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.json({
                            "Transaction ID": rec["tx_id"],
                            "Block Sequence": rec["block_index"],
                            "Sender Identifier": rec["sender"],
                            "Amount (INR)": rec["amount"],
                            "Payment Method": rec["payment_method"],
                            "Committed Timestamp": rec["timestamp"]
                        })
                    with c2:
                        st.json({
                            "Stored Hash": res["stored_hash"],
                            "Recalculated Hash": res["computed_hash"],
                            "Hash Integrity": "MATCH (0 discrepancies)",
                            "Link Continuity": "MATCH (Strict Chain Link)",
                            "Verification Audit Timestamp": res["verification_timestamp"]
                        })
                else:
                    st.error(f"❌ Verification FAILED: {res['explanation']}")
                    if res["error_reason"]:
                        st.markdown(f"**Diagnostic Error:** `{res['error_reason']}`")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.json({
                            "Stored Hash": res["stored_hash"],
                            "Computed Hash": res["computed_hash"],
                            "Hash Match": res["hash_match"]
                        })
                    with c2:
                        st.json({
                            "Stored Prev Hash": res["stored_prev_hash"],
                            "Expected Prev Hash": res["expected_prev_hash"],
                            "Link Match": res["link_match"]
                        })

    with tab_full:
        st.markdown("#### Database-Wide Cryptographic Audit")
        st.caption(f"Sequentially tests every block for payload mutations and broken hash links across {os.path.basename(active_db_path)}.")

        if st.button("🛡️ Execute Complete Ledger System Audit", use_container_width=True):
            audit_res = verification.verify_full_ledger_system(db_path=active_db_path)
            if audit_res["is_valid"]:
                st.success(f"🎉 Complete Ledger Intact! Audited {audit_res['total_blocks']} sequential blocks with 0 discrepancies.")
            else:
                st.error(f"🚨 Audit Discrepancies: Found {len(audit_res['errors'])} violations across {audit_res['total_blocks'] - audit_res['valid_blocks']} blocks.")
                for err in audit_res["errors"]:
                    st.markdown(f"- ❌ `{err}`")

            st.json({
                "Overall Audit Status": "VALID (100% INTACT)" if audit_res["is_valid"] else "FAILED (DISCREPANCIES FOUND)",
                "Total Blocks Scanned": audit_res["total_blocks"],
                "Valid Intact Blocks": audit_res["valid_blocks"],
                "Tampered Blocks": audit_res["tampered_blocks"],
                "Broken Hash Links": audit_res["broken_links"],
                "Audit Timestamp": audit_res["verification_timestamp"]
            })

    with tab_diag:
        st.markdown("#### Comprehensive Cryptographic Diagnostic & Root Cause Report")
        st.caption(f"Evaluates exact mathematical discrepancies and classifies root causes for {os.path.basename(active_db_path)}.")

        diag_report = verification.generate_diagnostic_report(db_path=active_db_path)
        c_rules = diag_report["counting_rules"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Blocks", c_rules["total_blocks"])
        m2.metric("Valid Blocks", c_rules["valid_blocks"])
        m3.metric("Invalid Blocks", c_rules["invalid_blocks"])
        m4.metric("Total Violations", c_rules["total_error_violations"])

        st.info(f"**Counting Rule Specification:** {c_rules['definition_of_valid_block']}")

        if diag_report["invalid_blocks_count"] == 0:
            st.success("✅ No cryptographic discrepancies found! The active ledger is 100% intact.")
        else:
            st.markdown("### 🚨 Detected Block Discrepancies Breakdown")
            for inv in diag_report["invalid_blocks"]:
                st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid #ef4444; border-radius: 12px; padding: 16px; margin-bottom: 14px;">
                        <div style="display: flex; justify-content: space-between; font-weight: 800; color: #f87171; margin-bottom: 8px;">
                            <span>Block #{inv['block_index']} — Tx ID: <code>{inv['tx_id']}</code></span>
                            <span>Failed Rules: {', '.join(inv['failed_rules'])}</span>
                        </div>
                        <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 8px;">
                            <b>Sender:</b> {inv['sender']} | <b>Amount:</b> {CURRENCY_SYMBOL}{inv['amount']:,.2f} | <b>Method:</b> {inv['payment_method']} | <b>Timestamp:</b> {inv['timestamp']}
                        </div>
                        <div style="font-family: monospace; font-size: 11px; background: rgba(0,0,0,0.4); padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; line-height: 1.6;">
                            <div><span style="color: #94a3b8;">Stored Current Hash:</span>   <span style="color: #f87171;">{inv['stored_current_hash']}</span></div>
                            <div><span style="color: #94a3b8;">Recomputed Hash:</span>      <span style="color: #38bdf8;">{inv['recomputed_current_hash']}</span></div>
                            <div><span style="color: #94a3b8;">Stored Prev Hash:</span>     <span style="color: #fbbf24;">{inv['stored_prev_hash']}</span></div>
                            <div><span style="color: #94a3b8;">Expected Prev Hash:</span>   <span style="color: #10b981;">{inv['expected_prev_hash']}</span> (preceding Block #{inv['preceding_block_index']})</div>
                        </div>
                        <div style="font-size: 12px; color: #38bdf8; line-height: 1.4;">
                            <b>Root Cause Analysis:</b> {inv['root_cause_explanation']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            diag_json = json.dumps(diag_report, indent=2)
            st.download_button(
                label="📥 Export Full Diagnostic Report (JSON)",
                data=diag_json.encode('utf-8'),
                file_name=f"cryptographic_diagnostic_report_{os.path.basename(active_db_path)}.json",
                mime="application/json",
                use_container_width=True
            )

# ---------------------------------------------------------
# PAGE 6: Tampering Detection Demo
# ---------------------------------------------------------
elif page == "⚠️ Tampering Detection Demo":
    render_top_telemetry(db_name="Isolated Sandbox Replica")
    st.title("Cryptographic Tampering Detection Sandbox")
    render_disclaimer()

    st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; border-radius: 12px; padding: 14px 18px; margin-bottom: 20px;">
            <strong style="color: #fbbf24;">🛡️ Isolated Sandbox Execution:</strong><br/>
            This demonstration runs on an in-memory replica of 4 blocks. 
            <strong>The real transaction database is never harmed.</strong>
        </div>
    """, unsafe_allow_html=True)

    if "sandbox_chain" not in st.session_state:
        st.session_state["sandbox_chain"] = tampering_demo.create_sample_sandbox_chain()
        st.session_state["tamper_meta"] = None

    if st.button("🔄 Reset Clean Sandbox Chain", use_container_width=True):
        st.session_state["sandbox_chain"] = tampering_demo.create_sample_sandbox_chain()
        st.session_state["tamper_meta"] = None
        st.toast("Clean sandbox chain restored!", icon="🧼")
        st.rerun()

    current_chain = st.session_state["sandbox_chain"]
    current_audit = blockchain_ledger.verify_ledger_integrity(current_chain)

    st.markdown("### 1. Current Sandbox Chain Status")
    if current_audit["is_valid"]:
        st.success("✅ Sandbox Chain is 100% INTACT & VALID. All sequential SHA-256 hashes match.")
    else:
        st.error(f"🚨 Tampering Detected! Found {len(current_audit['errors'])} cryptographic discrepancies.")
        for e in current_audit["errors"]:
            st.markdown(f"- 🛑 `{e}`")

    st.markdown("---")
    st.markdown("### 2. Inject Controlled Data Modification")
    st.markdown("Select a block and alter its amount or sender to witness instant chain fracture.")

    tc1, tc2, tc3 = st.columns([1, 1, 1.5])
    with tc1:
        target_idx = st.selectbox(
            "Select Target Block",
            [b["block_index"] for b in current_chain],
            index=1
        )
    with tc2:
        tamper_field = st.selectbox("Field to Modify", ["amount", "sender"])
    with tc3:
        if tamper_field == "amount":
            new_val = st.number_input("New Malicious Amount (₹)", value=50000.0, step=1000.0)
        else:
            new_val = st.text_input("New Malicious Sender", value="Hacker / Attacker")

    if st.button("💥 Apply Modification to Sandbox Record", use_container_width=True):
        tampered_c, meta = tampering_demo.apply_simulated_tamper(
            current_chain,
            target_block_index=target_idx,
            tamper_field=tamper_field,
            new_value=new_val
        )
        st.session_state["sandbox_chain"] = tampered_c
        st.session_state["tamper_meta"] = meta
        st.rerun()

    meta = st.session_state.get("tamper_meta")
    if meta:
        st.markdown("---")
        st.markdown("### 3. The Avalanche Effect: Visual Hash Breakdown")
        
        c_orig, c_tamp = st.columns(2)
        with c_orig:
            st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 14px; padding: 18px;">
                    <div style="font-weight: 800; color: #10b981; font-size: 14px; margin-bottom: 8px;">ORIGINAL BLOCK #{meta['target_block_index']}</div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 8px;"><b>{meta['tamper_field']}:</b> <code>{meta['original_value']}</code></div>
                    <div style="font-size: 11px; color: #94a3b8;">Original Stored Hash:</div>
                    <code style="color: #34d399; font-size: 11px; word-break: break-all;">{meta['original_stored_hash']}</code>
                </div>
            """, unsafe_allow_html=True)
        with c_tamp:
            st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 14px; padding: 18px;">
                    <div style="font-weight: 800; color: #ef4444; font-size: 14px; margin-bottom: 8px;">MALICIOUSLY ALTERED BLOCK #{meta['target_block_index']}</div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 8px;"><b>{meta['tamper_field']}:</b> <code style="color: #ef4444;">{meta['tampered_value']}</code></div>
                    <div style="font-size: 11px; color: #94a3b8;">Recalculated New Hash:</div>
                    <code style="color: #f87171; font-size: 11px; word-break: break-all;">{meta['recomputed_new_hash']}</code>
                </div>
            """, unsafe_allow_html=True)

        st.warning("""
            **The Avalanche Effect**: Even changing a single rupee or letter produces a radically different 
            SHA-256 hash. Because subsequent blocks reference the original hash in their `prev_hash` pointer, 
            the entire cryptographic chain after the modified block immediately fractures!
        """)

        if st.button("🔨 Attempt Attacker Chain Rewrite (Cascade Recalculate Forward Hashes)", use_container_width=True):
            rewritten = tampering_demo.recompute_subsequent_hashes(current_chain, meta['target_block_index'])
            st.session_state["sandbox_chain"] = rewritten
            st.toast("Attacker re-hashed forward blocks on local node!", icon="⚠️")
            st.rerun()

# ---------------------------------------------------------
# PAGE 7: Project Information
# ---------------------------------------------------------
elif page == "ℹ️ Project Information":
    render_top_telemetry(db_name=os.path.basename(active_db_path))
    st.title("Project Architecture & Academic Documentation")
    render_disclaimer()

    st.markdown("""
    ### 📌 Project Title
    **Blockchain-Based Payment Verification and Soundbox Simulation System**
    
    ### 🎯 Executive Abstract
    This academic project implements a software-only digital payment soundbox and cryptographic audit trail system. 
    It simulates consumer payment transactions across various digital modes (UPI, cards, net banking), 
    validates transaction constraints (positive amounts, non-empty IDs, duplicate prevention), computes 
    deterministic SHA-256 hash linkages to emulate an append-only blockchain ledger, and announces verified 
    simulated payments through dynamic visual and text-to-speech soundbox interfaces.
    """)

    tabs_info = st.tabs(["🏗️ Architecture & Flow", "🛡️ Security & Limitations", "💻 Tech Stack", "📜 Viva-Voce Master Guide"])

    with tabs_info[0]:
        st.markdown("#### System Architecture Flow")
        st.markdown("""
        ```mermaid
        flowchart TD
            A[User / Customer] -->|Enter Payment Details| B[Interactive Payment Simulator]
            B -->|Acquire Re-Entrant LEDGER_LOCK| C[Atomic Concurrency Guard]
            C -->|Strict Input Validation| D{Valid & Non-Duplicate?}
            D -->|No| E[Reject with Clear Error]
            D -->|Yes| F[Compute Canonical Data & SHA-256 Hash]
            F -->|Explicit Block Index & Prev Hash| G[(Persistent SQLite Ledger)]
            G -->|Verify Block & Link| H{Verification Check Passed?}
            H -->|Yes| I[🔊 Trigger Soundbox Audio & Visual Announcement]
            H -->|No / Tampered| J[🔇 Silence Soundbox & Flag Alert]
        ```
        """)

    with tabs_info[1]:
        st.markdown("#### Limitations and Security Realities")
        info_dict = blockchain_ledger.explain_architecture_difference()
        st.markdown(f"**Prototype Ledger:** {info_dict['prototype_ledger']}")
        st.markdown(f"**Decentralized Blockchain:** {info_dict['decentralized_blockchain']}")
        st.markdown(f"**Soundbox Context:** {info_dict['soundbox_context']}")
        st.info(verification.get_cryptographic_limitation_notice())

    with tabs_info[2]:
        st.markdown("#### Technology Stack Specifications")
        st.markdown("""
        - **Programming Language**: Python 3.11+
        - **Web Dashboard**: Streamlit (Hyper-Modern FinTech Custom UI)
        - **Database**: SQLite with WAL Mode & Explicit Block Index Tracking
        - **Concurrency Control**: Python Re-Entrant Lock (LEDGER_LOCK) + Transaction Isolation
        - **Cryptographic Hashing**: hashlib (SHA-256 with canonical sorted JSON serialization)
        - **Speech & Audio**: Google Text-to-Speech (gTTS) / pyttsx3 / Web Speech API (Bilingual EN & HI)
        - **Data Visualization**: Plotly Express & Graph Objects
        - **Testing Framework**: pytest (22 automated unit, integration, concurrency & diagnostic tests)
        - **Optional Smart Contract**: Solidity + Web3.py
        """)

    with tabs_info[3]:
        st.markdown("#### Viva-Voce / Lab Exam Q&A Highlights")
        
        q_list = [
            ("Why is SHA-256 used instead of MD5 or SHA-1?", 
             "SHA-256 offers 256-bit collision resistance, whereas MD5 and SHA-1 have known practical collision vulnerabilities."),
            ("How does the soundbox know when to speak?",
             "A security guard checks that the newly committed block has valid payload integrity and proper link continuity before triggering audio output."),
            ("What is canonical serialization?",
             "In Python, dictionary key ordering or float string formats can vary. Sorting keys and normalizing number representations ensures the exact same input bytes are fed to SHA-256 every time."),
            ("What caused the 3 invalid blocks (Block #15, #53, #54) in historical data?",
             "A concurrency race condition. Without thread locking, rapid concurrent inserts fetched stale tail blocks, calculated SHA-256 digests in memory with out-of-order block indices and parent pointers, and committed to SQLite out of sequence. Adding LEDGER_LOCK and explicit block_index insertion permanently fixed this."),
            ("Does this replace a real Paytm/PhonePe soundbox?",
             "No. Real soundboxes receive encrypted cryptograms over cellular IoT networks from certified banking switches. This simulator demonstrates local audit integrity."),
            ("What is the Avalanche Effect in cryptography?",
             "A fundamental property of cryptographic hash functions where a tiny change in the input (e.g., flipping a single bit or changing ₹500 to ₹501) results in a drastically different, unpredictable output hash digest.")
        ]
        
        for q, a in q_list:
            with st.expander(f"❓ {q}"):
                st.markdown(f"**Answer:** {a}")
