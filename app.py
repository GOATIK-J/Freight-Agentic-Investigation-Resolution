"""F.A.I.R. — 5-Page Streamlit Application."""
import json
import os
import sqlite3
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data.database import init_db, get_connection
from orchestration.controller import WorkflowController
from models.state import InvestigationState

st.set_page_config(page_title="F.A.I.R. — Freight Agentic Investigation & Resolution",
                   page_icon="🚛", layout="wide", initial_sidebar_state="expanded")

# Initialize DB on first run
if not os.path.exists("data/fair_freight.db"):
    init_db()

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 28px; font-weight: 700; color: #1a2744; }
    .sub-header { font-size: 18px; font-weight: 600; color: #2c3e50; }
    .badge-low { background-color: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
    .badge-medium { background-color: #fd7e14; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
    .badge-high { background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
    .badge-critical { background-color: #721c24; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
    .agent-card { background-color: #f8f9fa; border-left: 4px solid #1a2744; padding: 12px; margin: 8px 0; border-radius: 4px; }
    .agent-complete { border-left-color: #28a745; }
    .agent-active { border-left-color: #fd7e14; }
    .agent-error { border-left-color: #dc3545; }
    .evidence-found { color: #28a745; font-weight: 600; }
    .evidence-missing { color: #dc3545; font-weight: 600; }
    .metric-box { background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; padding: 16px; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<div class='main-header'>F.A.I.R.</div>", unsafe_allow_html=True)
st.sidebar.caption("Freight Agentic Investigation & Resolution")
page = st.sidebar.radio("Navigation", [
    "Exception Queue",
    "Investigation Console",
    "Resolution & Approval",
    "Operations Dashboard",
    "Audit & Compliance"
])

# Session state
if "investigation_results" not in st.session_state:
    st.session_state.investigation_results = {}
if "human_decisions" not in st.session_state:
    st.session_state.human_decisions = {}


def get_severity_badge(severity: str) -> str:
    return f"<span class='badge-{severity.lower()}'>{severity}</span>"


def load_exceptions(filters: dict = None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM exceptions WHERE 1=1"
    params = []
    if filters:
        if filters.get("type"):
            query += " AND exception_type = ?"
            params.append(filters["type"])
        if filters.get("severity"):
            query += " AND severity = ?"
            params.append(filters["severity"])
        if filters.get("status"):
            query += " AND status = ?"
            params.append(filters["status"])
    query += " ORDER BY reported_at DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_shipment(sid: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shipments WHERE shipment_id = ?", (sid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {}


def run_investigation(case: dict) -> InvestigationState:
    ctrl = WorkflowController()
    raw = {
        "exception_type": case["exception_type"],
        "cargo_value": load_shipment(case["shipment_id"]).get("cargo_value", 0),
        "customer_tier": "Standard",
        "carrier_id": load_shipment(case["shipment_id"]).get("carrier_id", ""),
        "origin": load_shipment(case["shipment_id"]).get("origin", ""),
        "destination": load_shipment(case["shipment_id"]).get("destination", ""),
        "commodity": load_shipment(case["shipment_id"]).get("commodity", ""),
        "promised_delivery": load_shipment(case["shipment_id"]).get("promised_delivery", ""),
        "reported_at": case["reported_at"],
        "description": case["description"],
    }
    return ctrl.run(case["case_id"], case["shipment_id"], raw)


# ========================
# PAGE 1: EXCEPTION QUEUE
# ========================
if page == "Exception Queue":
    st.markdown("<div class='main-header'>Exception Queue</div>", unsafe_allow_html=True)
    st.caption("Browse and select freight exceptions for investigation")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        f_type = st.selectbox("Exception Type", ["", "DAMAGE", "DELAY", "CUSTOMS_HOLD", "MISROUTE", "REFUSED_DELIVERY"])
    with col2:
        f_sev = st.selectbox("Severity", ["", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
    with col3:
        f_status = st.selectbox("Status", ["", "OPEN", "IN_PROGRESS", "RESOLVED", "ESCALATED"])
    with col4:
        st.write("")
        st.write("")
        refresh = st.button("Refresh")

    filters = {"type": f_type, "severity": f_sev, "status": f_status}
    exceptions = load_exceptions(filters)

    if not exceptions:
        st.info("No exceptions match the selected filters.")
    else:
        st.write(f"Showing {len(exceptions)} exceptions")
        for ex in exceptions:
            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 2, 2])
                c1.markdown(f"**{ex['case_id']}**")
                c2.write(ex['shipment_id'])
                c3.markdown(get_severity_badge(ex['severity']), unsafe_allow_html=True)
                c4.write(ex['exception_type'])
                c5.write(ex['status'])
                if c6.button("Investigate", key=f"inv_{ex['case_id']}"):
                    with st.spinner("Running investigation workflow..."):
                        result = run_investigation(ex)
                        st.session_state.investigation_results[ex['case_id']] = result
                        st.session_state.selected_case = ex['case_id']
                    st.success(f"Investigation complete for {ex['case_id']}")
                    st.rerun()

# ========================
# PAGE 2: INVESTIGATION CONSOLE
# ========================
elif page == "Investigation Console":
    st.markdown("<div class='main-header'>Investigation Console</div>", unsafe_allow_html=True)
    st.caption("Real-time agent execution trace and evidence analysis")

    if "selected_case" not in st.session_state or not st.session_state.selected_case:
        st.info("Select a case from the Exception Queue to begin investigation.")
    else:
        case_id = st.session_state.selected_case
        if case_id not in st.session_state.investigation_results:
            st.warning("Investigation not yet run for this case. Go to Exception Queue and click Investigate.")
        else:
            state = st.session_state.investigation_results[case_id]
            case = state.case
            ship = load_shipment(case.shipment_id)

            # Case header
            st.markdown("---")
            h1, h2, h3, h4, h5 = st.columns(5)
            h1.metric("Case ID", case.case_id)
            h2.metric("Shipment", case.shipment_id)
            h3.metric("Type", case.exception_type.value)
            h4.metric("Severity", case.severity.value)
            h5.metric("Status", state.status)

            # Shipment summary
            st.markdown("<div class='sub-header'>Shipment Summary</div>", unsafe_allow_html=True)
            s1, s2, s3, s4, s5, s6 = st.columns(6)
            s1.metric("Origin", ship.get("origin", "N/A"))
            s2.metric("Destination", ship.get("destination", "N/A"))
            s3.metric("Carrier", ship.get("carrier_id", "N/A"))
            s4.metric("Cargo Value", f"${ship.get('cargo_value', 0):,.2f}")
            s5.metric("Commodity", ship.get("commodity", "N/A"))
            s6.metric("Budget", f"{case.investigation_budget} calls")

            # Agent execution trace
            st.markdown("<div class='sub-header'>Agent Execution Trace</div>", unsafe_allow_html=True)
            agents = [
                ("Intake & Triage", "INTAKE_COMPLETE", state.status in ["INTAKE_COMPLETE", "PLANNED", "EVIDENCE_COLLECTED", "RESOLVED", "CRITIC_VALID", "CRITIC_REVISE", "CRITIC_REJECTED", "PENDING_APPROVAL", "APPROVED", "ESCALATED"]),
                ("Investigation Planner", "PLANNED", state.status in ["PLANNED", "EVIDENCE_COLLECTED", "RESOLVED", "CRITIC_VALID", "CRITIC_REVISE", "CRITIC_REJECTED", "PENDING_APPROVAL", "APPROVED", "ESCALATED"]),
                ("Evidence Collector", "EVIDENCE_COLLECTED", state.status in ["EVIDENCE_COLLECTED", "RESOLVED", "CRITIC_VALID", "CRITIC_REVISE", "CRITIC_REJECTED", "PENDING_APPROVAL", "APPROVED", "ESCALATED"]),
                ("Resolver", "RESOLVED", state.status in ["RESOLVED", "CRITIC_VALID", "CRITIC_REVISE", "CRITIC_REJECTED", "PENDING_APPROVAL", "APPROVED", "ESCALATED"]),
                ("Critic", f"CRITIC_{state.critic_verdict.value}", state.status in ["CRITIC_VALID", "CRITIC_REVISE", "CRITIC_REJECTED", "PENDING_APPROVAL", "APPROVED", "ESCALATED"]),
            ]
            for name, expected_status, completed in agents:
                css = "agent-complete" if completed else "agent-active"
                st.markdown(f"<div class='agent-card {css}'><strong>{name}</strong> {'✅ Complete' if completed else '⏳ Pending'}</div>", unsafe_allow_html=True)

            # Evidence collected
            st.markdown("<div class='sub-header'>Evidence Collected</div>", unsafe_allow_html=True)
            if state.bundle.items:
                ev_data = []
                for item in state.bundle.items:
                    status_icon = "🟢" if item.status == "RETRIEVED" else "🔴"
                    ev_data.append({
                        "Tool": item.tool_name,
                        "Status": f"{status_icon} {item.status}",
                        "Finding": item.finding,
                    })
                st.dataframe(ev_data, use_container_width=True)
                st.caption(f"Evidence gap ratio: {state.bundle.gap_ratio*100:.1f}%")
            else:
                st.info("No evidence collected yet.")

            # Resolution
            if state.resolution:
                st.markdown("<div class='sub-header'>Resolution Assessment</div>", unsafe_allow_html=True)
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Root Cause", state.resolution.root_cause)
                r2.metric("Confidence", f"{state.resolution.confidence*100:.0f}%")
                r3.metric("Proposed Action", state.resolution.action)
                r4.metric("Amount", f"${state.resolution.amount:,.2f}")
                st.write(f"**Rationale:** {state.resolution.rationale}")
                st.write(f"**Policy:** {', '.join(state.resolution.policy_references)}")

            # Critic validation
            if state.critic_verdict.value != "PENDING":
                st.markdown("<div class='sub-header'>Critic Validation</div>", unsafe_allow_html=True)
                verdict_color = "🟢" if state.critic_verdict.value == "VALID" else "🟠" if state.critic_verdict.value == "REVISE" else "🔴"
                st.write(f"**Verdict:** {verdict_color} {state.critic_verdict.value}")
                st.write(f"**Notes:** {state.critic_notes}")
                if state.requires_human_review:
                    st.warning(f"Human review required: {', '.join(state.human_review_reasons)}")

            # Actions
            st.markdown("---")
            a1, a2, a3 = st.columns(3)
            if a1.button("View Evidence Details"):
                with st.expander("Evidence Details", expanded=True):
                    for item in state.bundle.items:
                        st.json({"tool": item.tool_name, "status": item.status, "finding": item.finding, "details": item.details})
            if a2.button("Download Case Report"):
                report = {
                    "case": state.case.__dict__,
                    "resolution": state.resolution.__dict__ if state.resolution else None,
                    "critic_verdict": state.critic_verdict.value,
                    "critic_notes": state.critic_notes,
                    "requires_human_review": state.requires_human_review,
                    "audit_log": [ev.__dict__ for ev in state.audit_log],
                }
                st.download_button("Download JSON", json.dumps(report, indent=2, default=str), f"{case_id}_report.json")
            if a3.button("Route to Approval"):
                if state.requires_human_review:
                    st.info("Case routed to Resolution & Approval page.")
                else:
                    st.success("Case auto-approved. No human review required.")

# ========================
# PAGE 3: RESOLUTION & APPROVAL
# ========================
elif page == "Resolution & Approval":
    st.markdown("<div class='main-header'>Resolution & Approval</div>", unsafe_allow_html=True)
    st.caption("Human approval interface for escalated cases")

    pending_cases = [cid for cid, stt in st.session_state.investigation_results.items() if stt.requires_human_review and stt.status not in ["APPROVED", "OVERRIDDEN", "REJECTED"]]

    if not pending_cases:
        st.info("No cases pending human approval.")
    else:
        selected = st.selectbox("Select case", pending_cases)
        state = st.session_state.investigation_results[selected]

        st.markdown("---")
        st.write(f"**Case:** {state.case.case_id} | **Shipment:** {state.case.shipment_id}")
        st.write(f"**Proposed Action:** {state.resolution.action if state.resolution else 'N/A'}")
        st.write(f"**Proposed Amount:** ${state.resolution.amount:,.2f}" if state.resolution else "")
        st.write(f"**Confidence:** {state.resolution.confidence*100:.0f}%" if state.resolution else "")
        st.write(f"**Escalation Reasons:** {', '.join(state.human_review_reasons)}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Approve", key=f"app_{selected}"):
                ctrl = WorkflowController()
                new_state = ctrl.approve_case(state, reviewer="human_operator")
                st.session_state.investigation_results[selected] = new_state
                st.success("Case approved.")
                st.rerun()
        with col2:
            override_action = st.selectbox("Override to", ["NO_ACTION", "CUSTOMER_CREDIT", "ESCALATE_TO_HUMAN"], key=f"ovr_{selected}")
            if st.button("Override", key=f"ovr_btn_{selected}"):
                ctrl = WorkflowController()
                new_state = ctrl.override_case(state, override_action, "Human override selected", "human_operator")
                st.session_state.investigation_results[selected] = new_state
                st.success("Case overridden.")
                st.rerun()
        with col3:
            if st.button("Reject", key=f"rej_{selected}"):
                ctrl = WorkflowController()
                new_state = ctrl.reject_case(state, "Human rejection", "human_operator")
                st.session_state.investigation_results[selected] = new_state
                st.success("Case rejected.")
                st.rerun()

# ========================
# PAGE 4: OPERATIONS DASHBOARD
# ========================
elif page == "Operations Dashboard":
    st.markdown("<div class='main-header'>Operations Dashboard</div>", unsafe_allow_html=True)
    st.caption("Analytics from synthetic dataset and workflow outcomes")

    conn = get_connection()
    cur = conn.cursor()

    # Overall counts
    cur.execute("SELECT COUNT(*) FROM shipments")
    total_shipments = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM exceptions")
    total_exceptions = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM exceptions WHERE status = 'OPEN'")
    open_exceptions = cur.fetchone()[0]
    conn.close()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Shipments", total_shipments)
    m2.metric("Total Exceptions", total_exceptions)
    m3.metric("Open Exceptions", open_exceptions)

    # Exception distribution
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT exception_type, COUNT(*) as cnt FROM exceptions GROUP BY exception_type")
    ex_types = {r["exception_type"]: r["cnt"] for r in cur.fetchall()}
    cur.execute("SELECT severity, COUNT(*) as cnt FROM exceptions GROUP BY severity")
    sev_data = {r["severity"]: r["cnt"] for r in cur.fetchall()}
    conn.close()

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.pie(names=list(ex_types.keys()), values=list(ex_types.values()),
                      title="Exception Type Distribution", hole=0.4,
                      color_discrete_sequence=["#1a2744", "#fd7e14", "#28a745", "#dc3545", "#6c757d"])
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.bar(x=list(sev_data.keys()), y=list(sev_data.values()),
                      title="Severity Distribution", color=list(sev_data.keys()),
                      color_discrete_map={"LOW": "#28a745", "MEDIUM": "#fd7e14", "HIGH": "#dc3545", "CRITICAL": "#721c24"})
        st.plotly_chart(fig2, use_container_width=True)

    # Workflow outcomes from session state
    if st.session_state.investigation_results:
        results = list(st.session_state.investigation_results.values())
        statuses = {}
        for r in results:
            statuses[r.status] = statuses.get(r.status, 0) + 1
        fig3 = px.bar(x=list(statuses.keys()), y=list(statuses.values()),
                      title="Workflow Outcomes", color=list(statuses.keys()))
        st.plotly_chart(fig3, use_container_width=True)

        critic_counts = {"VALID": 0, "REVISE": 0, "REJECT": 0}
        for r in results:
            if r.critic_verdict.value in critic_counts:
                critic_counts[r.critic_verdict.value] += 1
        fig4 = px.pie(names=list(critic_counts.keys()), values=list(critic_counts.values()),
                      title="Critic Verdict Distribution", hole=0.4)
        st.plotly_chart(fig4, use_container_width=True)

    st.caption("Note: Resolution times are simulated based on agent execution steps.")

# ========================
# PAGE 5: AUDIT & COMPLIANCE
# ========================
elif page == "Audit & Compliance":
    st.markdown("<div class='main-header'>Audit & Compliance</div>", unsafe_allow_html=True)
    st.caption("Append-only audit trail with JSON export")

    all_events = []
    for case_id, state in st.session_state.investigation_results.items():
        for ev in state.audit_log:
            all_events.append({
                "Timestamp": ev.timestamp,
                "Case ID": ev.case_id,
                "Agent": ev.agent,
                "Event Type": ev.event_type,
                "Status": ev.status,
                "Details": json.dumps(ev.details),
            })

    if not all_events:
        st.info("No audit events yet. Run investigations to generate audit trails.")
    else:
        st.write(f"Total audit events: {len(all_events)}")
        st.dataframe(all_events, use_container_width=True)

        if st.button("Export Audit Log as JSON"):
            st.download_button("Download JSON", json.dumps(all_events, indent=2, default=str), "audit_log.json")

    st.markdown("---")
    st.caption("Audit log is append-only through the application interface. Records are stored in SQLite with no cryptographic integrity guarantees in this PoC.")