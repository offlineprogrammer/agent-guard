from langchain.tools import tool
import json, datetime

ROLE_ACCESS_MAP = {
    "senior_engineer": ["github_org", "aws_dev_account", "jira", "confluence", "slack_engineering"],
    "engineer": ["github_org", "jira", "slack_engineering"],
    "finance_analyst": ["finance_db", "tableau"],
}
USERS_DB = {
    "sarah.chen": {"role": "senior_engineer", "dept": "engineering", "risk_score": 2},
    "john.doe":   {"role": "engineer",         "dept": "engineering", "risk_score": 7},
}

def get_user_profile(user_id: str) -> str:
    """Retrieve user role, department, and risk score from identity store."""
    user = USERS_DB.get(user_id)
    if not user:
        return json.dumps({"error": f"User {user_id} not found"})
    return json.dumps({"user_id": user_id, **user})

@tool
def get_user_profile_tool(user_id: str) -> str:
    """Tool wrapper for get_user_profile."""
    return get_user_profile(user_id)

@tool
def get_required_access_for_role(role: str) -> str:
    """Returns the standard access entitlements for a given role (role baseline)."""
    access = ROLE_ACCESS_MAP.get(role, [])
    return json.dumps({"role": role, "required_access": access})

@tool
def provision_access(user_id: str, resource: str) -> str:
    """Mock-provisions JIT access to a resource. Credential expires in 8 hours."""
    expiry = (datetime.datetime.now() + datetime.timedelta(hours=8)).isoformat()
    return json.dumps({"status": "PROVISIONED", "user": user_id,
                         "resource": resource, "jit_expiry": expiry,
                         "note": "JIT credential — auto-expires in 8 hours"})