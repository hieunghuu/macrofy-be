from fastapi import APIRouter

from app.api.v1 import ai, calculator, meal_plan

api_router = APIRouter()
api_router.include_router(calculator.router)
api_router.include_router(meal_plan.router)
api_router.include_router(ai.router)
