# About This Project
This is a side project built to simulate a production-ready service and improve my DevOps skills. 

The codebase may not always follow the best practices even i'm not hiding that i use Claude to make my works easier (:> why not), and there will likely be areas for improvement. 

If you notice better approaches, cleaner implementations, or architectural improvements, feel free to contribute or open a discussion.

# So why macrofy?

The thing is, I'm also a pretty hardcore gym rat, so the first thing I think about when choosing food is hitting my macros.

To be honest, there are already plenty of great nutrition tracking apps. Many of them even use AI to estimate calories and macros from a photo of your meal, so I don't see much value in competing in that space.

Also... I don't really want to pay for another subscription just to track my meals (I'm too cheap for that 😅).

Since I have a Computer Science background and now work in IT, I figured, why not build something that solves my own problem while keeping myself busy?

Alright, so i want to build something that solves my own problem: deciding what to eat. I'm often too lazy to think about different protein sources, and whenever I can't decide, the answer is always the same—rice and chicken, chicken with rice, rice next to chicken, or rice on top of chicken.

This project is about helping people discover meals that fit their nutrition goals, instead of just tracking what they've already eaten.

# Macrofy
One of three repos: `macrofy-be` (this one), `macrofy-fe`,
and `macrofy-ai`. This repo is a self-contained FastAPI service --
calculates TDEE and calorie targets from body stats + goals, and generates
meal plans from a curated meal catalog. 


## 3. Run migrations

```bash
alembic upgrade head
```

Creates the `meals`, `ingredients`, and `meal_ingredients` tables. After changing a model in `app/models/`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## 4. Seed the data

```bash
# Seed the curated meal data
python -m seed.seed_meals

# Seed the ingredient database (USDA-sourced nutritional data)
python -m seed.seed_ingredients

# Link meals to ingredients with quantities
python -m seed.link_meals_to_ingredients
```

Safe to re-run -- scripts clear tables before inserting.

## 5. Run the API

```bash
uvicorn app.main:app --reload
```

- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Configuration

Everything tunable lives in `app/core/config.py` and is set via env vars
(see `.env.example` for the full list with descriptions):
