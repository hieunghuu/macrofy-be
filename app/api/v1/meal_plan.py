from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.meal import MealType
from app.repositories.postgres_meal_repo import PostgresMealRepository
from app.schemas.meal import (
    IngredientCategory,
    MealIngredientOut,
    MealOut,
    MealPlanRequest,
    MealPlanResponse,
    MealPlanSlotOut,
)
from app.services.meal_plan_generator import generate_meal_plan

router = APIRouter(tags=["meals"])


def _build_meal_out(meal) -> MealOut:
    """Build MealOut with ingredients array including gram quantities and nutrition."""
    ingredients = []
    if meal.meal_ingredients:
        for mi in sorted(meal.meal_ingredients, key=lambda x: x.order_index or 0):
            if mi.ingredient:
                nutrition = mi.calculate_nutrition()
                ingredients.append(MealIngredientOut(
                    ingredient_name=mi.ingredient.name,
                    category=mi.ingredient.category,
                    quantity_g=mi.quantity_g,
                    calories=nutrition["calories"],
                    protein_g=nutrition["protein_g"],
                    fat_g=nutrition["fat_g"],
                    carbs_g=nutrition["carbs_g"],
                ))
    return MealOut(
        id=meal.id,
        name=meal.name,
        description=meal.description,
        calories=meal.calories,
        protein_g=meal.protein_g,
        fat_g=meal.fat_g,
        carbs_g=meal.carbs_g,
        meal_type=meal.meal_type,
        diet_tags=meal.diet_tags,
        ingredients=ingredients,
    )


@router.get("/meals", response_model=list[MealOut])
def list_meals(
    meal_type: MealType | None = None,
    tag: list[str] | None = Query(
        default=None, description="Repeatable, e.g. ?tag=high_protein&tag=low_fat"
    ),
    db: Session = Depends(get_db),
) -> list[MealOut]:
    repo = PostgresMealRepository(db)
    meals = repo.list_meals(meal_type=meal_type, diet_tags=tag)
    return [_build_meal_out(m) for m in meals]


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
                meal=_build_meal_out(s.meal) if s.meal else None,
                relaxed_filters=s.relaxed_filters,
            )
            for s in result.slots
        ],
        total_calories=result.total_calories,
        total_protein_g=result.total_protein_g,
        total_fat_g=result.total_fat_g,
        total_carbs_g=result.total_carbs_g,
    )
