"""
Admin API endpoints for LP optimizer configuration.

Provides runtime control over LP solver weights and settings without
requiring a restart or configmap update.

NOTE: In production, these endpoints should be protected by authentication
(e.g., require an admin JWT token or API key). Currently no auth is applied.
"""
from fastapi import APIRouter

from app.schemas.lp_weights import (
    LPConfigOut,
    LPWeightsIn,
    LPWeightsOut,
    SolverSettingsIn,
    SolverSettingsOut,
)
from app.services.lp_weights_service import get_lp_weights_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/lp-weights", response_model=LPConfigOut)
def get_lp_config() -> LPConfigOut:
    """Get current LP optimizer weights and solver settings."""
    service = get_lp_weights_service()
    weights = service.get_weights()
    solver = service.get_solver_settings()
    return LPConfigOut(
        weights=LPWeightsOut(
            calories=weights["calories"],
            protein=weights["protein"],
            fat=weights["fat"],
            carbs=weights["carbs"],
        ),
        solver=SolverSettingsOut(
            time_limit_seconds=solver["time_limit_seconds"],
            return_best_if_timeout=solver["return_best_if_timeout"],
        ),
    )


@router.put("/lp-weights", response_model=LPConfigOut)
def update_lp_weights(body: LPWeightsIn) -> LPConfigOut:
    """
    Update LP optimizer weights.

    Only provided fields are updated (partial update).
    Changes are persisted to disk and survive restarts.

    Example request body:
        {"protein": 1.5, "carbs": 0.8}
    """
    service = get_lp_weights_service()
    updates = body.model_dump(exclude_none=True)
    service.update_weights(updates)

    # Return full config after update
    weights = service.get_weights()
    solver = service.get_solver_settings()
    return LPConfigOut(
        weights=LPWeightsOut(
            calories=weights["calories"],
            protein=weights["protein"],
            fat=weights["fat"],
            carbs=weights["carbs"],
        ),
        solver=SolverSettingsOut(
            time_limit_seconds=solver["time_limit_seconds"],
            return_best_if_timeout=solver["return_best_if_timeout"],
        ),
    )


@router.put("/lp-weights/solver", response_model=SolverSettingsOut)
def update_solver_settings(body: SolverSettingsIn) -> SolverSettingsOut:
    """
    Update LP solver settings.

    Only provided fields are updated (partial update).

    Example request body:
        {"time_limit_seconds": 10, "return_best_if_timeout": true}
    """
    service = get_lp_weights_service()
    updates = body.model_dump(exclude_none=True)
    service.update_solver_settings(updates)
    return SolverSettingsOut(**service.get_solver_settings())


@router.post("/lp-weights/reset", response_model=LPConfigOut)
def reset_lp_weights() -> LPConfigOut:
    """
    Reset LP weights and solver settings to YAML config defaults.

    Clears any runtime overrides (deletes the state file) and reloads
    from `config/lp_weights.yaml`.
    """
    service = get_lp_weights_service()
    service.reset_to_defaults()

    weights = service.get_weights()
    solver = service.get_solver_settings()
    return LPConfigOut(
        weights=LPWeightsOut(
            calories=weights["calories"],
            protein=weights["protein"],
            fat=weights["fat"],
            carbs=weights["carbs"],
        ),
        solver=SolverSettingsOut(
            time_limit_seconds=solver["time_limit_seconds"],
            return_best_if_timeout=solver["return_best_if_timeout"],
        ),
    )
