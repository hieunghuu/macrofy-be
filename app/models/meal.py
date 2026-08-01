import enum

from sqlalchemy import Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class Meal(Base):
    """
    A single curated meal in the catalog. This is the data the meal-plan
    generator selects from -- swapping this out for an external nutrition
    API later just means writing a new repository, not changing this model.
    """

    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)

    meal_type: Mapped[MealType] = mapped_column(
        Enum(MealType, name="meal_type"), nullable=False, index=True
    )

    # e.g. ["high_protein", "low_fat", "vegetarian"]
    # Postgres-specific ARRAY type -- fine since we're committed to Postgres.
    diet_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list, server_default="{}"
    )

    def __repr__(self) -> str:
        return f"<Meal id={self.id} name={self.name!r} meal_type={self.meal_type}>"
