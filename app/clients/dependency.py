from functools import lru_cache

from app.clients.base import AIClient
from app.clients.http_ai_client import HttpAIClient
from app.clients.null_ai_client import NullAIClient
from app.core.config import settings


@lru_cache
def get_ai_client() -> AIClient:
    """
    FastAPI dependency. Returns the real HTTP client once AI_SERVICE_URL is
    set, otherwise a no-op client. This is the entire swap for turning on
    AI features later: point the env var at the deployed `ai` service --
    nothing else in the app changes.
    """
    if settings.ai_service_url:
        return HttpAIClient(
            base_url=settings.ai_service_url,
            timeout_seconds=settings.ai_service_timeout_seconds,
        )
    return NullAIClient()
