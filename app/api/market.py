from fastapi import APIRouter, HTTPException

from app.ingestion.market_trends import get_market_trends

# ============================================================
# MARKET TRENDS ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/market",
    tags=["Market Trends"],
)


# ============================================================
# MARKET TRENDS ENDPOINT
# ============================================================


@router.get("/trends")
def market_trends(
    query: str = "AI Engineer",
    country: str = "in",
    pages: int = 2,
    results_per_page: int = 50,
    location: str | None = None,
):

    try:

        result = get_market_trends(
            query=query,
            country=country,
            pages=pages,
            results_per_page=results_per_page,
            location=location,
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
