from dataclasses import dataclass
from typing import Literal

@dataclass
class PolicyDecision:
    decision: Literal["APPROVED", "DENIED", "ESCALATE"]
    reason: str
    policy_rule: str

# SoD: no entity can hold both sides of a conflicting pair
SOD_CONFLICTS = [
    ("deploy_to_prod",  "approve_prod_deployment"),
    ("submit_invoice",  "approve_invoice"),
    ("create_user",     "approve_user_creation"),
]

ROLE_ALLOWED = {
    "senior_engineer": ["github_org", "aws_dev_account", "jira", "confluence", "slack_engineering"],
    "engineer":        ["github_org", "jira", "slack_engineering"],
    "finance_analyst": ["finance_db", "tableau"],
}

HIGH_RISK_RESOURCES = ["prod_database", "payment_system", "hr_records"]

def evaluate_access_request(user_id, role, resource, current_access, risk_score) -> PolicyDecision:
    """
    Main policy evaluation — mirrors SailPoint's policy engine.
    Returns APPROVED, DENIED, or ESCALATE with reason + rule name.
    Every call must be logged to the audit trail regardless of outcome.
    """
    # Rule 001: High-risk resources always need human approval
    if resource in HIGH_RISK_RESOURCES:
        return PolicyDecision("ESCALATE",
            f"{resource} is classified high-risk. Human approval required.",
            "RULE-001: High-Risk Resource Escalation")

    # Rule 002: SoD conflict check
    for (a, b) in SOD_CONFLICTS:
        if resource == a and b in current_access:
            return PolicyDecision("DENIED",
                f"SoD violation: cannot hold '{a}' and '{b}' simultaneously.",
                "RULE-002: Separation of Duties")

    # Rule 003: Least privilege — role entitlement check
    if resource not in ROLE_ALLOWED.get(role, []):
        return PolicyDecision("DENIED",
            f"Role '{role}' is not entitled to '{resource}'.",
            "RULE-003: Least Privilege Enforcement")

    # Rule 004: High user risk score → escalate for manager review
    if risk_score >= 7:
        return PolicyDecision("ESCALATE",
            f"User risk score {risk_score}/10 exceeds threshold. Manager review required.",
            "RULE-004: Risk-Based Access Control")

    # Rule 000: All rules passed
    return PolicyDecision("APPROVED",
        f"All policy rules passed for {user_id} → {resource}.",
        "RULE-000: Standard Approval")