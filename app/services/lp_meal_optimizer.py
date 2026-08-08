"""
Linear Programming Meal Optimizer.

Solves the meal plan selection as a Mixed Integer Linear Program (MILP),
selecting meals to minimize weighted deviation from macro targets.

Uses Google OR-Tools as the solver backend.

Configuration is loaded from (in priority order):
1. Runtime overrides via `PUT /api/v1/admin/lp-weights`
2. `config/lp_weights.yaml` (YAML config file)
3. Hard-coded defaults (ultimate fallback)
"""

from ortools.linear_solver import pywraplp
from dataclasses import dataclass

from app.models.meal import Meal, MealType
from app.repositories.base import MealRepository

from app.services.lp_weights_service import get_lp_weights_service


@dataclass
class MacroTargets:
    """Target macros for a meal plan."""
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float


@dataclass
class LPMealPlanResult:
    """Result from the LP optimizer."""
    meals: list[Meal]
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    objective_value: float
    optimal: bool


class LPMealOptimizer:
    """
    Linear programming optimizer for meal plan generation.

    Formulation:
    - Decision variables: x_i (binary) = 1 if meal i is selected
    - Objective: minimize weighted sum of absolute deviations from targets
    - Constraints: exactly one meal per required meal type

    Falls back to greedy if LP fails or no solution found.
    """

    def __init__(
        self,
        repository: MealRepository,
        targets: MacroTargets,
        meal_count: int,
        diet_tags: list[str] | None = None,
    ):
        self.repository = repository
        self.targets = targets
        self.meal_count = meal_count
        self.diet_tags = diet_tags

        # Load weights from the weights service (YAML config + runtime overrides)
        weights_service = get_lp_weights_service()
        self.weights = weights_service.get_weights()
        self.solver_settings = weights_service.get_solver_settings()

    def solve(self) -> LPMealPlanResult | None:
        """Solve the LP and return selected meals, or None if infeasible."""
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if solver is None:
            return None

        # Set solver time limit (convert seconds to milliseconds)
        time_limit_ms = int(self.solver_settings.get("time_limit_seconds", 30) * 1000)
        solver.SetTimeLimit(time_limit_ms)

        meals = self._fetch_candidates()
        x_i = {}
        for meal_type, meal_list in meals.items():
            x_i[meal_type] = {} 
            for meal in meal_list:
                    x_i[meal_type][meal.id] = solver.BoolVar(f"x_{meal_type}_{meal.id}")
    
        for meal_type, meal_vars in x_i.items():
            solver.Add(solver.Sum(meal_vars.values()) == 1)

        d_cal_pos = solver.NumVar(0, solver.infinity(), "d_cal_pos")
        d_cal_neg = solver.NumVar(0, solver.infinity(), "d_cal_neg")
        d_protein_pos = solver.NumVar(0, solver.infinity(), "d_protein_pos")
        d_protein_neg = solver.NumVar(0, solver.infinity(), "d_protein_neg")
        d_fat_pos = solver.NumVar(0, solver.infinity(), "d_fat_pos")
        d_fat_neg = solver.NumVar(0, solver.infinity(), "d_fat_neg")
        d_carbs_pos = solver.NumVar(0, solver.infinity(), "d_carbs_pos")
        d_carbs_neg = solver.NumVar(0, solver.infinity(), "d_carbs_neg")


        solver.Add(
            solver.Sum(meal.calories * x_i[meal_type][meal.id]
                       for meal_type, meal_list in meals.items()
                       for meal in meal_list)
            - self.targets.calories
            == d_cal_pos - d_cal_neg
            )
        solver.Add(solver.Sum(meal.protein_g * x_i[meal_type][meal.id]
                              for meal_type, meal_list in meals.items()
                              for meal in meal_list) - self.targets.protein_g
            == d_protein_pos - d_protein_neg)
        solver.Add(solver.Sum(meal.fat_g * x_i[meal_type][meal.id]
                              for meal_type, meal_list in meals.items()
                              for meal in meal_list) - self.targets.fat_g
            == d_fat_pos - d_fat_neg)
        solver.Add(solver.Sum(meal.carbs_g * x_i[meal_type][meal.id]
                              for meal_type, meal_list in meals.items()
                              for meal in meal_list) - self.targets.carbs_g
            == d_carbs_pos - d_carbs_neg) 

        objective = solver.Objective()
        objective.SetMinimization()
        objective.SetCoefficient(d_cal_pos, self.weights.get("calories", 1.0))
        objective.SetCoefficient(d_cal_neg, self.weights.get("calories", 1.0))
        objective.SetCoefficient(d_carbs_pos, self.weights.get("carbs", 1.0))
        objective.SetCoefficient(d_carbs_neg, self.weights.get("carbs", 1.0))
        objective.SetCoefficient(d_protein_neg, self.weights.get("protein", 1.0))
        objective.SetCoefficient(d_protein_pos, self.weights.get("protein", 1.0))
        objective.SetCoefficient(d_fat_neg, self.weights.get("fat", 1.0))
        objective.SetCoefficient(d_fat_pos, self.weights.get("fat", 1.0))

        result = solver.Solve()
        if result != solver.OPTIMAL and result != solver.FEASIBLE:
            return None
        selected = self._extract_solution(x_i, meals)
        total_cal, total_protein, total_fat, total_carbs = self._calculate_totals(selected)
        return LPMealPlanResult(
            meals=selected,
            total_calories=total_cal,
            total_carbs_g=total_carbs,
            total_protein_g=total_protein,
            total_fat_g=total_fat,
            objective_value=solver.Objective().Value(),
            optimal=(result == solver.OPTIMAL)
        )

    def _get_required_meal_types(self) -> list[MealType]:
        """Map meal_count to required meal types.

        Meal sequence:
        - 2 meals -> [lunch, dinner]
        - 3 meals -> [breakfast, lunch, dinner]
        - 4 meals -> [breakfast, lunch, dinner, snack]
        - 5 meals -> [breakfast, snack, lunch, dinner, snack]
        """
        if self.meal_count == 2:
            return [MealType.lunch, MealType.dinner]
        elif self.meal_count == 3:
            return [MealType.breakfast, MealType.lunch, MealType.dinner]
        elif self.meal_count == 4:
            return [MealType.breakfast, MealType.lunch, MealType.dinner, MealType.snack]
        elif self.meal_count == 5:
            return [
                MealType.breakfast,
                MealType.snack,
                MealType.lunch,
                MealType.dinner,
                MealType.snack,
            ]
        else:
            # Fall back to closest supported meal count
            closest = min([2, 3, 4, 5], key=lambda n: abs(n - self.meal_count))
            return self._get_required_meal_types_for_count(closest)

    def _get_required_meal_types_for_count(self, count: int) -> list[MealType]:
        """Get meal types for a specific meal count."""
        mapping = {
            2: [MealType.lunch, MealType.dinner],
            3: [MealType.breakfast, MealType.lunch, MealType.dinner],
            4: [MealType.breakfast, MealType.lunch, MealType.dinner, MealType.snack],
            5: [MealType.breakfast, MealType.snack, MealType.lunch, MealType.dinner, MealType.snack],
        }
        return mapping[count]

    def _fetch_candidates(self) -> dict[MealType, list[Meal]]:
        """Fetch candidate meals from repository, grouped by type.

        For each required meal type:
        1. Try to get meals matching both meal_type AND diet_tags
        2. If no results, fall back to meal_type only (relaxed filters)
        """
        candidates = {}
        for meal_type in self._get_required_meal_types():
            meals = self.repository.list_meals(meal_type=meal_type, diet_tags=self.diet_tags)
            if not meals:
                meals = self.repository.list_meals(meal_type=meal_type, diet_tags=None)
            candidates[meal_type] = meals
        return candidates

    def _extract_solution(
        self,
        x_i: dict[MealType, dict[int, pywraplp.Variable]],
        meals: dict[MealType, list[Meal]],
    ) -> list[Meal]:
        """
        Extract selected meals from solved variables.

        Args:
            x_i: Dict of {meal_type: {meal_id: BoolVar}} created in solve()
            meals: Dict of {meal_type: [Meal]} candidate meals

        Returns:
            List of selected Meal objects where the binary variable = 1.
        """
        selected = []
        # Build a lookup: meal_id -> Meal object
        meal_lookup: dict[int, Meal] = {}
        for meal_type, meal_list in meals.items():
            for meal in meal_list:
                meal_lookup[meal.id] = meal

        # Collect meals where the variable is selected (value close to 1)
        for meal_type, var_dict in x_i.items():
            for meal_id, var in var_dict.items():
                if var.solution_value() > 0.5:
                    if meal_id in meal_lookup:
                        selected.append(meal_lookup[meal_id])
                    else:
                        # Fallback: find meal in the original list
                        for meal_list in meals.values():
                            for meal in meal_list:
                                if meal.id == meal_id:
                                    selected.append(meal)
                                    break

        return selected

    def _calculate_totals(self, meals: list[Meal]) -> tuple[float, float, float, float]:
        """Calculate total macros for selected meals."""
        sum_calories = sum(meal.calories for meal in meals)
        sum_protein = sum(meal.protein_g for meal in meals)
        sum_fat = sum(meal.fat_g for meal in meals)
        sum_carbs = sum(meal.carbs_g for meal in meals)
        return sum_calories, sum_protein, sum_fat, sum_carbs

def optimize_meal_plan_lp(
    repository: MealRepository,
    target_calories: float,
    target_protein_g: float,
    target_fat_g: float,
    target_carbs_g: float,
    meal_count: int,
    diet_tags: list[str] | None = None,
) -> LPMealPlanResult | None:
    """
    Convenience wrapper to run LP optimization.

    Args:
        repository: MealRepository to fetch candidate meals
        target_calories: Daily calorie target
        target_protein_g: Daily protein target in grams
        target_fat_g: Daily fat target in grams
        target_carbs_g: Daily carbs target in grams
        meal_count: Number of meals (2-5)
        diet_tags: Optional diet filters (e.g., ["high_protein", "vegetarian"])

    Returns:
        LPMealPlanResult with selected meals, or None if infeasible.

    This is the main entry point called from meal_plan_generator.py.
    """
    macro_targets = MacroTargets(
        calories=target_calories,
        protein_g=target_protein_g,
        fat_g=target_fat_g,
        carbs_g=target_carbs_g
    )
    optimizer = LPMealOptimizer(
        repository=repository,
        targets=macro_targets,
        meal_count=meal_count,
        diet_tags=diet_tags,
    )

    return optimizer.solve()
