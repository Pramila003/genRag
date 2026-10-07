import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Import the chat router
from apps.chatbot_service.api.v1.endpoints.chat import router as chat_router

# 1. Create the FastAPI app instance (this is what Uvicorn looks for)
app = FastAPI(
    title="ITSM AI Chatbot Service",
    description="LangGraph-powered ITSM Agent Assistant",
    version="1.0.0"
)

# 2. Add CORS middleware (allows requests from frontend apps/Postman)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount the Chat endpoint (/api/v1/chat)
app.include_router(chat_router, prefix="/api/v1")

# 4. Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "chatbot_service"}