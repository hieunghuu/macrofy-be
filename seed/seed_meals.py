"""
Populates the meals table with the curated starter data.
Safe to re-run: it clears existing rows first.

Usage:
    python -m seed.seed_meals
"""

from app.db.session import SessionLocal
from app.models.meal import Meal
from seed.meals_data import MEALS
from sqlalchemy import text

def run() -> None:
    db = SessionLocal()
    try:
        db.query(Meal).delete()
        db.execute(
            text("ALTER SEQUENCE meals_id_seq RESTART WITH 1")
        )
        db.add_all([Meal(**meal_kwargs) for meal_kwargs in MEALS])
        db.commit()
        count = db.query(Meal).count()
        print(f"Seeded {count} meals.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
