from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient, IngredientCategory
from app.repositories.base import IngredientRepository


class PostgresIngredientRepository(IngredientRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_ingredients(self, category: IngredientCategory | None = None, search: str | None = None) -> list[Ingredient]:
        query = self.db.query(Ingredient)
        if category is not None:
            query = query.filter(Ingredient.category == category)
        if search:
            query = query.filter(Ingredient.name.ilike(f"%{search}%"))
        return query.order_by(Ingredient.name).all()

    def get_ingredient(self, ingredient_id: int) -> Ingredient | None:
        return self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    def create_ingredient(self, ingredient_data: dict) -> Ingredient:
        ingredient = Ingredient(**ingredient_data)
        self.db.add(ingredient)
        self.db.flush()
        return ingredient

    def update_ingredient(self, ingredient_id: int, ingredient_data: dict) -> Ingredient | None:
        ingredient = self.get_ingredient(ingredient_id)
        if not ingredient:
            return None
        for key, value in ingredient_data.items():
            if hasattr(ingredient, key):
                setattr(ingredient, key, value)
        self.db.flush()
        return ingredient

    def delete_ingredient(self, ingredient_id: int) -> bool:
        ingredient = self.get_ingredient(ingredient_id)
        if not ingredient:
            return False
        self.db.delete(ingredient)
        self.db.flush()
        return True

    def count_ingredients(self, category: IngredientCategory | None = None) -> int:
        query = self.db.query(Ingredient)
        if category is not None:
            query = query.filter(Ingredient.category == category)
        return query.count()
