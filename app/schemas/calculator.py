from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.macro_calculator import Goal
from app.services.tdee_calculator import ActivityLevel, Sex


class BodyStatsRequest(BaseModel):
    height_cm: float = Field(..., gt=0, le=272, description="Height in centimeters")
    weight_kg: float = Field(..., gt=0, le=300, description="Weight in kilograms")
    age: int = Field(..., ge=settings.min_user_age, le=100)
    sex: Sex
    activity_level: ActivityLevel


class TDEEResponse(BaseModel):
    bmr: float
    tdee: float


class CalorieTargetRequest(BodyStatsRequest):
    goal: Goal
    rate_kg_per_week: float = Field(
        default=settings.default_rate_kg_per_week,
        ge=0,
        le=1.0,
        description="Target rate of weight change per week; ignored for 'maintain'",
    )


class CalorieTargetResponse(BaseModel):
    tdee: float
    target_calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    capped_for_safety: bool = Field(
        description="True if the requested rate would have gone below the configured safe-calorie floor"
    )
