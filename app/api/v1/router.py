from fastapi import APIRouter

from app.api.v1 import admin, ai, calculator, ingredients, meal_plan

api_router = APIRouter()
api_router.include_router(calculator.router)
api_router.include_router(meal_plan.router)
api_router.include_router(ingredients.router)
api_router.include_router(ai.router)
api_router.include_router(admin.router)
