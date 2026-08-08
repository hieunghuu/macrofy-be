"""
Pydantic schemas for LP optimizer admin API.
"""
from pydantic import BaseModel, Field


class LPWeightsIn(BaseModel):
    """Request body for updating LP weights."""

    calories: float | None = Field(
        default=None, ge=0, description="Weight for calorie deviation penalty"
    )
    protein: float | None = Field(
        default=None, ge=0, description="Weight for protein deviation penalty"
    )
    fat: float | None = Field(
        default=None, ge=0, description="Weight for fat deviation penalty"
    )
    carbs: float | None = Field(
        default=None, ge=0, description="Weight for carbs deviation penalty"
    )


class LPWeightsOut(BaseModel):
    """Response body for LP weights (GET and PUT)."""

    calories: float = Field(description="Current weight for calorie deviation")
    protein: float = Field(description="Current weight for protein deviation")
    fat: float = Field(description="Current weight for fat deviation")
    carbs: float = Field(description="Current weight for carbs deviation")


class SolverSettingsIn(BaseModel):
    """Request body for updating solver settings."""

    time_limit_seconds: float | None = Field(
        default=None, ge=0, description="Max solve time in seconds (0 = unlimited)"
    )
    return_best_if_timeout: bool | None = Field(
        default=None, description="Return best found solution if time limit hit"
    )


class SolverSettingsOut(BaseModel):
    """Response body for solver settings (GET and PUT)."""

    time_limit_seconds: float = Field(description="Max solve time in seconds (0 = unlimited)")
    return_best_if_timeout: bool = Field(
        description="Whether to return best solution if time limit hit"
    )


class LPConfigOut(BaseModel):
    """Full LP optimizer config response."""

    weights: LPWeightsOut
    solver: SolverSettingsOut
