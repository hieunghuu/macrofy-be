"""
Tests for the LP Meal Optimizer.

Run with: python -m pytest tests/test_lp_meal_optimizer.py -v
"""
import pytest

from app.services.lp_meal_optimizer import (
    LPMealOptimizer,
    MacroTargets,
    LPMealPlanResult,
)
from app.models.meal import Meal, MealType
from app.repositories.base import MealRepository


class MockMealRepository(MealRepository):
    """In-memory mock repository for testing."""

    def __init__(self, meals: list[Meal] | None = None):
        self._meals = meals or []

    def list_meals(
        self,
        meal_type: MealType | None = None,
        diet_tags: list[str] | None = None,
    ) -> list[Meal]:
        result = self._meals
        if meal_type:
            result = [m for m in result if m.meal_type == meal_type]
        if diet_tags:
            result = [m for m in result if all(t in m.diet_tags for t in diet_tags)]
        return result

    def get_meal(self, meal_id: int) -> Meal | None:
        return next((m for m in self._meals if m.id == meal_id), None)


def make_meal(
    meal_id: int,
    name: str,
    meal_type: MealType,
    calories: float,
    protein_g: float,
    fat_g: float,
    carbs_g: float,
    diet_tags: list[str] | None = None,
) -> Meal:
    """Factory helper to create test Meal objects."""
    return Meal(
        id=meal_id,
        name=name,
        description=None,
        calories=calories,
        protein_g=protein_g,
        fat_g=fat_g,
        carbs_g=carbs_g,
        meal_type=meal_type,
        diet_tags=diet_tags or [],
    )


