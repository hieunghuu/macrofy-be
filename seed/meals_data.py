"""
Starter set of curated meals. Small on purpose -- enough to exercise the
meal-plan generator end to end. Expand freely; each entry maps 1:1 to the
Meal model fields.
"""

from app.models.meal import MealType

MEALS = [
    {
        "name": "Grilled chicken breast with steamed broccoli",
        "description": "Simple high-protein, low-fat plate with lean chicken and greens.",
        "calories": 320,
        "protein_g": 48,
        "fat_g": 6,
        "carbs_g": 12,
        "meal_type": MealType.lunch,
        "diet_tags": ["high_protein", "low_fat", "gluten_free"],
    },
    {
        "name": "Egg white and spinach omelette",
        "description": "Fluffy egg white omelette with spinach and a sprinkle of feta.",
        "calories": 220,
        "protein_g": 28,
        "fat_g": 7,
        "carbs_g": 6,
        "meal_type": MealType.breakfast,
        "diet_tags": ["high_protein", "low_fat", "vegetarian", "gluten_free"],
    },
    {
        "name": "Baked cod with quinoa and asparagus",
        "description": "Flaky white fish with fiber-rich quinoa and roasted asparagus.",
        "calories": 380,
        "protein_g": 40,
        "fat_g": 8,
        "carbs_g": 32,
        "meal_type": MealType.dinner,
        "diet_tags": ["high_protein", "low_fat"],
    },
    {
        "name": "Greek yogurt with berries and honey",
        "description": "Non-fat Greek yogurt topped with mixed berries.",
        "calories": 180,
        "protein_g": 20,
        "fat_g": 1,
        "carbs_g": 22,
        "meal_type": MealType.snack,
        "diet_tags": ["high_protein", "low_fat", "vegetarian", "gluten_free"],
    },
    {
        "name": "Turkey and vegetable stir-fry",
        "description": "Lean ground turkey stir-fried with bell peppers and snap peas.",
        "calories": 350,
        "protein_g": 42,
        "fat_g": 9,
        "carbs_g": 18,
        "meal_type": MealType.dinner,
        "diet_tags": ["high_protein", "low_fat", "gluten_free"],
    },
    {
        "name": "Protein smoothie with banana and oats",
        "description": "Whey protein blended with banana, oats, and almond milk.",
        "calories": 310,
        "protein_g": 30,
        "fat_g": 5,
        "carbs_g": 38,
        "meal_type": MealType.breakfast,
        "diet_tags": ["high_protein", "low_fat", "vegetarian"],
    },
    {
        "name": "Lentil and vegetable soup",
        "description": "Hearty plant-based soup, naturally low in fat.",
        "calories": 260,
        "protein_g": 18,
        "fat_g": 3,
        "carbs_g": 40,
        "meal_type": MealType.lunch,
        "diet_tags": ["low_fat", "vegetarian", "vegan", "gluten_free"],
    },
    {
        "name": "Cottage cheese with pineapple",
        "description": "Low-fat cottage cheese with fresh pineapple chunks.",
        "calories": 160,
        "protein_g": 22,
        "fat_g": 2,
        "carbs_g": 14,
        "meal_type": MealType.snack,
        "diet_tags": ["high_protein", "low_fat", "vegetarian", "gluten_free"],
    },
]
