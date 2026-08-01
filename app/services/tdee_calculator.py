from enum import Enum


class Sex(str, Enum):
    male = "male"
    female = "female"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"


# Standard Mifflin-St Jeor activity multipliers. These define the formula
# itself (not deployment config) so they live in code, not env vars.
_ACTIVITY_MULTIPLIERS: dict[ActivityLevel, float] = {
    ActivityLevel.sedentary: 1.2,
    ActivityLevel.light: 1.375,
    ActivityLevel.moderate: 1.55,
    ActivityLevel.active: 1.725,
    ActivityLevel.very_active: 1.9,
}


def calculate_bmr(*, weight_kg: float, height_cm: float, age: int, sex: Sex) -> float:
    """Mifflin-St Jeor equation for basal metabolic rate."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == Sex.male else base - 161


def calculate_tdee(
    *,
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: Sex,
    activity_level: ActivityLevel,
) -> float:
    bmr = calculate_bmr(weight_kg=weight_kg, height_cm=height_cm, age=age, sex=sex)
    return bmr * _ACTIVITY_MULTIPLIERS[activity_level]
