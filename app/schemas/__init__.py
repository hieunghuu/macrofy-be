"""
Schemas package - Pydantic models for API request/response validation.

Main exports:
- Meal schemas for meal plan endpoints
- Ingredient schemas for ingredient database

Usage:
    from app.schemas import MealOut, IngredientSummary
"""

from app.schemas.meal import (
    IngredientCategory,
    IngredientCreate,
    IngredientNutrition,
    MealIngredientOut,
    MealOut,
    MealPlanRequest,
    MealPlanResponse,
    MealPlanSlotOut,
    MealSummary,
    MealType,
    OptimizerType,
)

__all__ = [
    # Enums
    "MealType",
    "IngredientCategory",
    "OptimizerType",
    # Ingredient schemas
    "IngredientNutrition",
    "IngredientCreate",
    # Meal schemas
    "MealOut",
    "MealSummary",
    "MealIngredientOut",
    # Meal plan schemas
    "MealPlanRequest",
    "MealPlanResponse",
    "MealPlanSlotOut",
]
