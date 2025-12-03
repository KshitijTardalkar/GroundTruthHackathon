from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import settings
from modules.llm_handler import chatbot

app = FastAPI(
    title="H-002 Customer Support Bot",
    description="AI-powered customer support with conversation memory",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"  # Optional session ID


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "model": settings.MODEL_NAME,
        "langchain_version": "0.3+",
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        response = chatbot.get_response(
            user_message=request.message, session_id=request.session_id
        )

        return {"response": response, "session_id": request.session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
