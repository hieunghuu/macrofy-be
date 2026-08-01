import httpx

from app.clients.base import AIClient


class HttpAIClient(AIClient):
    """Talks to the external `ai` repo's deployed service over HTTP."""

    def __init__(self, base_url: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        return True

    def ping(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/health", timeout=self.timeout_seconds)
            return response.status_code == 200
        except httpx.HTTPError:
            return False
