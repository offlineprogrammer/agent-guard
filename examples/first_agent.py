from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from langchain import hub
from dotenv import load_dotenv
load_dotenv()

search = DuckDuckGoSearchRun()

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression. Input must be valid Python math."""
    try: return str(eval(expression))
    except: return "Could not evaluate"

tools = [search, calculator]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({
    "input": "Search for SailPoint's stock ticker, then calculate 1000 * 42.50"
})
print(result["output"])