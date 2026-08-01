from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Central app configuration. Every value here is loaded from environment
    variables (or a local .env file) so the same code works across
    dev/staging/prod without any code changes -- just different env vars.

    Note: formula-intrinsic constants (Mifflin-St Jeor coefficients,
    activity-level multipliers) are NOT here -- those define the algorithm
    itself, not something an environment should be able to override.
    """

    # --- App metadata ---
    app_name: str = Field(default="Food Coach API", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")

    # --- Database ---
    database_url: str = Field(
        default="postgresql+psycopg2://food_coach:food_coach@localhost:5432/food_coach",
        validation_alias="DATABASE_URL",
    )

    # --- CORS: comma-separated origins, e.g. "http://localhost:3000,https://app.example.com" ---
    cors_origins: str = Field(default="*", validation_alias="CORS_ORIGINS")

    # --- Nutrition/business defaults (tunable per environment, no redeploy needed) ---
    min_safe_calories: float = Field(default=1200, validation_alias="MIN_SAFE_CALORIES")
    default_protein_g_per_kg: float = Field(
        default=1.8, validation_alias="DEFAULT_PROTEIN_G_PER_KG"
    )
    default_fat_percent: float = Field(default=0.25, validation_alias="DEFAULT_FAT_PERCENT")
    kcal_per_kg_fat: float = Field(default=7700, validation_alias="KCAL_PER_KG_FAT")
    default_rate_kg_per_week: float = Field(
        default=0.5, validation_alias="DEFAULT_RATE_KG_PER_WEEK"
    )
    default_meal_count: int = Field(default=3, validation_alias="DEFAULT_MEAL_COUNT")
    min_user_age: int = Field(default=18, validation_alias="MIN_USER_AGE")

    # --- Future AI service (empty = disabled; set once the `ai` repo is deployed) ---
    ai_service_url: str = Field(default="", validation_alias="AI_SERVICE_URL")
    ai_service_timeout_seconds: float = Field(
        default=5.0, validation_alias="AI_SERVICE_TIMEOUT_SECONDS"
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
