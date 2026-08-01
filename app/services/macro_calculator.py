from dataclasses import dataclass
from enum import Enum

from app.core.config import settings


class Goal(str, Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"


@dataclass
class MacroTarget:
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    capped_for_safety: bool = False


def calculate_calorie_target(
    *, tdee: float, goal: Goal, rate_kg_per_week: float | None = None
) -> tuple[float, bool]:
    """
    Returns (target_calories, was_capped_for_safety).
    rate_kg_per_week is only used for lose/gain goals; falls back to the
    configured default when omitted.
    """
    if goal == Goal.maintain:
        return tdee, False

    rate = rate_kg_per_week if rate_kg_per_week is not None else settings.default_rate_kg_per_week
    daily_adjustment = (rate * settings.kcal_per_kg_fat) / 7

    if goal == Goal.lose:
        target = tdee - daily_adjustment
        if target < settings.min_safe_calories:
            return settings.min_safe_calories, True
        return target, False

    # gain
    return tdee + daily_adjustment, False


def calculate_macros(
    *,
    target_calories: float,
    weight_kg: float,
    protein_g_per_kg: float | None = None,
    fat_percent: float | None = None,
) -> MacroTarget:
    protein_g_per_kg = (
        protein_g_per_kg if protein_g_per_kg is not None else settings.default_protein_g_per_kg
    )
    fat_percent = fat_percent if fat_percent is not None else settings.default_fat_percent

    protein_g = weight_kg * protein_g_per_kg
    protein_cal = protein_g * 4

    fat_cal = target_calories * fat_percent
    fat_g = fat_cal / 9

    # Whatever's left after protein and fat goes to carbs; never negative
    # (a very low target combined with a high protein/fat ask can otherwise
    # produce nonsense numbers).
    remaining_cal = target_calories - protein_cal - fat_cal
    carbs_g = max(remaining_cal, 0) / 4

    return MacroTarget(
        calories=round(target_calories),
        protein_g=round(protein_g, 1),
        fat_g=round(fat_g, 1),
        carbs_g=round(carbs_g, 1),
    )


def build_target(
    *,
    tdee: float,
    weight_kg: float,
    goal: Goal,
    rate_kg_per_week: float | None = None,
    protein_g_per_kg: float | None = None,
    fat_percent: float | None = None,
) -> MacroTarget:
    """Combines calorie-target and macro-split calculation into one call."""
    target_calories, capped = calculate_calorie_target(
        tdee=tdee, goal=goal, rate_kg_per_week=rate_kg_per_week
    )
    macros = calculate_macros(
        target_calories=target_calories,
        weight_kg=weight_kg,
        protein_g_per_kg=protein_g_per_kg,
        fat_percent=fat_percent,
    )
    macros.capped_for_safety = capped
    return macros
