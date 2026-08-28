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
meal plans from a curated meal catalog. All config is env-driven -- nothing
environment-specific is hardcoded.


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

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `APP_NAME`, `APP_VERSION`, `API_V1_PREFIX` | App metadata / route prefix |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins, or `*` |
| `MIN_SAFE_CALORIES` | Hard floor on any generated calorie target |
| `DEFAULT_PROTEIN_G_PER_KG` | Protein target when a request doesn't override it |
| `DEFAULT_FAT_PERCENT` | Fraction of calories from fat when not overridden |
| `KCAL_PER_KG_FAT` | Energy density used to convert kg/week into daily kcal |
| `DEFAULT_RATE_KG_PER_WEEK` | Default weight-change rate |
| `DEFAULT_MEAL_COUNT` | Default number of meals per generated plan |
| `MIN_USER_AGE` | Minimum age accepted by the calculator endpoints |

Note: the Mifflin-St Jeor formula coefficients and activity-level
multipliers in `app/services/tdee_calculator.py` are intentionally **not**
env-configurable -- they define the formula itself, not deployment config.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/v1/calculate/tdee` | Body stats -> BMR + TDEE |
| POST | `/api/v1/calculate/calorie-target` | Body stats + goal -> target calories & macros |
| GET | `/api/v1/meals` | List curated meals, filterable by `meal_type` and repeatable `tag` |
| GET | `/api/v1/ingredients` | List ingredients with optional category filter and search |
| GET | `/api/v1/ingredients/{id}` | Get full nutritional details for an ingredient |
| POST | `/api/v1/ingredients` | Create a new ingredient (admin) |
| PUT | `/api/v1/ingredients/{id}` | Update an ingredient's nutritional data |
| DELETE | `/api/v1/ingredients/{id}` | Delete an ingredient (fails if used in meals) |
| POST | `/api/v1/meal-plan/generate` | Target calories/macros + preferences -> a full meal plan |
| GET | `/api/v1/ai/status` | Reports whether the `ai` service is configured and reachable |

## Adding the `ai` service later, without refactoring

`app/clients/` holds an `AIClient` interface (same pattern as
`MealRepository`): a `NullAIClient` (default, AI disabled) and an
`HttpAIClient` that calls the external `ai` repo over HTTP. Which one gets
used is decided purely by the `AI_SERVICE_URL` env var -- set it once the
`ai` repo is deployed, and the backend switches automatically. No route,
service, or existing code needs to change.

This was tested, not just designed: with `AI_SERVICE_URL` unset,
`/api/v1/ai/status` returns `{"configured": false, "reachable": false}`.
Restarting with `AI_SERVICE_URL=http://some-host` set -- and nothing else
touched -- flips it to `{"configured": true, "reachable": false}` (false
because nothing was actually listening there in the test, which the client
handles gracefully rather than crashing). When real AI-powered endpoints
are added, they'll depend on `get_ai_client()` the same way `/ai/status`
already does.

## Architecture

```
app/
  api/v1/        FastAPI routers (HTTP layer only -- no business logic)
  schemas/        Pydantic request/response models
  services/       Framework-agnostic business logic (TDEE, macros, meal-plan generation)
  repositories/   MealRepository interface + Postgres implementation (our own data)
  clients/        AIClient interface + implementations (external services, e.g. the ai repo)
  models/         SQLAlchemy ORM models
  db/             Engine, session, declarative base
  core/           Env-driven settings
```

The service layer only talks to `MealRepository` and `AIClient` -- both
interfaces, never concrete implementations directly. Adding a third-party
nutrition API or the real AI service later means writing a new
implementation of an existing interface, not restructuring the app.

## What's been tested end-to-end

- Migration applied against a real Postgres instance; schema verified column-by-column
- Seed data loaded and confirmed
- Every endpoint hit with real HTTP requests: TDEE math verified by hand,
  the calorie safety floor confirmed to trigger correctly, meal-plan
  generation verified including the tag-relaxation fallback when no meal
  matches every requested diet tag
- Config confirmed to be genuinely env-driven: `MIN_SAFE_CALORIES` and
  `DEFAULT_PROTEIN_G_PER_KG` were overridden via env vars alone (no code
  touched) and the API's behavior changed accordingly

## Next steps

- User accounts + auth (JWT), so users can save/favorite plans
- Daily intake logging vs. target
- Build out `food-coach-ai` for real (LLM coaching, food-photo recognition),
  then extend `app/clients/http_ai_client.py` to call its actual endpoints
  and add `/api/v1/ai/...` routes for whatever it exposes -- the seam is
  already there and tested
- A second `MealRepository` implementation backed by a third-party
  nutrition API, blended with the curated catalog
- Smarter meal-plan optimization (e.g. linear programming to hit macros
  more precisely instead of nearest-calorie matching)
- Dockerize the app itself (currently only Postgres is containerized)

--- 
for meal plan, it should be give user also information about,
how many gram of  ingredient they should eat
example:
```
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
```
