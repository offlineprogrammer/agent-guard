import json
import os
import re
import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools import tool
from tools.identity_tools import get_user_profile_tool as get_user_profile, get_required_access_for_role
from engine.policy_rules import evaluate_access_request
from db.audit import log_decision
from dotenv import load_dotenv

load_dotenv()

MOCK_ENV_VAR = "USE_MOCK_LLM"
DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"

@tool
def provision_with_governance(user_id: str, resource: str, role: str,
                               current_access_json: str, risk_score: int) -> str:
    """
    Provision access ONLY if the SailPoint policy engine approves.
    Logs EVERY decision to the audit trail — approved or not.
    This is the governance gate: nothing gets provisioned without a policy check.
    """
    current_access = json.loads(current_access_json)
    decision = evaluate_access_request(user_id, role, resource, current_access, risk_score)

    jit_expiry = None
    if decision.decision == "APPROVED":
        jit_expiry = (datetime.datetime.now() + datetime.timedelta(hours=8)).isoformat()

    log_decision("provisioner-agent-001", user_id, resource,
                  decision.decision, decision.policy_rule, decision.reason, jit_expiry)

    return json.dumps({
        "resource": resource, "decision": decision.decision,
        "policy_rule": decision.policy_rule, "reason": decision.reason,
        "jit_expiry": jit_expiry
    })


def _is_mock_mode(use_mock: bool = False) -> bool:
    return use_mock or os.environ.get(MOCK_ENV_VAR, "false").lower() in {"1", "true", "yes"}


def _parse_request(request: str) -> dict:
    user_id_match = re.search(r"([a-z]+\.[a-z]+)", request)
    role_match = re.search(r"\b(senior_engineer|engineer|finance_analyst)\b", request)
    risk_match = re.search(r"risk score(?: is|:)?\s*(\d+)", request, re.IGNORECASE)
    current_access = []
    if re.search(r"current access (?:list )?(?:is|=) ?\[\]", request, re.IGNORECASE):
        current_access = []
    elif access_match := re.search(r"current access (?:list )?(?:is|=) ?\[([^\]]*)\]", request, re.IGNORECASE):
        entries = [x.strip() for x in access_match.group(1).split(",") if x.strip()]
        current_access = entries

    return {
        "user_id": user_id_match.group(1) if user_id_match else "",
        "role": role_match.group(1) if role_match else "",
        "risk_score": int(risk_match.group(1)) if risk_match else 0,
        "current_access": current_access,
        "request": request,
    }


def _run_mock_provisioner(request: str) -> str:
    parsed = _parse_request(request)
    user_id = parsed["user_id"]
    role = parsed["role"]
    risk_score = parsed["risk_score"]
    current_access = parsed["current_access"]

    profile_json = get_user_profile.invoke(user_id)
    profile = json.loads(profile_json)
    required_json = get_required_access_for_role.invoke(role)
    required_access = json.loads(required_json).get("required_access", [])

    actions = []
    for resource in required_access:
        decision_json = provision_with_governance.invoke({
            "user_id": user_id,
            "resource": resource,
            "role": role,
            "current_access_json": json.dumps(current_access),
            "risk_score": risk_score,
        })
        actions.append(json.loads(decision_json))

    output = {
        "mode": "mock",
        "request": request,
        "profile": profile,
        "required_access": required_access,
        "current_access": current_access,
        "actions": actions,
    }
    return json.dumps(output, indent=2)


def run_provisioner(request: str, use_mock: bool = False) -> str:
    if _is_mock_mode(use_mock):
        return _run_mock_provisioner(request)

    llm = ChatOpenAI(model=DEFAULT_OPENAI_MODEL, temperature=0)
    tools = [get_user_profile, get_required_access_for_role, provision_with_governance]
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=12)
    result = executor.invoke({"input": request})
    return result["output"]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [get_user_profile, get_required_access_for_role, provision_with_governance]
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=12)
    result = executor.invoke({"input": request})
    return result["output"]