from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ingredient import IngredientCategory
from app.repositories.postgres_ingredient_repo import PostgresIngredientRepository
from app.schemas.meal import IngredientCreate, IngredientNutrition

router = APIRouter(tags=["ingredients"])


@router.get("/ingredients", response_model=list[IngredientNutrition])
def list_ingredients(
    category: IngredientCategory | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[IngredientNutrition]:
    repo = PostgresIngredientRepository(db)
    ingredients = repo.list_ingredients(category=category, search=search)
    return [IngredientNutrition.model_validate(i) for i in ingredients]


@router.get("/ingredients/categories", response_model=list[str])
def list_categories() -> list[str]:
    return [c.value for c in IngredientCategory]


@router.get("/ingredients/{ingredient_id}", response_model=IngredientNutrition)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)) -> IngredientNutrition:
    repo = PostgresIngredientRepository(db)
    ingredient = repo.get_ingredient(ingredient_id)
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingredient {ingredient_id} not found")
    return IngredientNutrition.model_validate(ingredient)


@router.post("/ingredients", response_model=IngredientNutrition, status_code=status.HTTP_201_CREATED)
def create_ingredient(ingredient_data: IngredientCreate, db: Session = Depends(get_db)) -> IngredientNutrition:
    repo = PostgresIngredientRepository(db)
    ingredient = repo.create_ingredient(ingredient_data.model_dump())
    db.commit()
    return IngredientNutrition.model_validate(ingredient)


@router.put("/ingredients/{ingredient_id}", response_model=IngredientNutrition)
def update_ingredient(
    ingredient_id: int, ingredient_data: IngredientCreate, db: Session = Depends(get_db)
) -> IngredientNutrition:
    repo = PostgresIngredientRepository(db)
    ingredient = repo.update_ingredient(ingredient_id, ingredient_data.model_dump())
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingredient {ingredient_id} not found")
    db.commit()
    return IngredientNutrition.model_validate(ingredient)


@router.delete("/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)) -> None:
    repo = PostgresIngredientRepository(db)
    try:
        deleted = repo.delete_ingredient(ingredient_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete: ingredient is used in meals")
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingredient {ingredient_id} not found")
    db.commit()
