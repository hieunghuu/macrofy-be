from abc import ABC, abstractmethod


class AIClient(ABC):
    """
    Abstraction over the (future) AI service, which will live in its own
    repo and cover things like LLM-based coaching or food-photo
    recognition. The backend only ever talks to this interface -- never a
    specific implementation -- so adding real AI features later means
    writing a new client + endpoints, not restructuring the app. Same
    pattern as MealRepository in app/repositories/.
    """

    @abstractmethod
    def is_configured(self) -> bool:
        """Whether a real AI backend is wired up, vs. running with AI disabled."""
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> bool:
        """Lightweight reachability check, used by /ai/status."""
        raise NotImplementedError
