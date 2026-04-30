# 🛡 AgentGuard
### AI Agent Identity Governance — SailPoint-Style Policy Engine Demo

> **AgentGuard** demonstrates what happens when AI agents request access to enterprise resources — and how identity governance controls, audits, and governs every decision before anything is provisioned.

---

## The Problem This Solves

Every enterprise deploying AI agents faces an unsolved identity problem:

- **AI agents need credentials** to call APIs, access databases, and interact with enterprise systems
- **Traditional PAM tools** were built for human identities — not for agents that request access dynamically at runtime, act autonomously, and can spawn sub-agents
- **No governance means no audit trail** — which fails SOC 2, SOX, and emerging EU AI Act requirements

AgentGuard shows how SailPoint-style identity governance closes this gap: every agent access request is checked against policy rules, approved or denied, and logged to an immutable audit trail before anything is provisioned.

---

## Architecture

```
Natural Language Input
"Onboard Sarah Chen as Senior Engineer"
        │
        ▼
┌─────────────────────────────────────────┐
│   SUPERVISOR AGENT  (LangGraph)          │
│   Parses intent · Determines resources  │
│   Routes to worker agents               │
└──────────┬──────────────────┬───────────┘
           │                  │
           ▼                  ▼
┌─────────────────┐  ┌────────────────────────────┐
│  RISK CHECKER   │  │   PROVISIONER AGENT         │
│  AGENT          │  │                             │
│  • Score user   │  │   For each resource:        │
│  • Flag SoD     │  │   1. Call policy_engine()   │
│  • Check JIT    │  │   2. If APPROVED → mock     │
└─────────────────┘  │      provision_access()     │
                     │   3. Log to audit_db         │
                     └──────────────┬──────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────┐
│   POLICY ENGINE  (engine/policy_rules.py)        │
│                                                  │
│   RULE-001  High-risk resource    → ESCALATE     │
│   RULE-002  SoD conflict          → DENIED       │
│   RULE-003  Role not entitled     → DENIED       │
│   RULE-004  Risk score ≥ 7        → ESCALATE     │
│   RULE-000  All rules pass        → APPROVED     │
└──────────────────────────┬──────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────┐
│   AUDIT LOG  (SQLite — db/agentguard.db)         │
│   timestamp · agent_id · user · resource         │
│   decision · policy_rule · reason · jit_expiry   │
└──────────────────────────┬──────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────┐
│   STREAMLIT DASHBOARD  (dashboard/app.py)        │
│   Live audit trail · Decision metrics            │
│   Color-coded outcomes · Filter by result        │
└─────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Orchestration | LangChain + LangGraph |
| LLM Backend | OpenAI GPT-4o-mini (or AWS Bedrock Claude 3 Haiku) |
| Policy Engine | Python — custom rules engine |
| Audit Log | SQLite via Python `sqlite3` |
| Dashboard | Streamlit + Pandas |
| Language | Python 3.11+ |

---

## Project Structure

```
AgentGuard/
├── .env                     # API keys — never committed
├── .env.example             # Template for environment variables
├── .gitignore
├── requirements.txt         # Python dependencies
├── main.py                  # Entry point — runs both demo scenarios
├── examples/
│   ├── first_agent.py           # Basic agent example with OpenAI
│   ├── bedrock_agent.py         # Agent example with AWS Bedrock
│   └── supervisor_provisioner_graph.py  # Supervisor agent using LangGraph
├── agents/
│   └── provisioner.py       # Provisioner agent with governance-gated tool
├── tools/
│   └── identity_tools.py    # Mock SailPoint identity API tools
├── engine/
│   └── policy_rules.py      # Policy engine — the heart of the demo
├── db/
│   └── audit.py             # SQLite audit log — read/write functions
├── dashboard/
│   └── app.py               # Streamlit visual dashboard
└── notes/                   # CISO narrative docs, objection responses
```

## Bonus Examples

The `examples/` folder contains standalone agent implementations for reference:

- **`first_agent.py`**: A simple LangChain agent using OpenAI GPT-4o-mini with search and calculator tools.
- **`bedrock_agent.py`**: An agent powered by AWS Bedrock (Claude 3 Haiku) for enterprise-grade LLM backends.
- **`supervisor_provisioner_graph.py`**: A LangGraph-based supervisor agent that routes tasks to worker agents (conceptual demo, not integrated into the main flow).

---

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key — get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (~$2 for this demo)
- Optional: AWS account with Bedrock access (for enterprise-grade LLM backend)

### Install

```bash
git clone https://github.com/offlineprogrammer/agent-guard.git
cd agent-guard

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

### Run

