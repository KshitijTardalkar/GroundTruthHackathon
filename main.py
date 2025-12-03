import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from models.schemas import ChatRequest, ChatResponse, HealthResponse, UserListResponse
from modules.auth import get_or_create_user, list_users
from modules.llm_handler import ChatbotError, chatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize RAG globally
from modules import llm_handler
from modules.rag_retriever import rag_retriever

llm_handler.rag_retriever = rag_retriever


# ========================================
# LIFESPAN (replaces on_event)
# ========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 EVA Customer Support Bot (Demo Mode)")
    logger.info("=" * 60)
    logger.info("Demo Users: john, sarah, demo")
    logger.info("=" * 60)

    yield

    # Shutdown (if needed)
    logger.info("Shutting down...")


app = FastAPI(
    title="EVA - Customer Support Bot",
    description="H-002 Demo: Simple Chat with Customer Tracking",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ========================================
# Exception handlers
# ========================================
@app.exception_handler(ChatbotError)
async def chatbot_exception_handler(request, exc: ChatbotError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Chatbot Error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


# ========================================
# AUTH ROUTES
# ========================================
@app.get("/")
async def root_redirect():
    """Redirect root to login"""
    return FileResponse("static/login.html")


@app.get("/login")
async def serve_login():
    """Serve login page"""
    return FileResponse("static/login.html")


@app.get("/app")
async def serve_frontend():
    """Serve the chat interface"""
    return FileResponse("static/index.html")


# ========================================
# API ENDPOINTS
# ========================================
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    try:
        rag_enabled = (
            rag_retriever is not None and rag_retriever.vectorstore is not None
        )

        return {
            "status": "healthy",
            "model": settings.MODEL_NAME,
            "langchain_version": "0.3+",
            "rag_enabled": rag_enabled,
            "pii_protection": True,
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unhealthy"
        )


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Simple chat endpoint - just provide username and message
    No authentication needed for demo!
    """
    try:
        # Get or create user
        user = get_or_create_user(request.username)
        customer_id = user["customer_id"]

        logger.info(f"Chat from {request.username} ({customer_id})")

        result = chatbot.get_response(
            user_message=request.message, customer_id=customer_id, session_id="default"
        )

        return {
            "response": result["response"],
            "username": request.username,
            "customer_id": customer_id,
            "timestamp": datetime.now().isoformat(),
            "pii_masked": result["pii_masked"],
            "context_retrieved": result["context_retrieved"],
        }

    except ChatbotError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request",
        )


@app.get("/users", response_model=UserListResponse)
def list_all_users():
    """List all users (for demo)"""
    users = list_users()
    return {"users": users, "count": len(users)}


@app.delete("/session/{username}")
def clear_session(username: str):
    """Clear conversation history for a user"""
    try:
        user = get_or_create_user(username)
        customer_id = user["customer_id"]
        full_session_id = f"{customer_id}:default"

        success = chatbot.clear_session(full_session_id)
        return {
            "message": f"Session cleared for {username}",
            "customer_id": customer_id,
        }
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear session",
        )


@app.get("/history/{username}")
def get_chat_history(username: str):
    """Get chat history for a user"""
    try:
        user = get_or_create_user(username)
        customer_id = user["customer_id"]
        full_session_id = f"{customer_id}:default"

        if full_session_id not in chatbot.store:
            return {"messages": [], "count": 0}

        history = chatbot.store[full_session_id]
        messages = []

        for msg in history.messages:
            messages.append(
                {
                    "type": msg.type,  # 'human' or 'ai'
                    "content": msg.content,
                }
            )

        return {
            "username": username,
            "customer_id": customer_id,
            "messages": messages,
            "count": len(messages),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics")
def get_analytics():
    """Analytics dashboard data"""
    from modules.auth import users_db

    # Count active sessions
    active_sessions = len(chatbot.store)

    # Count messages per user
    message_counts = {}
    for session_id, history in chatbot.store.items():
        customer_id = session_id.split(":")[0]
        username = next(
            (u for u, d in users_db.items() if d["customer_id"] == customer_id),
            "Unknown",
        )
        message_counts[username] = len(history.messages)

    # Total messages
    total_messages = sum(message_counts.values())

    return {
        "total_users": len(users_db),
        "active_conversations": active_sessions,
        "total_messages": total_messages,
        "messages_per_user": message_counts,
        "rag_enabled": rag_retriever is not None
        and rag_retriever.vectorstore is not None,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
