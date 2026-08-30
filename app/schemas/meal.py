from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class IngredientCategory(str, Enum):
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
    


class IngredientBase(BaseModel):
    name: str = Field(..., max_length=200)
    category: IngredientCategory


class IngredientNutrition(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str = Field(..., max_length=200)
    category: IngredientCategory
    calories_per_100g: float = Field(..., ge=0)
    protein_g_per_100g: float = Field(..., ge=0)
    fat_g_per_100g: float = Field(..., ge=0)
    carbs_g_per_100g: float = Field(..., ge=0)


class IngredientCreate(IngredientBase):
    calories_per_100g: float = Field(..., ge=0)
    protein_g_per_100g: float = Field(..., ge=0)
    fat_g_per_100g: float = Field(..., ge=0)
    carbs_g_per_100g: float = Field(..., ge=0)


class MealIngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ingredient_name: str
    category: IngredientCategory
    quantity_g: float = Field(..., ge=0)
    calories: float = Field(..., description="Calories from this ingredient quantity")
    protein_g: float = Field(..., description="Protein from this ingredient quantity")
    fat_g: float = Field(..., description="Fat from this ingredient quantity")
    carbs_g: float = Field(..., description="Carbs from this ingredient quantity")


class MealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    meal_type: MealType
    diet_tags: list[str]
    ingredients: list[MealIngredientOut] = Field(default_factory=list)


class MealSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    meal_type: MealType
    diet_tags: list[str]


class OptimizerType(str, Enum):
    greedy = "greedy"
    lp = "lp"


class MealPlanRequest(BaseModel):
    target_calories: float = Field(..., gt=0)
    target_protein_g: float | None = Field(default=None, gt=0)
    target_fat_g: float | None = Field(default=None, gt=0)
    target_carbs_g: float | None = Field(default=None, gt=0)
    meal_count: int = Field(default=3, ge=2, le=5)
    diet_tags: list[str] | None = None
    optimizer: OptimizerType = Field(default=OptimizerType.greedy)


class MealPlanSlotOut(BaseModel):
    meal_type: MealType
    target_calories: float
    meal: MealOut | None
    relaxed_filters: bool = False


class MealPlanResponse(BaseModel):
    slots: list[MealPlanSlotOut]
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
