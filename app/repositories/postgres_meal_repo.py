from sqlalchemy.orm import Session, joinedload

from app.models.meal import Meal, MealType
from app.models.meal_ingredient import MealIngredient
from app.repositories.base import MealRepository


class PostgresMealRepository(MealRepository):
    """Reads meals from the curated `meals` table via SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def _with_ingredients(self, query):
        """Add eager loading for ingredients."""
        return query.options(
            joinedload(Meal.meal_ingredients).joinedload(MealIngredient.ingredient)
        )

    def list_meals(
        self,
        meal_type: MealType | None = None,
        diet_tags: list[str] | None = None,
    ) -> list[Meal]:
        query = self.db.query(Meal)
        if meal_type is not None:
            query = query.filter(Meal.meal_type == meal_type)
        if diet_tags:
            query = query.filter(Meal.diet_tags.contains(diet_tags))
        return self._with_ingredients(query).all()

    def get_meal(self, meal_id: int) -> Meal | None:
        return self._with_ingredients(
            self.db.query(Meal).filter(Meal.id == meal_id)
        ).first()
