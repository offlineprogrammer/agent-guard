from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools import tool
from tools.identity_tools import get_user_profile_tool as get_user_profile, get_required_access_for_role
from engine.policy_rules import evaluate_access_request
from db.audit import log_decision
from dotenv import load_dotenv
import json, datetime

load_dotenv()

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

def run_provisioner(request: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [get_user_profile, get_required_access_for_role, provision_with_governance]
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=12)
    result = executor.invoke({"input": request})
    return result["output"]