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


def generate_meal_plan_greedy(
    *,
    repository: MealRepository,
    target_calories: float,
    meal_count: int,
    diet_tags: list[str] | None = None,
) -> MealPlanResult:
    """
    Greedy meal plan generator: picks best meal per slot independently.

    This is the fast, simple fallback. It optimizes each meal slot in
    isolation (nearest calorie match), which may not globally optimize
    macro targets.
    """
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


def generate_meal_plan(
    *,
    repository: MealRepository,
    target_calories: float,
    target_protein_g: float | None = None,
    target_fat_g: float | None = None,
    target_carbs_g: float | None = None,
    meal_count: int,
    diet_tags: list[str] | None = None,
    use_lp: bool = False,
) -> MealPlanResult:
    """
    Generate a meal plan.

    Args:
        repository: Meal data source
        target_calories: Daily calorie target
        target_protein_g: Daily protein target (used by LP optimizer)
        target_fat_g: Daily fat target (used by LP optimizer)
        target_carbs_g: Daily carbs target (used by LP optimizer)
        meal_count: Number of meals (2-5)
        diet_tags: Filter meals by these tags
        use_lp: If True, use LP optimizer (better macro matching).
                 If False or LP unavailable, fall back to greedy.

    // TODO: Implement LP routing
    //
    // When use_lp=True and all macro targets are provided:
    // 1. Import and call optimize_meal_plan_lp()
    // 2. Convert LPMealPlanResult to MealPlanResult format
    // 3. Return the LP result
    //
    // When use_lp=True but LP fails:
    // 1. Log fallback (TODO: add logging)
    // 2. Fall back to greedy
    //
    // When use_lp=False or macro targets missing:
    // 1. Call generate_meal_plan_greedy()
    // 2. Return greedy result
    """
    if use_lp and target_protein_g is not None:
        # // TODO: Try LP optimization
        # try:
        #     from app.services.lp_meal_optimizer import optimize_meal_plan_lp
        #     lp_result = optimize_meal_plan_lp(
        #         repository=repository,
        #         target_calories=target_calories,
        #         target_protein_g=target_protein_g,
        #         target_fat_g=target_fat_g or 0,
        #         target_carbs_g=target_carbs_g or 0,
        #         meal_count=meal_count,
        #         diet_tags=diet_tags,
        #     )
        #     if lp_result:
        #         # Convert LPMealPlanResult -> MealPlanResult
        #         slots = [MealPlanSlot(...)]  # Build from lp_result.meals
        #         return MealPlanResult(...)
        # except ImportError:
        #     pass  # OR-Tools not installed, fall through to greedy
        pass

    # Fallback to greedy
    return generate_meal_plan_greedy(
        repository=repository,
        target_calories=target_calories,
        meal_count=meal_count,
        diet_tags=diet_tags,
    )
