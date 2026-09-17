import os

import requests
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ADZUNA CONFIGURATION
# ============================================================

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api"


# ============================================================
# ADZUNA CLIENT
# ============================================================


class AdzunaClient:

    def __init__(self):

        self.app_id = os.getenv("MARKET_TRENDS_APPLICATION_ID")

        self.app_key = os.getenv("MARKET_TRENDS_API_KEY")

        self.base_url = ADZUNA_BASE_URL

    # ========================================================
    # SEARCH JOBS
    # ========================================================

    def search_jobs(
        self,
        country="in",
        query="AI Engineer",
        page=1,
        results_per_page=20,
        location=None,
    ):

        # ----------------------------------------------------
        # Validate credentials only when API is used
        # ----------------------------------------------------

        if not self.app_id:

            raise RuntimeError("MARKET_TRENDS_APPLICATION_ID is missing in .env")

        if not self.app_key:

            raise RuntimeError("MARKET_TRENDS_API_KEY is missing in .env")

        # ----------------------------------------------------
        # Build URL
        # ----------------------------------------------------

        url = f"{self.base_url}/jobs/" f"{country}/search/{page}"

        # ----------------------------------------------------
        # Request parameters
        # ----------------------------------------------------

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": results_per_page,
            "what": query,
            "content-type": "application/json",
        }

        if location:
            params["where"] = location

        # ----------------------------------------------------
        # API request
        # ----------------------------------------------------

        try:

            response = requests.get(
                url,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        # ----------------------------------------------------
        # Timeout
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            raise RuntimeError("Adzuna API request timed out.")

        # ----------------------------------------------------
        # HTTP error
        # ----------------------------------------------------

        except requests.exceptions.HTTPError as error:

            raise RuntimeError(f"Adzuna API HTTP error: {error}")

        # ----------------------------------------------------
        # Other request error
        # ----------------------------------------------------

        except requests.exceptions.RequestException as error:

            raise RuntimeError(f"Adzuna API request failed: {error}")

        # ----------------------------------------------------
        # Invalid JSON
        # ----------------------------------------------------

        except ValueError:

            raise RuntimeError("Adzuna returned an invalid JSON response.")
