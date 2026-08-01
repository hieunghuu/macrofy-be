from abc import ABC, abstractmethod

from app.models.meal import Meal, MealType


class MealRepository(ABC):
    """
    Abstraction over "where meal data comes from". The service layer only
    ever talks to this interface -- swap in a different implementation
    (e.g. one backed by a third-party nutrition API, or a blended repo that
    tries the local catalog first and falls back to an external source)
    without touching any service or route code.
    """

    @abstractmethod
    def list_meals(
        self,
        meal_type: MealType | None = None,
        diet_tags: list[str] | None = None,
    ) -> list[Meal]:
        """Return meals optionally filtered by type and required diet tags (AND semantics)."""
        raise NotImplementedError

    @abstractmethod
    def get_meal(self, meal_id: int) -> Meal | None:
        raise NotImplementedError
