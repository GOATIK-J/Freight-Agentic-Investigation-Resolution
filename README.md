# F.A.I.R. — Freight Agentic Investigation & Resolution

**Autonomous Multi-Agent System for Freight Exception Handling**

Built for Agentic AI CA-3 Academic Project | October 2026

---

## Overview

F.A.I.R. is an autonomous multi-agent proof-of-concept that investigates and resolves freight exceptions through a structured five-agent workflow. It demonstrates core agentic AI principles: task planning, multi-step execution, decision-making under uncertainty, adversarial validation, and human-in-the-loop governance.

## Business Problem

Freight exceptions (damage, delay, customs hold, misroute, refused delivery) occur on 8–15% of shipments. Each investigation requires coordinators to manually query multiple disconnected systems, consuming 60–70% of their time on evidence gathering rather than decision-making.

## System Architecture

F.A.I.R. implements a state-machine workflow where a typed `InvestigationState` flows sequentially through five specialized agents:

1. **Intake & Triage Agent** — Normalizes exceptions, assigns severity, sets investigation budget
2. **Investigation Planner Agent** — Builds exception-specific evidence plans
3. **Evidence Collector Agent** — Executes read-only tool calls against synthetic data
4. **Resolver Agent** — Correlates evidence and proposes deterministic resolutions
5. **Critic Agent** — Independently validates conclusions via adversarial checks

**Conditional Branching:**
- Evidence gap > 30% → auto-escalation
- Critic REVISE → one bounded revision loop
- Critic REJECT → human escalation
- High-value / low-confidence / strategic customers → human gate

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data Layer | SQLite + synthetic data |
| UI / PoC | Streamlit |
| Charts | Plotly |
| Testing | pytest |

## Project Structure

```
FAIR-Freight-Agentic-Investigation/
├── app.py                    # 5-page Streamlit application
├── agents/                   # 5 agent implementations
│   ├── intake.py
│   ├── planner.py
│   ├── evidence.py
│   ├── resolver.py
│   └── critic.py
├── orchestration/            # Workflow controller
│   └── controller.py
├── tools/                    # 10 read-only query tools
│   └── freight_tools.py
├── data/                     # SQLite database & synthetic data
│   └── database.py
├── models/                   # Typed shared state
│   └── state.py
├── utils/                    # Deterministic policy functions
│   └── policy.py
├── tests/                    # pytest suite
│   └── test_fair.py
├── architecture/             # Architecture diagrams
│   ├── architecture.mmd
│   └── architecture.png
├── docs/                     # Documentation
├── presentation/             # PowerPoint presentation
├── demo/                     # Demo script
├── requirements.txt
└── README.md
```

## Setup & Installation

```bash
# Clone or extract the project
cd FAIR-Freight-Agentic-Investigation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from data.database import init_db; init_db()"
```

## Running the Application

```bash
streamlit run app.py
```

The application will start at `http://localhost:8501`.

## Running Tests

```bash
pytest tests/test_fair.py -v
```

## Five-Page Streamlit UI

| Page | Purpose |
|------|---------|
| Exception Queue | Browse and select cases |
| Investigation Console | Real-time agent trace and evidence |
| Resolution & Approval | Human approval interface |
| Operations Dashboard | Analytics and metrics |
| Audit & Compliance | Append-only audit trail |

## Demo Scenarios

1. **Damage with sufficient evidence** — Select CASE-20260001 (DAMAGE, HIGH). The system retrieves POD, damage photos, and carrier history, then proposes a carrier claim.
2. **Customs hold with missing docs** — Select CASE-20260003 (CUSTOMS_HOLD). The system identifies missing commercial invoice and proposes document submission.
3. **High-value escalation** — Any CRITICAL severity or Strategic customer triggers mandatory human review.

## Deterministic Safeguards

- All monetary calculations are pure Python functions
- Policy-permitted actions are explicitly allow-listed per exception type
- Liability caps are computed from cargo value and customer tier
- No real claims, payments, or notifications are executed

## Limitations

- Synthetic data only — no live TMS or carrier integrations
- Deterministic rule-based classification (optional Ollama integration possible)
- Single-modal evidence (structured data and text only)
- No real-time streaming — simulated agent trace

## License

Academic project. Not for production use.

## Authors

- Gatik Johar - 24070126060
- Harman Singh - 24070126064