from fastapi import APIRouter

from app.schemas.calculator import (
    BodyStatsRequest,
    CalorieTargetRequest,
    CalorieTargetResponse,
    TDEEResponse,
)
from app.services.macro_calculator import build_target
from app.services.tdee_calculator import calculate_bmr, calculate_tdee

router = APIRouter(prefix="/calculate", tags=["calculator"])


@router.post("/tdee", response_model=TDEEResponse)
def calculate_tdee_endpoint(body: BodyStatsRequest) -> TDEEResponse:
    bmr = calculate_bmr(
        weight_kg=body.weight_kg, height_cm=body.height_cm, age=body.age, sex=body.sex
    )
    tdee = calculate_tdee(
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        age=body.age,
        sex=body.sex,
        activity_level=body.activity_level,
    )
    return TDEEResponse(bmr=round(bmr, 1), tdee=round(tdee, 1))


@router.post("/calorie-target", response_model=CalorieTargetResponse)
def calculate_calorie_target_endpoint(body: CalorieTargetRequest) -> CalorieTargetResponse:
    tdee = calculate_tdee(
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        age=body.age,
        sex=body.sex,
        activity_level=body.activity_level,
    )
    target = build_target(
        tdee=tdee,
        weight_kg=body.weight_kg,
        goal=body.goal,
        rate_kg_per_week=body.rate_kg_per_week,
    )
    return CalorieTargetResponse(
        tdee=round(tdee, 1),
        target_calories=target.calories,
        protein_g=target.protein_g,
        fat_g=target.fat_g,
        carbs_g=target.carbs_g,
        capped_for_safety=target.capped_for_safety,
    )
