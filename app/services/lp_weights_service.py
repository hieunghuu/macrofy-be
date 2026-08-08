"""
LP Optimizer Weights Service.

Manages LP solver weights with:
- YAML config file as source of truth (loaded on startup)
- In-memory store for runtime updates (via API)
- Persistence to disk on update (so changes survive restart)

Weights control how the LP solver balances macro targets in the objective:
  Higher weight = more penalty for deviating from that macro target.
"""
import json
from pathlib import Path
from typing import Any

import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = BASE_DIR / "config" / "lp_weights.yaml"
_STATE_FILE = BASE_DIR / ".lp_weights.state.json"

class LPWeightsService:
    """
    Manages LP optimizer weights.

    Load order:
    1. State file (`.lp_weights.state.json`) if exists — runtime overrides
    2. YAML config file (`config/lp_weights.yaml`) — baseline defaults
    3. Hard-coded fallbacks

    Save: writes runtime overrides to state file (call save() after updates).
    """

    def __init__(self, config_path: Path | str = DEFAULT_CONFIG_PATH):
        self._config_path = Path(config_path)
        self._weights: dict[str, float] = {}
        self._solver_settings: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load config: state file overrides > YAML config > defaults."""
        # Hard-coded defaults (ultimate fallback)
        defaults = {
            "weights": {
                "calories": 0.8,
                "protein": 1.0,
                "fat": 0.5,
                "carbs": 0.5,
            },
            "solver": {
                "time_limit_seconds": 30,
                "return_best_if_timeout": True,
            },
        }

        # Start with YAML config (if exists)
        config = defaults.copy()
        if self._config_path.exists():
            with open(self._config_path, encoding="utf-8") as f:
                file_config = yaml.safe_load(f) or {}
                config = _deep_merge(defaults, file_config)

        # Override with state file (runtime overrides survive restarts)
        if _STATE_FILE.exists():
            with open(_STATE_FILE, encoding="utf-8") as f:
                state = json.load(f)
                config = _deep_merge(config, state)

        self._weights = config["weights"]
        self._solver_settings = config["solver"]

    def save(self) -> None:
        """
        Persist current weights to state file.

        Called by the admin API after a successful PUT.
        This makes runtime overrides survive app restarts.
        """
        state = {
            "weights": self._weights,
            "solver": self._solver_settings,
        }
        with open(_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def get_weights(self) -> dict[str, float]:
        """Return current weights (runtime overrides applied)."""
        return dict(self._weights)

    def get_solver_settings(self) -> dict[str, Any]:
        """Return current solver settings."""
        return dict(self._solver_settings)

    def update_weights(self, weights: dict[str, float]) -> dict[str, float]:
        """
        Update weights and persist to state file.

        Args:
            weights: Dict with keys 'calories', 'protein', 'fat', 'carbs'.
                     Only provided keys are updated.

        Returns:
            The updated weights dict.

        Raises:
            ValueError: If any weight value is not a positive number.
        """
        for key, value in weights.items():
            if key not in self._weights:
                raise ValueError(f"Unknown weight key: {key!r}. Valid keys: {list(self._weights.keys())}")
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"Weight {key!r} must be a non-negative number, got {value!r}")

        self._weights.update(weights)
        self.save()
        return self.get_weights()

    def update_solver_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        """
        Update solver settings and persist to state file.

        Args:
            settings: Dict with solver settings to update.
                      Valid keys: 'time_limit_seconds', 'return_best_if_timeout'.

        Returns:
            The updated solver settings dict.
        """
        for key, value in settings.items():
            if key == "time_limit_seconds":
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError("time_limit_seconds must be a non-negative number")
            elif key == "return_best_if_timeout":
                if not isinstance(value, bool):
                    raise ValueError("return_best_if_timeout must be a boolean")
            else:
                raise ValueError(f"Unknown solver setting: {key!r}")
            self._solver_settings[key] = value

        self.save()
        return self.get_solver_settings()

    def reset_to_defaults(self) -> None:
        """
        Clear runtime overrides and reload from YAML config.

        Deletes the state file.
        """
        if _STATE_FILE.exists():
            _STATE_FILE.unlink()
        self._load()


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep-merge override dict into base dict."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# Module-level singleton (lazy-loaded on first access)
_lp_weights_service: LPWeightsService | None = None


def get_lp_weights_service() -> LPWeightsService:
    """Get or create the module-level LPWeightsService singleton."""
    global _lp_weights_service
    if _lp_weights_service is None:
        _lp_weights_service = LPWeightsService()
    return _lp_weights_service
