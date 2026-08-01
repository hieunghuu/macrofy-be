from fastapi import APIRouter, Depends

from app.clients.base import AIClient
from app.clients.dependency import get_ai_client
from app.schemas.ai import AIStatusResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status", response_model=AIStatusResponse)
def ai_status(client: AIClient = Depends(get_ai_client)) -> AIStatusResponse:
    """
    Reports whether the AI service is configured and reachable. Once real
    AI-powered endpoints are added, they'll depend on get_ai_client() the
    same way this one does.
    """
    return AIStatusResponse(configured=client.is_configured(), reachable=client.ping())
