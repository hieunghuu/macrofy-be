from app.clients.base import AIClient


class NullAIClient(AIClient):
    """Default client when AI_SERVICE_URL isn't set. Always reports unavailable."""

    def is_configured(self) -> bool:
        return False

    def ping(self) -> bool:
        return False
