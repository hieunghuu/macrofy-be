"""
Seed ingredients from USDA FoodData Central API.

Fetches nutritional data from USDA and populates the ingredients table.
This replaces manual seed data with real USDA-sourced nutrition.

USAGE:
    python -m seed.seed_from_usda

PREREQUISITES:
    1. Get a free API key from https://portal.ndata.fdc.nal.usda.gov/
    2. Set USDA_API_KEY in your .env file

RATE LIMITS:
    - Free tier: 1000 requests/day
    - This script batches requests (20 foods per request) to be efficient

FOOD CATEGORIES SEEDED:
    - Proteins: chicken, turkey, beef, fish, eggs, tofu
    - Vegetables: broccoli, spinach, asparagus, peppers
    - Grains: rice, oats, quinoa, bread
    - Dairy: yogurt, cheese, milk
    - Legumes: lentils, beans, chickpeas
    - Fruits: banana, berries, apple, pineapple
    - Fats: olive oil, butter, coconut oil
"""

import logging

from app.clients.usda_client import get_usda_client
from app.db.session import SessionLocal
from app.models.ingredient import Ingredient, IngredientCategory
from app.models.meal_ingredient import MealIngredient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Search queries for each category
# USDA returns many results, so we use specific queries to get common foods
SEARCH_QUERIES: dict[str, list[str]] = {
    "seasonings": [
        "soy sauce",
        "fish sauce",
        "salt",
    ],
    "protein": [
        "chicken breast raw",
        "turkey ground raw",
        "cod fish raw",
        "salmon raw",
        "egg whole raw",
        "egg white raw",
        "tofu firm",
        "whey protein powder",
        "shrimp raw",
        "pork tenderloin raw",
    ],
    "vegetable": [
        "broccoli raw",
        "spinach raw",
        "asparagus raw",
        "bell pepper raw",
        "zucchini raw",
        "cauliflower raw",
        "snap peas raw",
        "carrot raw",
        "tomato raw",
        "cucumber raw",
        "bell pepper raw"
    ],
    "grain": [
        "quinoa cooked",
        "rice brown cooked",
        "rice white cooked",
        "oats rolled dry",
        "bread whole wheat",
        "pasta cooked",
        "sweet potato baked",
        "potato baked",
    ],
    "dairy": [
        "greek yogurt nonfat plain",
        "cottage cheese lowfat",
        "milk whole",
        "milk almond unsweetened",
        "cheese feta",
        "cheese cheddar",
        "mozzarella cheese",
        "cream cheese",
    ],
    "legume": [
        "lentils cooked",
        "black beans cooked",
        "chickpeas cooked",
        "kidney beans cooked",
        "edamame cooked",
        "navy beans cooked",
    ],
    "fruit": [
        "banana raw",
        "mixed berries raw",
        "apple raw with skin",
        "pineapple raw",
        "strawberries raw",
        "blueberries raw",
        "orange raw",
        "grapes raw",
    ],
    "oil_fat": [
        "olive oil",
        "coconut oil",
        "butter salted",
        "avocado raw",
        "mayonnaise",
    ],
   
}


def map_usda_category(food_category: str) -> IngredientCategory:
    """Map USDA food category to our IngredientCategory."""
    category_lower = food_category.lower()

    # Direct mappings
    if "poultry" in category_lower or "chicken" in category_lower:
        return IngredientCategory.protein
    if "fish" in category_lower or "seafood" in category_lower or "salmon" in category_lower:
        return IngredientCategory.protein
    if "beef" in category_lower or "pork" in category_lower or "lamb" in category_lower:
        return IngredientCategory.protein
    if "eggs" in category_lower or "egg" in category_lower:
        return IngredientCategory.protein
    if "legumes" in category_lower or "beans" in category_lower or "lentils" in category_lower:
        return IngredientCategory.legume
    if "vegetables" in category_lower or "vegetable" in category_lower:
        return IngredientCategory.vegetable
    if "fruits" in category_lower or "fruit" in category_lower:
        return IngredientCategory.fruit
    if "grain" in category_lower or "cereal" in category_lower or "baked products" in category_lower:
        return IngredientCategory.grain
    if "dairy" in category_lower or "milk" in category_lower or "cheese" in category_lower:
        return IngredientCategory.dairy
    if "fats" in category_lower or "oils" in category_lower:
        return IngredientCategory.oil_fat

    # Default fallback
    return IngredientCategory.condiment


