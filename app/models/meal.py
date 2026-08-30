from __future__ import annotations

from sqlalchemy import Boolean, Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import MealType


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    use_computed_macros: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    meal_type: Mapped[MealType] = mapped_column(
        Enum(MealType, name="meal_type"), nullable=False, index=True
    )
    diet_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list, server_default="'{}'"
    )

    meal_ingredients: Mapped[list["MealIngredient"]] = relationship(
        "MealIngredient", back_populates="meal", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Meal {self.name!r}>"

    @property
    def total_calories(self) -> float:
        if not self.meal_ingredients:
            return 0.0
        return sum(mi.ingredient.calories_per_100g * (mi.quantity_g / 100) for mi in self.meal_ingredients if mi.ingredient)

    @property
    def total_protein_g(self) -> float:
        if not self.meal_ingredients:
            return 0.0
        return sum(mi.ingredient.protein_g_per_100g * (mi.quantity_g / 100) for mi in self.meal_ingredients if mi.ingredient)

    @property
    def total_fat_g(self) -> float:
        if not self.meal_ingredients:
            return 0.0
        return sum(mi.ingredient.fat_g_per_100g * (mi.quantity_g / 100) for mi in self.meal_ingredients if mi.ingredient)

    @property
    def total_carbs_g(self) -> float:
        if not self.meal_ingredients:
            return 0.0
        return sum(mi.ingredient.carbs_g_per_100g * (mi.quantity_g / 100) for mi in self.meal_ingredients if mi.ingredient)

    @property
    def effective_calories(self) -> float:
        return round(self.total_calories, 2) if self.use_computed_macros else self.calories

    @property
    def effective_protein_g(self) -> float:
        return round(self.total_protein_g, 2) if self.use_computed_macros else self.protein_g

    @property
    def effective_fat_g(self) -> float:
        return round(self.total_fat_g, 2) if self.use_computed_macros else self.fat_g

    @property
    def effective_carbs_g(self) -> float:
        return round(self.total_carbs_g, 2) if self.use_computed_macros else self.carbs_g

    @property
    def ingredient_summary(self) -> list[dict]:
        return [
            {"name": mi.ingredient.name, "quantity_g": mi.quantity_g, "category": mi.ingredient.category.value if mi.ingredient else None}
            for mi in sorted(self.meal_ingredients, key=lambda x: x.order_index)
        ]

    def recalculate_and_store_macros(self) -> dict[str, float]:
        self.calories = round(self.total_calories, 2)
        self.protein_g = round(self.total_protein_g, 2)
        self.fat_g = round(self.total_fat_g, 2)
        self.carbs_g = round(self.total_carbs_g, 2)
        return {"calories": self.calories, "protein_g": self.protein_g, "fat_g": self.fat_g, "carbs_g": self.carbs_g}
