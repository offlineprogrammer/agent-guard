from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from tools.identity_tools import get_user_profile, check_user_access

# Same agent — now running on enterprise-grade AWS backend
llm = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name="us-east-1",
    model_kwargs={"temperature": 0, "max_tokens": 1000}
)
tools = [get_user_profile, check_user_access]
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({
    "input": "Review john.doe's access. What is high risk and overdue for review?"
})
print(result["output"])