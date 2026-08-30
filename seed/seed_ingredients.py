from app.db.session import SessionLocal
from app.models.ingredient import Ingredient
from app.models.meal_ingredient import MealIngredient
from seed.ingredients_data import get_ingredient_kwargs_list


def run() -> None:
    db = SessionLocal()
    try:
        # Delete meal_ingredients first (foreign key constraint)
        db.query(MealIngredient).delete()
        db.commit()
        # Then delete ingredients
        db.query(Ingredient).delete()
        db.commit()
        # Insert new ingredients
        ingredients = [Ingredient(**kwargs) for kwargs in get_ingredient_kwargs_list()]
        db.add_all(ingredients)
        db.commit()
        count = db.query(Ingredient).count()
        print(f"Seeded {count} ingredients.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
