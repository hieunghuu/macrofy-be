"""
USDA FoodData Central API Client

Uses the USDA FoodData Central API to search and fetch nutritional data.
API documentation: https://portal.ndata.fdc.nal.usda.gov/

ENDPOINTS:
- POST /foods/search - Search for foods by query
- GET /food/{fdcId} - Get detailed food data by ID
- POST /foods/list - Get foods by list of IDs

AUTHENTICATION:
- API key passed as header: X-Api-Key
- Free tier: 1000 requests/day (plenty for seeding + occasional lookups)
"""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class USDANutrientData:
    """Parsed nutritional data from USDA API."""
    fdc_id: int
    description: str
    food_category: str
    calories_per_100g: float
    protein_g_per_100g: float
    fat_g_per_100g: float
    carbs_g_per_100g: float
    fiber_g_per_100g: float
    sugar_g_per_100g: float
    sodium_mg_per_100g: float


class USDANutrientClient:
    """
    Client for USDA FoodData Central API.

    Handles authentication, request formatting, and response parsing.
    Use this to search and fetch food nutritional data.

    Example:
        client = USDANutrientClient()
        results = client.search_foods("chicken breast", page_size=10)
        for food in results:
            print(f"{food.description}: {food.calories_per_100g} cal/100g")
    """

    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    API_KEY: str | None = None  # Set from settings

    def __init__(self, api_key: str | None = None):
        """
        Initialize USDA API client.

        Args:
            api_key: USDA API key. If not provided, uses from settings.
        """
        self.api_key = api_key or settings.usda_api_key
        if not self.api_key:
            logger.warning("USDA API key not configured. Set USDA_API_KEY in .env")

    def _get_headers(self) -> dict[str, str]:
        """Build request headers with API key."""
        return {
            "X-Api-Key": self.api_key or "",
            "Content-Type": "application/json",
        }
    def _get_params(self) -> dict[str, str]:
        return {
             "api_key": self.api_key or "",
        }

    def search_foods(
        self,
        query: str,
        page_size: int = 25,
        page_number: int = 1,
        data_type: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for foods by query string.

        Args:
            query: Search term (e.g., "chicken breast", "broccoli")
            page_size: Number of results per page (max 150)
            page_number: Page number for pagination
            data_type: Filter by data type (e.g., ["Foundation", "SR Legacy", "Branded"])

        Returns:
            List of food items with basic info (not full nutrients).
            Use get_food() to get detailed nutritional data.

        Example response:
            {
                "foods": [
                    {"fdcId": 12345, "description": "Chicken breast...", "dataType": "Foundation"},
                    ...
                ],
                "totalHits": 150,
                "currentPage": 1
            }
        """
        if not self.api_key:
            raise ValueError("USDA API key not configured")

        # USDA API requires POST with JSON body
        payload = {
            "query": query,
            "pageSize": min(page_size, 150),  # API max is 150
            "pageNumber": page_number,
            "dataType": data_type or ["Foundation", "SR Legacy", "Branded"],
            "format": "abridged",
            "nutrients": [203, 204, 205]
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.BASE_URL}/foods/search",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("foods", [])
        except httpx.HTTPError as e:
            logger.error(f"USDA API error: {e}")
            raise

    def get_food(self, fdc_id: int) -> dict[str, Any] | None:
        """
        Get detailed nutritional data for a single food by FDC ID.

        Args:
            fdc_id: The FDC ID from search results

        Returns:
            Full food object with nutrient data, or None if not found.
        """
        if not self.api_key:
            raise ValueError("USDA API key not configured")

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.BASE_URL}/food/{fdc_id}",
                    headers=self._get_headers(),
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"USDA API error fetching food {fdc_id}: {e}")
            return None

    def get_foods_batch(self, fdc_ids: list[int]) -> list[dict[str, Any]]:
        """
        Get multiple foods by their FDC IDs in one request.

        Args:
            fdc_ids: List of FDC IDs (max 20 per request)

        Returns:
            List of food objects with nutritional data.
        """
        if not self.api_key:
            raise ValueError("USDA API key not configured")

        if len(fdc_ids) > 20:
            raise ValueError("Maximum 20 FDC IDs per request")

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.BASE_URL}/foods",
                    headers=self._get_headers(),
                    json={"fdcIds": fdc_ids},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"USDA API error fetching batch: {e}")
            return []

    def _parse_nutrients(self, food_data: dict[str, Any]) -> USDANutrientData | None:
        """
        Parse USDA food data into standardized nutrient format.

        Extracts macros (calories, protein, fat, carbs) per 100g.
        USDA provides nutrients with IDs - we match common ones:
        - 1008: Energy (kcal)
        - 1003: Protein
        - 1004: Total lipid (fat)
        - 1005: Carbohydrate
        - 1079: Fiber
        - 2000: Sugars
        - 1093: Sodium

        Args:
            food_data: Full food object from get_food()

        Returns:
            USDANutrientData with parsed values, or None if parsing fails.
        """
        try:
            # Build nutrient lookup from food.nutrients
            nutrient_map: dict[int, float] = {}
            for nutrient in food_data.get("foodNutrients", []):
                nutrient_id = nutrient.get("nutrient").get("id")
                value = nutrient.get("value") or nutrient.get("amount")
                if nutrient_id is not None and value is not None:
                    nutrient_map[nutrient_id] = float(value)
            # Extract serving size info for conversion
            # Most foods have serving sizes in servingSize or portion
            serving_weight = food_data.get("servingSize")
            if serving_weight is None:
                serving_weight = 100.0  # Default to 100g if no serving size

            # Get macros per 100g (USDA may give per serving, so we normalize)
            serving_ratio = 100.0 / float(serving_weight)

            calories = nutrient_map.get(1008, 0) * serving_ratio
            protein = nutrient_map.get(1003, 0) * serving_ratio
            fat = nutrient_map.get(1004, 0) * serving_ratio
            carbs = nutrient_map.get(1005, 0) * serving_ratio
            fiber = nutrient_map.get(1079, 0) * serving_ratio
            sugar = nutrient_map.get(2000, 0) * serving_ratio
            sodium = nutrient_map.get(1093, 0) * serving_ratio

            return USDANutrientData(
                fdc_id=food_data.get("fdcId",""),
                description=food_data.get("description", ""),
                food_category=food_data.get("foodCategory", {}).get("description", ""),
                calories_per_100g=round(calories, 1),
                protein_g_per_100g=round(protein, 1),
                fat_g_per_100g=round(fat, 1),
                carbs_g_per_100g=round(carbs, 1),
                fiber_g_per_100g=round(fiber, 1),
                sugar_g_per_100g=round(sugar, 1),
                sodium_mg_per_100g=round(sodium, 1),
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Failed to parse nutrients for food {food_data.get('fdcId')}: {e}")
            return None

    def search_and_get_nutrients(
        self,
        query: str,
        page_size: int = 10,
    ) -> list[USDANutrientData]:
        """
        Search for foods and return parsed nutritional data.

        This is a convenience method that combines search + nutrient parsing.

        Args:
            query: Search term
            page_size: How many results to fetch and parse

        Returns:
            List of USDANutrientData with fully parsed nutritional info.
        """
        # Step 1: Search for foods
        search_results = self.search_foods(query, page_size=page_size)
        if not search_results:
            return []

        # Step 2: Get FDC IDs
        fdc_ids = [food["fdcId"] for food in search_results]

        # Step 3: Fetch full data in batch (max 20 at a time)
        all_nutrients = []
        for i in range(0, len(fdc_ids), 20):
            batch_ids = fdc_ids[i : i + 20]
            foods = self.get_foods_batch(batch_ids)
            for food in foods:
                parsed = self._parse_nutrients(food)
                if parsed:
                    all_nutrients.append(parsed)

        return all_nutrients


# Singleton instance for app-wide use
_usda_client: USDANutrientClient | None = None


def get_usda_client() -> USDANutrientClient:
    """Get or create the USDA client singleton."""
    global _usda_client
    if _usda_client is None:
        _usda_client = USDANutrientClient()
    return _usda_client
