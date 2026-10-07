from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from apps.chatbot_service.agent.graph import chatbot_graph

router = APIRouter()

class ChatPayload(BaseModel):
    message: str
    thread_id: str = "session_default"

@router.post("/chat")
async def chat_endpoint(
    payload: ChatPayload,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token missing")

   
    config = {
        "configurable": {
            "thread_id": payload.thread_id,
            "user_token": token
        }
    }

    result = await chatbot_graph.ainvoke(
        {"messages": [HumanMessage(content=payload.message)]},
        config=config
    )

    return {"response": result["messages"][-1].content}