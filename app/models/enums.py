from __future__ import annotations

import enum


class IngredientCategory(str, enum.Enum):
    protein = "protein"
    vegetable = "vegetable"
    fruit = "fruit"
    grain = "grain"
    dairy = "dairy"
    legume = "legume"
    nut_seed = "nut_seed"
    oil_fat = "oil_fat"
    condiment = "condiment"
    beverage = "beverage"
    seasonings = "seasonings"


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"
