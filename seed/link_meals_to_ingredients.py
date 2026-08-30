"""
Links existing meals to ingredients with fixed quantities.

This script maps the 8 original meals to their ingredients,
calculates macros from ingredients, and stores them.

USAGE:
    python -m seed.link_meals_to_ingredients

EXAMPLE OUTPUT:
    Linked 8 meals to ingredients.
    Updated macros for 8 meals.

INGREDIENT QUANTITY NOTES:
    Quantities are based on culinary standards:
    - 1 chicken breast ≈ 400g raw
    - 1 medium broccoli ≈ 250g florets
    - 1 egg ≈ 50g (whole)
    - 1 egg white ≈ 33g
"""

from app.db.session import SessionLocal
from app.models import Meal, Ingredient, MealIngredient, IngredientCategory


def get_ingredient_by_name(db, name_substring: str, category: IngredientCategory | None = None) -> Ingredient | None:
    """Find ingredient by partial name match."""
    query = db.query(Ingredient).filter(Ingredient.name.ilike(f"%{name_substring}%"))
    print(name_substring)
    if category:
        query = query.filter(Ingredient.category == category)
    return query.first()


def link_grilled_chicken_meal(db) -> None:
    """Grilled chicken breast with steamed broccoli (lunch)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Grilled chicken%")).first()
    if not meal:
        return

    # Get ingredients
    chicken = get_ingredient_by_name(db, "Chicken, breast, boneless, skinless, raw")
    broccoli = get_ingredient_by_name(db, "Broccoli")
    olive_oil = get_ingredient_by_name(db, "OLIVE OIL")
    salt = get_ingredient_by_name(db, "Salt")

    if not all([chicken, broccoli, olive_oil, salt]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    # Add ingredients with quantities
    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=chicken.id, quantity_g=400, order_index=1),
        MealIngredient(meal_id=meal.id, ingredient_id=broccoli.id, quantity_g=250, order_index=2),
        MealIngredient(meal_id=meal.id, ingredient_id=olive_oil.id, quantity_g=10, order_index=3),
        MealIngredient(meal_id=meal.id, ingredient_id=salt.id, quantity_g=2, order_index=4),
    ]

    # Clear existing and add new
    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def link_egg_white_omelette(db) -> None:
    """Egg white and spinach omelette (breakfast)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Egg white%")).first()
    if not meal:
        return

    egg_white = get_ingredient_by_name(db, "Egg, white, raw, fresh")
    spinach = get_ingredient_by_name(db, "Spinach, raw")
    feta = get_ingredient_by_name(db, "Cheese, feta")
    olive_oil = get_ingredient_by_name(db, "OLIVE OIL")

    if not all([egg_white, spinach, feta, olive_oil]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=egg_white.id, quantity_g=200, order_index=1),  # ~6 egg whites
        MealIngredient(meal_id=meal.id, ingredient_id=spinach.id, quantity_g=100, order_index=2),
        MealIngredient(meal_id=meal.id, ingredient_id=feta.id, quantity_g=30, order_index=3),
        MealIngredient(meal_id=meal.id, ingredient_id=olive_oil.id, quantity_g=5, order_index=4),
    ]

    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def link_baked_cod_meal(db) -> None:
    """Baked cod with quinoa and asparagus (dinner)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Baked cod%")).first()
    if not meal:
        return

    cod = get_ingredient_by_name(db, "Fish, cod, Atlantic, raw")
    quinoa = get_ingredient_by_name(db, "Quinoa, cooked")
    asparagus = get_ingredient_by_name(db, "Asparagus, raw")
    olive_oil = get_ingredient_by_name(db, "OLIVE OIL")

    if not all([cod, quinoa, asparagus, olive_oil]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=cod.id, quantity_g=200, order_index=1),
        MealIngredient(meal_id=meal.id, ingredient_id=quinoa.id, quantity_g=150, order_index=2),
        MealIngredient(meal_id=meal.id, ingredient_id=asparagus.id, quantity_g=150, order_index=3),
        MealIngredient(meal_id=meal.id, ingredient_id=olive_oil.id, quantity_g=10, order_index=4),
    ]

    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def link_greek_yogurt_meal(db) -> None:
    """Greek yogurt with berries and honey (snack)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Greek yogurt%")).first()
    if not meal:
        return

    yogurt = get_ingredient_by_name(db, "Yogurt, Greek, nonfat, plain, CHOBANI")
    berries = get_ingredient_by_name(db, "Snack, Mixed Berry Bar")
    honey = get_ingredient_by_name(db, "Honey")

    if not all([yogurt, berries, honey]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=yogurt.id, quantity_g=200, order_index=1),
        MealIngredient(meal_id=meal.id, ingredient_id=berries.id, quantity_g=100, order_index=2),
        MealIngredient(meal_id=meal.id, ingredient_id=honey.id, quantity_g=15, order_index=3),
    ]

    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def link_turkey_stirfry(db) -> None:
    """Turkey and vegetable stir-fry (dinner)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Turkey%stir-fry%")).first()
    if not meal:
        return

    turkey = get_ingredient_by_name(db, "Turkey, Ground, raw")
    pepper = get_ingredient_by_name(db, "Bell pepper, red")
    snap_peas = get_ingredient_by_name(db, "Beans, snap, green, raw")
    soy_sauce = get_ingredient_by_name(db, "SOY SAUCE")
    olive_oil = get_ingredient_by_name(db, "OLIVE OIL")

    if not all([turkey, pepper, snap_peas, soy_sauce, olive_oil]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=turkey.id, quantity_g=250, order_index=1),
        MealIngredient(meal_id=meal.id, ingredient_id=pepper.id, quantity_g=150, order_index=2),
        MealIngredient(meal_id=meal.id, ingredient_id=snap_peas.id, quantity_g=100, order_index=3),
        MealIngredient(meal_id=meal.id, ingredient_id=soy_sauce.id, quantity_g=20, order_index=4),
        MealIngredient(meal_id=meal.id, ingredient_id=olive_oil.id, quantity_g=15, order_index=5),
    ]

    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def link_protein_smoothie(db) -> None:
    """Protein smoothie with banana and oats (breakfast)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Protein smoothie%")).first()
    if not meal:
        return

    whey = get_ingredient_by_name(db, "Whey protein powder")
    banana = get_ingredient_by_name(db, "Banana, raw")
    oats = get_ingredient_by_name(db, "Cereals, QUAKER, Quick Oats, Dry")
    almond_milk = get_ingredient_by_name(db, "Almond milk, unsweetened, plain, refrigerated")

    if not all([whey, banana, oats, almond_milk]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=whey.id, quantity_g=30, order_index=1),  # 1 scoop
        MealIngredient(meal_id=meal.id, ingredient_id=banana.id, quantity_g=120, order_index=2),  # 1 medium
        MealIngredient(meal_id=meal.id, ingredient_id=oats.id, quantity_g=40, order_index=3),
        MealIngredient(meal_id=meal.id, ingredient_id=almond_milk.id, quantity_g=250, order_index=4),
    ]

    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def link_lentil_soup(db) -> None:
    """Lentil and vegetable soup (lunch)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Lentil%soup%")).first()
    if not meal:
        return

    lentils = get_ingredient_by_name(db, "Lentils, mature seeds, cooked, boiled, with salt")
    zucchini = get_ingredient_by_name(db, "Squash, zucchini, baby, raw")
    spinach = get_ingredient_by_name(db, "Spinach, raw")

    if not all([lentils, zucchini, spinach]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=lentils.id, quantity_g=200, order_index=1),
        MealIngredient(meal_id=meal.id, ingredient_id=zucchini.id, quantity_g=150, order_index=2),
        MealIngredient(meal_id=meal.id, ingredient_id=spinach.id, quantity_g=100, order_index=3),
    ]

    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def link_cottage_cheese(db) -> None:
    """Cottage cheese with pineapple (snack)"""
    meal = db.query(Meal).filter(Meal.name.ilike("%Cottage cheese%")).first()
    if not meal:
        return

    cottage = get_ingredient_by_name(db, "cheese, cottage, lowfat, 1% milkfat")
    pineapple = get_ingredient_by_name(db, "Pineapple, raw")

    if not all([cottage, pineapple]):
        print(f"[ERR] Missing ingredients for {meal.name}")
        return

    meal_ingredients = [
        MealIngredient(meal_id=meal.id, ingredient_id=cottage.id, quantity_g=200, order_index=1),
        MealIngredient(meal_id=meal.id, ingredient_id=pineapple.id, quantity_g=100, order_index=2),
    ]

    db.query(MealIngredient).filter(MealIngredient.meal_id == meal.id).delete()
    db.add_all(meal_ingredients)


def calculate_and_update_macros(db) -> int:
    """Calculate macros from ingredients and update meal records."""
    meals = db.query(Meal).join(MealIngredient).distinct().all()

    for meal in meals:
        # Eager load ingredients
        db.refresh(meal, ['meal_ingredients'])

        if meal.use_computed_macros:
            continue  # Already using computed macros

        # Calculate from ingredients
        macros = {
            "calories": 0.0,
            "protein_g": 0.0,
            "fat_g": 0.0,
            "carbs_g": 0.0,
        }

        for mi in meal.meal_ingredients:
            if mi.ingredient:
                ratio = mi.quantity_g / 100.0
                macros["calories"] += mi.ingredient.calories_per_100g * ratio
                macros["protein_g"] += mi.ingredient.protein_g_per_100g * ratio
                macros["fat_g"] += mi.ingredient.fat_g_per_100g * ratio
                macros["carbs_g"] += mi.ingredient.carbs_g_per_100g * ratio

        # Round and store
        meal.calories = round(macros["calories"], 2)
        meal.protein_g = round(macros["protein_g"], 2)
        meal.fat_g = round(macros["fat_g"], 2)
        meal.carbs_g = round(macros["carbs_g"], 2)

    return len(meals)


def run() -> None:
    db = SessionLocal()
    try:
        print("Linking meals to ingredients...")

        link_grilled_chicken_meal(db)
        link_egg_white_omelette(db)
        link_baked_cod_meal(db)
        link_greek_yogurt_meal(db)
        link_turkey_stirfry(db)
        link_protein_smoothie(db)
        link_lentil_soup(db)
        link_cottage_cheese(db)

        db.commit()
        meals_linked = db.query(Meal).join(MealIngredient).distinct().count()
        print(f"Linked {meals_linked} meals to ingredients.")

        print("\n📊 Calculating macros from ingredients...")
        meals_updated = calculate_and_update_macros(db)
        db.commit()
        print(f"Updated macros for {meals_updated} meals.")

        # Show sample calculation
        meal = db.query(Meal).join(MealIngredient).first()
        if meal:
            db.refresh(meal, ['meal_ingredients'])
            print(f"\n  Sample: {meal.name}")
            print(f"   Stored macros: {meal.calories} cal, {meal.protein_g}g protein, {meal.fat_g}g fat, {meal.carbs_g}g carbs")
            print("   Ingredients:")
            for mi in sorted(meal.meal_ingredients, key=lambda x: x.order_index):
                if mi.ingredient:
                    print(f"     - {mi.ingredient.name}: {mi.quantity_g}g")

    finally:
        db.close()


if __name__ == "__main__":
    run()