class TestLPMealOptimizer:
    """Test suite for LPMealOptimizer."""

    @pytest.fixture
    def three_meals(self) -> list[Meal]:
        """Three meals, one per required type for a 3-meal plan."""
        return [
            make_meal(1, "Oatmeal", MealType.breakfast,
                      calories=400, protein_g=15, fat_g=10, carbs_g=60),
            make_meal(2, "Chicken Salad", MealType.lunch,
                      calories=450, protein_g=35, fat_g=18, carbs_g=30),
            make_meal(3, "Grilled Salmon", MealType.dinner,
                      calories=600, protein_g=45, fat_g=25, carbs_g=40),
        ]

    @pytest.fixture
    def many_meals_per_type(self) -> list[Meal]:
        """Multiple meal options per type (optimizer should choose best fit)."""
        return [
            # Breakfast options
            make_meal(1, "Oatmeal", MealType.breakfast,
                      calories=350, protein_g=12, fat_g=8, carbs_g=55),
            make_meal(2, "Eggs & Toast", MealType.breakfast,
                      calories=450, protein_g=25, fat_g=22, carbs_g=35),
            make_meal(3, "Greek Yogurt", MealType.breakfast,
                      calories=300, protein_g=20, fat_g=8, carbs_g=40),
            # Lunch options
            make_meal(4, "Chicken Salad", MealType.lunch,
                      calories=400, protein_g=35, fat_g=15, carbs_g=25),
            make_meal(5, "Turkey Wrap", MealType.lunch,
                      calories=500, protein_g=28, fat_g=22, carbs_g=45),
            make_meal(6, "Veggie Soup", MealType.lunch,
                      calories=350, protein_g=15, fat_g=12, carbs_g=50),
            # Dinner options
            make_meal(7, "Grilled Salmon", MealType.dinner,
                      calories=550, protein_g=45, fat_g=25, carbs_g=30),
            make_meal(8, "Pasta Primavera", MealType.dinner,
                      calories=650, protein_g=22, fat_g=20, carbs_g=85),
            make_meal(9, "Lean Steak & Veg", MealType.dinner,
                      calories=600, protein_g=50, fat_g=30, carbs_g=25),
        ]

    @pytest.fixture
    def targets(self) -> MacroTargets:
        """Reasonable daily macro targets for a 3-meal plan."""
        return MacroTargets(
            calories=1500,
            protein_g=100,
            fat_g=60,
            carbs_g=150,
        )

    def test_solve_returns_result(self, three_meals, targets):
        """solve() returns a valid LPMealPlanResult."""
        repo = MockMealRepository(meals=three_meals)
        optimizer = LPMealOptimizer(repo, targets, meal_count=3)
        result = optimizer.solve()

        assert result is not None
        assert isinstance(result, LPMealPlanResult)

    def test_solve_selects_correct_count(self, many_meals_per_type, targets):
        """Exactly meal_count meals are selected."""
        repo = MockMealRepository(meals=many_meals_per_type)
        optimizer = LPMealOptimizer(repo, targets, meal_count=3)
        result = optimizer.solve()

        assert result is not None
        assert len(result.meals) == 3

    def test_solve_respects_meal_types(self, many_meals_per_type, targets):
        """One meal per required type is selected."""
        repo = MockMealRepository(meals=many_meals_per_type)
        optimizer = LPMealOptimizer(repo, targets, meal_count=3)
        result = optimizer.solve()

        assert result is not None
        selected_types = {m.meal_type for m in result.meals}
        assert MealType.breakfast in selected_types
        assert MealType.lunch in selected_types
        assert MealType.dinner in selected_types

    def test_solve_totals_match_meals(self, many_meals_per_type, targets):
        """Reported totals match the sum of selected meal macros."""
        repo = MockMealRepository(meals=many_meals_per_type)
        optimizer = LPMealOptimizer(repo, targets, meal_count=3)
        result = optimizer.solve()

        assert result is not None
        expected_cal = sum(m.calories for m in result.meals)
        expected_protein = sum(m.protein_g for m in result.meals)
        expected_fat = sum(m.fat_g for m in result.meals)
        expected_carbs = sum(m.carbs_g for m in result.meals)

        assert abs(result.total_calories - expected_cal) < 0.01
        assert abs(result.total_protein_g - expected_protein) < 0.01
        assert abs(result.total_fat_g - expected_fat) < 0.01
        assert abs(result.total_carbs_g - expected_carbs) < 0.01

    def test_solve_infeasible_no_meals(self, targets):
        """Returns None when no meals are available."""
        repo = MockMealRepository(meals=[])
        optimizer = LPMealOptimizer(repo, targets, meal_count=3)
        result = optimizer.solve()

        # Empty catalog makes the model infeasible
        assert result is None

    def test_solve_infeasible_missing_type(self, three_meals, targets):
        """Returns None when no meals for a required type."""
        # Only breakfast meals available, but we need 3 types
        repo = MockMealRepository(meals=[three_meals[0]])
        optimizer = LPMealOptimizer(repo, targets, meal_count=3)
        result = optimizer.solve()

        assert result is None

    def test_calculate_totals(self):
        """_calculate_totals correctly sums macros."""
        meals = [
            make_meal(1, "A", MealType.breakfast,
                      calories=100, protein_g=10, fat_g=5, carbs_g=20),
            make_meal(2, "B", MealType.lunch,
                      calories=200, protein_g=20, fat_g=10, carbs_g=30),
        ]
        repo = MockMealRepository(meals=meals)
        optimizer = LPMealOptimizer(repo, MacroTargets(0, 0, 0, 0), meal_count=2)
        totals = optimizer._calculate_totals(meals)

        assert totals == (300.0, 30.0, 15.0, 50.0)
    def test_get_required_meal_types_1(self):
        """meal_count=1 returns still return [lunch, dinner]."""
        repo = MockMealRepository(meals=[])
        optimizer = LPMealOptimizer(repo, MacroTargets(0, 0, 0, 0), meal_count=1)
        assert optimizer._get_required_meal_types() == [MealType.lunch, MealType.dinner]

    def test_get_required_meal_types_2(self):
        """meal_count=2 returns [lunch, dinner]."""
        repo = MockMealRepository(meals=[])
        optimizer = LPMealOptimizer(repo, MacroTargets(0, 0, 0, 0), meal_count=2)
        assert optimizer._get_required_meal_types() == [MealType.lunch, MealType.dinner]

    def test_get_required_meal_types_3(self):
        """meal_count=3 returns [breakfast, lunch, dinner]."""
        repo = MockMealRepository(meals=[])
        optimizer = LPMealOptimizer(repo, MacroTargets(0, 0, 0, 0), meal_count=3)
        assert optimizer._get_required_meal_types() == [MealType.breakfast, MealType.lunch, MealType.dinner]

    def test_get_required_meal_types_5(self):
        """meal_count=5 returns the 5-meal sequence."""
        repo = MockMealRepository(meals=[])
        optimizer = LPMealOptimizer(repo, MacroTargets(0, 0, 0, 0), meal_count=5)
        assert optimizer._get_required_meal_types() == [
            MealType.breakfast, MealType.snack, MealType.lunch,
            MealType.dinner, MealType.snack,
        ]

    def test_get_required_meal_types_6(self):
        """meal_count=6 still return the 5-meal sequence."""
        repo = MockMealRepository(meals=[])
        optimizer = LPMealOptimizer(repo, MacroTargets(0, 0, 0, 0), meal_count=6)
        assert optimizer._get_required_meal_types() == [
            MealType.breakfast, MealType.snack, MealType.lunch,
            MealType.dinner, MealType.snack,
        ]
