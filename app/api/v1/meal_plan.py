from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.meal import MealType
from app.repositories.postgres_meal_repo import PostgresMealRepository
from app.schemas.meal import MealOut, MealPlanRequest, MealPlanResponse, MealPlanSlotOut
from app.services.meal_plan_generator import generate_meal_plan

router = APIRouter(tags=["meals"])


@router.get("/meals", response_model=list[MealOut])
def list_meals(
    meal_type: MealType | None = None,
    tag: list[str] | None = Query(
        default=None, description="Repeatable, e.g. ?tag=high_protein&tag=low_fat"
    ),
    db: Session = Depends(get_db),
) -> list[MealOut]:
    repo = PostgresMealRepository(db)
    return repo.list_meals(meal_type=meal_type, diet_tags=tag)


@router.post("/meal-plan/generate", response_model=MealPlanResponse)
def generate_meal_plan_endpoint(
    body: MealPlanRequest,
    db: Session = Depends(get_db),
) -> MealPlanResponse:
    repo = PostgresMealRepository(db)
    use_lp = body.optimizer == "lp"
    result = generate_meal_plan(
        repository=repo,
        target_calories=body.target_calories,
        target_protein_g=body.target_protein_g,
        target_fat_g=body.target_fat_g,
        target_carbs_g=body.target_carbs_g,
        meal_count=body.meal_count,
        diet_tags=body.diet_tags,
        use_lp=use_lp,
    )
    return MealPlanResponse(
        slots=[
            MealPlanSlotOut(
                meal_type=s.meal_type,
                target_calories=s.target_calories,
                meal=s.meal,
                relaxed_filters=s.relaxed_filters,
            )
            for s in result.slots
        ],
        total_calories=result.total_calories,
        total_protein_g=result.total_protein_g,
        total_fat_g=result.total_fat_g,
        total_carbs_g=result.total_carbs_g,
    )
