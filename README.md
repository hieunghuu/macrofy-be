# Food Coach -- backend

One of three repos: `food-coach-backend` (this one), `food-coach-frontend`,
and `food-coach-ai`. This repo is a self-contained FastAPI service --
calculates TDEE and calorie targets from body stats + goals, and generates
meal plans from a curated meal catalog. All config is env-driven -- nothing
environment-specific is hardcoded.

## Architecture: modular monolith, not microservices (for now)

Backend, frontend, and ai are separate **repos** so they can be developed,
versioned, and deployed independently -- but the backend itself is a single
deployable FastAPI app, not a set of internal microservices. At this stage
(a handful of endpoints, one database) splitting the backend further would
add network calls, service discovery, and deployment overhead without a
concrete need for it yet. Internally it's organized into clean modules
(`services/`, `repositories/`, `clients/`) with narrow interfaces between
them, so any one of them could be extracted into its own service later if
it genuinely needs independent scaling -- without a rewrite.

## 1. Start PostgreSQL

```bash
docker compose up -d
```

Starts Postgres 16 on `localhost:5432` with the credentials from
`docker-compose.yml` (`food_coach` / `food_coach`, database `food_coach`).

## 2. Set up your local environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

`.env.example` documents every configurable value -- see the table below.
Defaults already match the Docker Compose service, so no edits are needed
for local dev.

## 3. Run migrations

```bash
alembic upgrade head
```

Creates the `meals` table. After changing a model in `app/models/`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## 4. Seed the curated meal data

```bash
python -m seed.seed_meals
```

Safe to re-run -- clears the table and re-inserts the current data in
`seed/meals_data.py`.

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
