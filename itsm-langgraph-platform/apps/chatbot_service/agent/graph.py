from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from apps.chatbot_service.agent.state import AgentState
from apps.chatbot_service.agent.prompts import SYSTEM_PROMPT
from apps.chatbot_service.tools.registry import ALL_TOOLS
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Bind tools to model
tools = ALL_TOOLS
tool_node = ToolNode(tools)
print(f"[DEBUG GRAPH TOOLS]: {ALL_TOOLS}")
model = ChatOpenAI(
    model="openai/gpt-oss-120b",               
    api_key=os.getenv("OPENAI_API_KEY"),          
    base_url="https://api.groq.com/openai/v1",      
    temperature=0
).bind_tools(tools, parallel_tool_calls=False)

# 2. Agent node
async def call_model(state: AgentState):
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(state["messages"])
    response = await model.ainvoke(messages)
    return {"messages": [response]}

# 3. Workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

chatbot_graph = workflow.compile()