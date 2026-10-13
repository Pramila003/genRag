# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import ToolNode, tools_condition
# from langchain_openai import ChatOpenAI
# from apps.chatbot_service.agent.state import AgentState
# from apps.chatbot_service.agent.prompts import SYSTEM_PROMPT
# from apps.chatbot_service.tools.registry import ALL_TOOLS
# from dotenv import load_dotenv
# import os
# from  langchain_core.messages import HumanMessage 
# from langgraph.checkpoint.memory import MemorySaver

# load_dotenv()

# # 1. Bind tools to model
# tools = ALL_TOOLS
# tool_node = ToolNode(tools)
# print(f"[DEBUG GRAPH TOOLS]: {ALL_TOOLS}")
# model = ChatOpenAI(
#     model="openai/gpt-oss-120b",               
#     api_key=os.getenv("OPENAI_API_KEY"),          
#     base_url="https://api.groq.com/openai/v1",      
#     temperature=0
# ).bind_tools(tools, parallel_tool_calls=False)

# # 2. Agent node
# async def call_model(state: AgentState):
    
#     messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(state["messages"])
#     response = await model.ainvoke(messages)
#     return {"messages": [response]}

# # 3. Workflow graph
# workflow = StateGraph(AgentState)
# workflow.add_node("agent", call_model)
# workflow.add_node("tools", tool_node)

# workflow.add_edge(START, "agent")
# workflow.add_conditional_edges("agent", tools_condition)
# workflow.add_edge("tools", "agent")

# chatbot_graph = workflow.compile()

# apps/chatbot_service/agent/graph.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver  

from apps.chatbot_service.agent.state import AgentState
from apps.chatbot_service.agent.prompts import SYSTEM_PROMPT
from apps.chatbot_service.tools.registry import ALL_TOOLS

load_dotenv()

groq_api_key = os.getenv("OPENAI_API_KEY")
groq_base_url = "https://api.groq.com/openai/v1"
model_name = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# Setup models & tools
tools = ALL_TOOLS
tool_node = ToolNode(tools)

tool_model = ChatOpenAI(
    model=model_name,
    api_key=groq_api_key,
    base_url=groq_base_url,
    temperature=0
).bind_tools(tools, parallel_tool_calls=False)

responder_model = ChatOpenAI(
    model=model_name,
    api_key=groq_api_key,
    base_url=groq_base_url,
    temperature=0
)

# Nodes
async def agent_node(state: AgentState):
    """Inspects conversation history and chooses tool if needed."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(state["messages"])
    response = await tool_model.ainvoke(messages)
    return {"messages": [response]}

async def responder_node(state: AgentState):
    """Synthesizes the tool output while preserving conversation context."""
    user_message = [m.content for m in state["messages"] if isinstance(m, HumanMessage)][-1]
    tool_data = state["messages"][-1].content

    # Include recent context so follow-up questions work seamlessly
    synthesis_prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""User Question: {user_message}

Data retrieved from backend:
{tool_data}

Provide a helpful response answering the question based on this data. Remember previous conversation context if relevant."""}
    ]
    response = await responder_model.ainvoke(synthesis_prompt)
    return {"messages": [response]}

def route_after_agent(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# Graph Construction
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("responder", responder_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", route_after_agent, ["tools", END])
workflow.add_edge("tools", "responder")
workflow.add_edge("responder", END)

# ➔ 2. Instantiate Checkpointer & Compile
memory = MemorySaver()
chatbot_graph = workflow.compile(checkpointer=memory)  # <--- Persists history by thread_id