```bash
# Step 1 — Run both demo scenarios and populate the audit log
python3 main.py

# Step 2 — Launch the Streamlit dashboard
streamlit run dashboard/app.py
# Opens at http://localhost:8501
```

**Run with Mock LLM** (no API keys required):

```bash
USE_MOCK_LLM=true python main.py
```

This mode runs the demo without calling OpenAI or any external LLM service — useful for testing the policy engine and audit logging without credentials.

---

## Demo Scenarios

AgentGuard ships with two scenarios designed to tell a complete governance story:

### Scenario 1 — Standard Onboarding ✅

```
Input: "Onboard sarah.chen as senior_engineer"
```

The provisioner agent retrieves Sarah's profile, determines all required access for her role (GitHub, AWS dev account, Jira, Confluence, Slack), and runs each through the policy engine. All requests pass — role entitlement confirmed, risk score low, no SoD conflicts. All access is provisioned with JIT credentials expiring in 8 hours.

**What the CISO sees:** Green audit trail. Every access decision justified. JIT expiry timestamps on every credential.

### Scenario 2 — Rogue Agent (Policy Violation) 🚫

```
Input: "Provision prod_database access for john.doe"
```

A second agent attempts to request production database access for an engineer with a high risk score. The policy engine catches it on two rules: `RULE-001` (prod_database is a high-risk resource) and `RULE-004` (risk score 7/10 exceeds threshold). Both decisions are ESCALATE/DENIED and logged.

**What the CISO sees:** Red and amber rows in the audit trail. Exact policy rules that triggered. Proof that the governance layer caught what a human reviewer would have flagged in a quarterly access review — but did it in milliseconds, automatically.

---

## Identity Governance Concepts Demonstrated

| Concept | How AgentGuard Demonstrates It |
|---|---|
| **Least Privilege** | Agents only receive access that matches their role baseline. `RULE-003` denies anything outside the role entitlement map. |
| **Just-In-Time Access** | All provisioned credentials carry an 8-hour JIT expiry. No persistent credentials. |
| **Separation of Duties** | `RULE-002` detects and blocks SoD conflicts before provisioning (e.g., cannot hold deploy_to_prod + approve_prod_deployment). |
| **Risk-Based Access Control** | `RULE-004` escalates requests from users with risk scores ≥ 7 to human review. |
| **Non-Human Identity Governance** | The agent itself has an `agent_id` in the audit log — treated as an identity, not just a process. |
| **Immutable Audit Trail** | Every decision — approved, denied, or escalated — is logged to SQLite with timestamp, policy rule, and full reason. This is the SOC 2 evidence record. |

---

## Policy Rules Reference

| Rule | Name | Trigger | Outcome |
|---|---|---|---|
| RULE-000 | Standard Approval | All rules pass | APPROVED + JIT expiry |
| RULE-001 | High-Risk Resource | Resource in `HIGH_RISK_RESOURCES` list | ESCALATE |
| RULE-002 | Separation of Duties | SoD conflict with current access | DENIED |
| RULE-003 | Least Privilege | Role not entitled to resource | DENIED |
| RULE-004 | Risk-Based Access Control | User risk score ≥ 7 | ESCALATE |

To add a new rule: extend `evaluate_access_request()` in `engine/policy_rules.py`. Each rule follows the same pattern — check condition, return a `PolicyDecision` with decision, reason, and rule name.

---

## Extending AgentGuard

**Add a new policy rule:**
1. Open `engine/policy_rules.py`
2. Add your condition before the final RULE-000 approval
3. Return a `PolicyDecision("DENIED"/"ESCALATE", reason, "RULE-00N: Name")`

**Add a new resource or role:**
1. Add to `ROLE_ALLOWED` in `engine/policy_rules.py`
2. Add to `ROLE_ACCESS_MAP` in `tools/identity_tools.py`

**Add a new user:**
1. Add to `USERS_DB` in `tools/identity_tools.py`

**Connect to a real SailPoint API:**
Replace the mock functions in `tools/identity_tools.py` with HTTP calls to the [SailPoint Identity Security Cloud REST API](https://developer.sailpoint.com/docs/api/v3/).

---

## Compliance Relevance

| Framework | How AgentGuard's Audit Log Supports It |
|---|---|
| **SOC 2 Type II** | Every access decision is logged with timestamp, policy rule, and reason — the evidence record for access control testing |
| **SOX** | SoD conflict detection prevents AI agents from creating financial control violations |
| **EU AI Act** | Audit trail of AI agent decisions with governance controls demonstrates human oversight of high-risk AI |
| **NIST AI RMF** | Policy engine maps to GOVERN and MANAGE functions — risk-based access control per RMF guidance |

---

## License

MIT — use freely for educational and demonstration purposes.