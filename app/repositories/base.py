from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient, IngredientCategory
    from app.models.meal import Meal, MealType


class MealRepository(ABC):
    @abstractmethod
    def list_meals(self, meal_type: "MealType | None" = None, diet_tags: "list[str] | None" = None) -> "list[Meal]": ...
    @abstractmethod
    def get_meal(self, meal_id: int) -> "Meal | None": ...


class IngredientRepository(ABC):
    @abstractmethod
    def list_ingredients(self, category: "IngredientCategory | None" = None, search: "str | None" = None) -> "list[Ingredient]": ...
    @abstractmethod
    def get_ingredient(self, ingredient_id: int) -> "Ingredient | None": ...
    @abstractmethod
    def create_ingredient(self, ingredient_data: dict) -> "Ingredient": ...
    @abstractmethod
    def update_ingredient(self, ingredient_id: int, ingredient_data: dict) -> "Ingredient | None": ...
    @abstractmethod
    def delete_ingredient(self, ingredient_id: int) -> bool: ...
    @abstractmethod
    def count_ingredients(self, category: "IngredientCategory | None" = None) -> int: ...