def create_ingredient_from_usda(nutrient_data, category_override: IngredientCategory | None = None) -> Ingredient:
    """Create an Ingredient model from USDA parsed data."""
    category = category_override or map_usda_category(nutrient_data.food_category)

    return Ingredient(
        name=clean_description(nutrient_data.description),
        category=category,
        calories_per_100g=nutrient_data.calories_per_100g,
        protein_g_per_100g=nutrient_data.protein_g_per_100g,
        fat_g_per_100g=nutrient_data.fat_g_per_100g,
        carbs_g_per_100g=nutrient_data.carbs_g_per_100g,
        serving_size_default_g=100.0,
    )


def clean_description(description: str) -> str:
    """
    Clean up USDA description to be more readable.

    Examples:
        "Chicken, breast, boneless, skinless, raw" -> "Chicken breast, boneless, skinless, raw"
        "Broccoli, flower clusters, raw" -> "Broccoli, flower clusters, raw"
    """
    # Remove common prefixes
    description = description.replace(", UPC: ", ", ")
    description = description.replace(", GTIN: ", ", ")

    # Title case the first word if it starts with lowercase
    if description and description[0].islower():
        parts = description.split(",", 1)
        if len(parts) > 1:
            description = parts[0].title() + "," + parts[1]

    return description.strip()


def seed_from_usda() -> int:
    """
    Fetch ingredients from USDA API and seed the database.

    Returns:
        Number of ingredients seeded
    """
    client = get_usda_client()

    if not client.api_key:
        logger.error("USDA_API_KEY not set. Please set it in your .env file.")
        logger.info("Get a free key at: https://portal.data.fdc.nal.usda.gov/")
        return 0
    else:
        logger.info("Found aPi key in .env")
    db = SessionLocal()
    try:
        # Clear existing data (order matters due to foreign key)
        db.query(MealIngredient).delete()
        db.commit()
        db.query(Ingredient).delete()
        db.commit()
        logger.info("Cleared existing ingredients.")

        total_seeded = 0
        errors = 0

        # Process each category
        for category_name, queries in SEARCH_QUERIES.items():
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing category: {category_name.upper()}")
            logger.info(f"{'='*50}")

            category = IngredientCategory(category_name)
            ingredients_for_category = []

            for query in queries:
                try:
                    logger.info(f"  Searching: '{query}'...")
                    nutrients = client.search_and_get_nutrients(query, page_size=5)
                    print(nutrients)
                    for nutrient_data in nutrients:
                        try:
                            ingredient = create_ingredient_from_usda(
                                nutrient_data, category_override=category
                            )
                            ingredients_for_category.append(ingredient)
                            logger.info(
                                f"    ✓ {ingredient.name[:50]}: "
                                f"{ingredient.calories_per_100g}cal, "
                                f"{ingredient.protein_g_per_100g}g protein"
                            )
                        except Exception as e:
                            logger.warning(f"     Failed to create ingredient: {e}")
                            errors += 1
                        break
                except Exception as e:
                    logger.error(f"   Search failed for '{query}': {e}")
                    errors += 1

            # Batch insert for this category
            if ingredients_for_category:
                db.add_all(ingredients_for_category)
                db.commit()
                total_seeded += len(ingredients_for_category)
                logger.info(f"  → Inserted {len(ingredients_for_category)} ingredients for {category_name}")

        logger.info(f"\n{'='*50}")
        logger.info(f"SEEDING COMPLETE")
        logger.info(f"{'='*50}")
        logger.info(f"Total ingredients seeded: {total_seeded}")
        logger.info(f"Errors: {errors}")

        return total_seeded

    finally:
        db.close()


def run() -> None:
    """Entry point for CLI."""
    count = seed_from_usda()
    if count > 0:
        print(f"\nSuccessfully seeded {count} ingredients from USDA!")
    else:
        print("\nSeeding failed. Check your API key and internet connection.")


if __name__ == "__main__":
    run()
