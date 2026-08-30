
from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MealIngredient(Base):
    __tablename__ = "meal_ingredients"

    meal_id: Mapped[int] = mapped_column(
        ForeignKey("meals.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="RESTRICT"), primary_key=True
    )
    quantity_g: Mapped[float] = mapped_column(Float, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    meal: Mapped["Meal"] = relationship("Meal", back_populates="meal_ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="meal_ingredients")

    def __repr__(self) -> str:
        return f"<MealIngredient meal={self.meal_id} ing={self.ingredient_id} qty={self.quantity_g}g>"

    @property
    def ingredient_name(self) -> str:
        return self.ingredient.name if self.ingredient else "Unknown"

    def calculate_nutrition(self) -> dict[str, float]:
        if not self.ingredient:
            return {"calories": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0}
        ratio = self.quantity_g / 100.0
        return {
            "calories": round(self.ingredient.calories_per_100g * ratio, 2),
            "protein_g": round(self.ingredient.protein_g_per_100g * ratio, 2),
            "fat_g": round(self.ingredient.fat_g_per_100g * ratio, 2),
            "carbs_g": round(self.ingredient.carbs_g_per_100g * ratio, 2),
        }
