SHELL := /bin/bash

.PHONY: all

migrate:
	alembic upgrade head

seed: seed-meals seed-ingredients link-meals

seed-meals:
	python3 -m seed.seed_meals

# Seed from USDA API (requires API key in .env)
seed-usda:
	python3 -m seed.seed_from_usda

link-meals:
	python3 -m seed.link_meals_to_ingredients

start:
	uvicorn app.main:app --reload
