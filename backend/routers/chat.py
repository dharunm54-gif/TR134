"""
Chat Router - AI clinical assistant endpoint
"""

from fastapi import APIRouter, HTTPException
import logging
from models.schemas import ChatRequest, ChatResponse
from services.chat_service import generate_chat_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    RAG-grounded clinical AI chat assistant.
    All responses are based on retrieved medical evidence only.
    Returns 'Insufficient evidence' if data not found.
    """
    try:
        result = await generate_chat_response(
            message=request.message,
            mode=request.mode,
            conversation_history=[m.dict() for m in request.conversation_history],
            analysis_context=request.context
        )
        return ChatResponse(
            response=result["response"],
            citations=result.get("citations", []),
            confidence=result.get("confidence", 0.0),
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
