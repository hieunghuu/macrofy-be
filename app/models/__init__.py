"""
Models package - SQLAlchemy ORM models.

Each model file represents a database table:
- meal.py: Meals/recipes in the catalog
- ingredient.py: Raw ingredients with nutritional data per 100g
- meal_ingredient.py: Junction table linking meals to ingredients

Usage:
    from app.models import Meal, Ingredient, MealIngredient
"""

from app.models.ingredient import Ingredient, IngredientCategory
from app.models.meal import Meal
from app.models.meal_ingredient import MealIngredient
from app.models.enums import IngredientCategory, MealType

__all__ = [
    "Meal",
    "MealType",
    "Ingredient",
    "IngredientCategory",
    "MealIngredient",
]
