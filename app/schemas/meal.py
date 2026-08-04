from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings
from app.models.meal import MealType


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


class OptimizerType(str, Enum):
    greedy = "greedy"
    lp = "lp"


class MealPlanRequest(BaseModel):
    target_calories: float = Field(..., gt=0)
    # Optional macro targets for LP optimizer. If not provided, LP will
    # derive protein/fat/carbs targets from defaults in config.
    target_protein_g: float | None = Field(default=None, gt=0)
    target_fat_g: float | None = Field(default=None, gt=0)
    target_carbs_g: float | None = Field(default=None, gt=0)
    meal_count: int = Field(default=settings.default_meal_count, ge=2, le=5)
    diet_tags: list[str] | None = Field(
        default=None, description="e.g. ['high_protein', 'low_fat']"
    )
    optimizer: OptimizerType = Field(
        default=OptimizerType.greedy,
        description="'greedy' = nearest-calorie per slot (fast, simple). 'lp' = globally optimized via linear programming (better macro matching).",
    )


class MealPlanSlotOut(BaseModel):
    meal_type: MealType
    target_calories: float
    meal: MealOut | None
    relaxed_filters: bool = Field(
        description="True if no meal matched every requested diet tag, so the tag filter was relaxed for this slot"
    )


class MealPlanResponse(BaseModel):
    slots: list[MealPlanSlotOut]
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
