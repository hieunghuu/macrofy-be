from dataclasses import dataclass

from app.models.meal import Meal, MealType
from app.repositories.base import MealRepository

# Which meal types make up a day, depending on how many meals the user wants.
# This is domain/product logic (how a day's calories get split into named
# meals), not deployment config, so it lives in code.
_MEAL_SEQUENCES: dict[int, list[MealType]] = {
    2: [MealType.lunch, MealType.dinner],
    3: [MealType.breakfast, MealType.lunch, MealType.dinner],
    4: [MealType.breakfast, MealType.lunch, MealType.dinner, MealType.snack],
    5: [
        MealType.breakfast,
        MealType.snack,
        MealType.lunch,
        MealType.dinner,
        MealType.snack,
    ],
}


@dataclass
class MealPlanSlot:
    meal_type: MealType
    meal: Meal | None
    target_calories: float
    relaxed_filters: bool = False


@dataclass
class MealPlanResult:
    slots: list[MealPlanSlot]
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float


def generate_meal_plan(
    *,
    repository: MealRepository,
    target_calories: float,
    meal_count: int,
    diet_tags: list[str] | None = None,
) -> MealPlanResult:
    sequence = _MEAL_SEQUENCES.get(meal_count)
    if sequence is None:
        # Fall back to the closest supported meal count instead of failing.
        closest = min(_MEAL_SEQUENCES, key=lambda n: abs(n - meal_count))
        sequence = _MEAL_SEQUENCES[closest]

    per_meal_target = target_calories / len(sequence)

    slots: list[MealPlanSlot] = []
    for meal_type in sequence:
        candidates = repository.list_meals(meal_type=meal_type, diet_tags=diet_tags)
        relaxed = False

        if not candidates:
            # Keep the plan complete even if nothing matches every
            # preference: relax the diet-tag filter but keep the meal type.
            candidates = repository.list_meals(meal_type=meal_type, diet_tags=None)
            relaxed = True

        best_meal = min(
            candidates,
            key=lambda m: abs(m.calories - per_meal_target),
            default=None,
        )

        slots.append(
            MealPlanSlot(
                meal_type=meal_type,
                meal=best_meal,
                target_calories=round(per_meal_target),
                relaxed_filters=relaxed,
            )
        )

    filled = [s.meal for s in slots if s.meal is not None]
    return MealPlanResult(
        slots=slots,
        total_calories=sum(m.calories for m in filled),
        total_protein_g=sum(m.protein_g for m in filled),
        total_fat_g=sum(m.fat_g for m in filled),
        total_carbs_g=sum(m.carbs_g for m in filled),
    )
