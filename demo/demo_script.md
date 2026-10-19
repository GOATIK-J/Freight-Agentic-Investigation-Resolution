# F.A.I.R. 5-Minute Demo Script

## Slide 1: Title (0:00–0:20)
"F.A.I.R. — Freight Agentic Investigation & Resolution. An autonomous multi-agent system for freight exception handling. Built for Agentic AI CA-3."

## Slide 2: Problem (0:20–0:50)
"Freight exceptions occur on 8–15% of shipments. Coordinators spend 60–70% of their time gathering evidence across disconnected systems — TMS, carrier portals, customs platforms, weather tools. Resolution cycles stretch to 24–72 hours."

## Slide 3: Business Challenge (0:50–1:20)
"Each exception family requires a completely different evidence set and resolution logic. Damage needs POD and photos. Delay needs weather and route history. Customs needs HS codes and missing documents. A fixed rule cannot handle all of these. Agency is required."

## Slide 4: Proposed Solution (1:20–1:50)
"F.A.I.R. introduces five collaborative agents — Intake, Planner, Evidence Collector, Resolver, and Critic. Deterministic safety for all financial computations. Adversarial validation to catch false positives. Human-in-the-loop gate for high-risk cases."

## Slide 5: Architecture (1:50–2:20)
"A typed InvestigationState flows through all agents. Conditional branching routes based on exception type, evidence sufficiency, confidence, and Critic verdict. Bounded loops allow one revision attempt before human escalation."

## Slide 6: Agent Roles (2:20–2:50)
"Intake normalizes and budgets. Planner tailors evidence lists. Collector queries the synthetic SQLite database through ten read-only tools. Resolver correlates evidence and proposes actions with calculated amounts. Critic independently validates — catching contradictions and unsupported claims."

## Slide 7: Streamlit PoC Demo (2:50–3:40)
[Show live application or screenshot]
"The five-page Streamlit application demonstrates the full workflow. Exception Queue for browsing. Investigation Console showing real-time agent execution. Resolution & Approval for human gates. Operations Dashboard with metrics. And Audit & Compliance for full traceability."

## Slide 8: Evaluation (3:40–4:10)
"On our 25-case synthetic evaluation suite: 36 automated tests cover boundary conditions, workflow paths, critic rejection, bounded revision, and human gate triggers. All tests pass, validating deterministic safeguards and agent coordination."

## Slide 9: Limitations & Future (4:10–4:40)
"Current limitations: synthetic data only, rule-based classification, no multi-modal evidence. Future scope includes real carrier APIs, computer vision for damage assessment, predictive prevention, and ERP connectors."

## Slide 10: Conclusion (4:40–5:00)
"F.A.I.R. demonstrates that agentic AI can be applied to complex freight workflows with deterministic safety, full auditability, and adversarial validation — without requiring paid LLM APIs. Thank you. Questions?"
