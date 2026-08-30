from __future__ import annotations

from sqlalchemy import Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import IngredientCategory


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[IngredientCategory] = mapped_column(
        Enum(IngredientCategory, name="ingredient_category"), nullable=False, index=True
    )
    calories_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    serving_size_default_g: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)

    meal_ingredients: Mapped[list["MealIngredient"]] = relationship(
        "MealIngredient",
        back_populates="ingredient",
        foreign_keys="MealIngredient.ingredient_id",
    )

    def __repr__(self) -> str:
        return f"<Ingredient {self.name!r}>"

    def calculate_nutrition(self, quantity_g: float) -> dict[str, float]:
        ratio = quantity_g / 100.0
        return {
            "calories": round(self.calories_per_100g * ratio, 2),
            "protein_g": round(self.protein_g_per_100g * ratio, 2),
            "fat_g": round(self.fat_g_per_100g * ratio, 2),
            "carbs_g": round(self.carbs_g_per_100g * ratio, 2),
        }
