import os
import re
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/news",
    tags=["News"],
)


# ============================================================
# GNEWS CONFIGURATION
# ============================================================

GNEWS_API_URL = "https://gnews.io/api/v4/top-headlines"

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")


# ============================================================
# NEWS SETTINGS
# ============================================================

MAX_NEWS = 5

GNEWS_FETCH_COUNT = 10

COUNTRY = "in"

CATEGORY = "technology"


# ============================================================
# STRICT TECHNOLOGY KEYWORDS
# ============================================================

TECHNOLOGY_KEYWORDS = {
    # --------------------------------------------------------
    # Artificial Intelligence
    # --------------------------------------------------------
    "artificial intelligence",
    "artificial-intelligence",
    "ai model",
    "ai models",
    "ai agent",
    "ai agents",
    "ai assistant",
    "ai assistants",
    "generative ai",
    "genai",
    "machine learning",
    "deep learning",
    "large language model",
    "large language models",
    "llm",
    "llms",
    "foundation model",
    "foundation models",
    "multimodal ai",
    "computer vision",
    "natural language processing",
    "nlp",
    "retrieval augmented generation",
    "rag",
    "ai automation",
    "ai chatbot",
    "ai chatbots",
    "neural network",
    "neural networks",
    "transformer model",
    "transformer models",
    "ai inference",
    "ai training",
    "ai infrastructure",
    "ai research",
    # --------------------------------------------------------
    # AI Companies / Products
    # --------------------------------------------------------
    "openai",
    "chatgpt",
    "google ai",
    "google deepmind",
    "deepmind",
    "gemini",
    "gemini ai",
    "microsoft ai",
    "azure ai",
    "meta ai",
    "nvidia",
    "anthropic",
    "claude",
    "claude ai",
    "hugging face",
    "huggingface",
    "mistral ai",
    "xai",
    "grok",
    # --------------------------------------------------------
    # Software Development
    # --------------------------------------------------------
    "software development",
    "software engineering",
    "software engineer",
    "developer",
    "developers",
    "programming",
    "programmer",
    "coding",
    "code generation",
    "developer tools",
    "developer platform",
    "api",
    "apis",
    "sdk",
    "github",
    "gitlab",
    "open source",
    "opensource",
    "python",
    "javascript",
    "typescript",
    "java",
    "golang",
    "rust",
    "fastapi",
    "langchain",
    "langgraph",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "kubernetes",
    "docker",
    # --------------------------------------------------------
    # Cloud
    # --------------------------------------------------------
    "cloud computing",
    "cloud technology",
    "cloud platform",
    "cloud platforms",
    "cloud infrastructure",
    "cloud service",
    "cloud services",
    "aws",
    "amazon web services",
    "microsoft azure",
    "azure",
    "google cloud",
    "gcp",
    "cloud native",
    "serverless",
    "containerization",
    "containers",
    # --------------------------------------------------------
    # Cybersecurity
    # --------------------------------------------------------
    "cybersecurity",
    "cyber security",
    "information security",
    "infosec",
    "data breach",
    "ransomware",
    "malware",
    "phishing",
    "zero day",
    "zero-day",
    "security vulnerability",
    "software vulnerability",
    "network security",
    "cloud security",
    "application security",
    "identity security",
    "endpoint security",
    "security patch",
    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------
    "data science",
    "data engineering",
    "big data",
    "data analytics",
    "database",
    "databases",
    "postgresql",
    "mysql",
    "mongodb",
    "vector database",
    "vector databases",
    "vector search",
    "data center",
    "data centers",
    # --------------------------------------------------------
    # Robotics / Automation
    # --------------------------------------------------------
    "robotics",
    "robot",
    "robots",
    "humanoid robot",
    "humanoid robots",
    "industrial robot",
    "industrial robots",
    "intelligent automation",
    "autonomous systems",
    "autonomous vehicle",
    "autonomous vehicles",
    "self driving",
    "self-driving",
    # --------------------------------------------------------
    # Hardware
    # --------------------------------------------------------
    "semiconductor",
    "semiconductors",
    "processor",
    "processors",
    "gpu",
    "gpus",
    "cpu",
    "cpus",
    "ai chip",
    "ai chips",
    "ai accelerator",
    "ai accelerators",
    "graphics processor",
    "graphics processing unit",
    "microchip",
    "microchips",
    "chip manufacturing",
    "chipmaker",
    "chipmakers",
    "silicon",
    # --------------------------------------------------------
    # Emerging Technology
    # --------------------------------------------------------
    "quantum computing",
    "quantum computer",
    "quantum computers",
    "quantum technology",
    "edge computing",
    "edge ai",
    "internet of things",
    "iot",
    "5g technology",
    "6g technology",
    "augmented reality",
    "virtual reality",
    "extended reality",
    "digital twin",
    "blockchain technology",
    "web3 technology",
    "3d printing",
    "additive manufacturing",
    # --------------------------------------------------------
    # Enterprise Technology
    # --------------------------------------------------------
    "enterprise software",
    "enterprise ai",
    "enterprise technology",
    "digital transformation",
    "technology infrastructure",
    "it infrastructure",
    "information technology",
    "it services",
    "saas",
    "software as a service",
    "platform engineering",
    "devops",
    "devsecops",
    "mlops",
    "aiops",
}


# ============================================================
# STRONG TECHNOLOGY KEYWORDS
# ============================================================

STRONG_TECH_KEYWORDS = {
    "artificial intelligence",
    "generative ai",
    "machine learning",
    "deep learning",
    "large language model",
    "llm",
    "ai agent",
    "ai agents",
    "computer vision",
    "natural language processing",
    "openai",
    "chatgpt",
    "gemini",
    "deepmind",
    "anthropic",
    "claude",
    "nvidia",
    "hugging face",
    "huggingface",
    "robotics",
    "cybersecurity",
    "cyber security",
    "semiconductor",
    "semiconductors",
    "gpu",
    "gpus",
    "ai chip",
    "ai chips",
    "cloud computing",
    "cloud infrastructure",
    "software development",
    "developer tools",
    "quantum computing",
    "pytorch",
    "tensorflow",
    "github",
    "kubernetes",
    "docker",
    "langchain",
    "langgraph",
    "rag",
}


# ============================================================
# EXCLUDE NON-TECH / LIFESTYLE CONTENT
# ============================================================

EXCLUDE_KEYWORDS = {
    # --------------------------------------------------------
    # Sports
    # --------------------------------------------------------
    "cricket",
    "football",
    "soccer",
    "tennis",
    "basketball",
    "baseball",
    "hockey",
    "golf",
    "olympics",
    "ipl",
    "fifa",
    "premier league",
    "world cup",
    "match report",
    "live score",
    "scorecard",
    "fixtures",
    "league table",
    "athlete",
    "athletes",
    "stadium",
    "tournament",
    "esports",
    # --------------------------------------------------------
    # Entertainment
    # --------------------------------------------------------
    "movie",
    "movies",
    "film",
    "films",
    "actor",
    "actress",
    "celebrity",
    "celebrities",
    "hollywood",
    "bollywood",
    "television",
    "tv show",
    "tv shows",
    "music",
    "singer",
    "album",
    "song",
    "concert",
    "box office",
    # --------------------------------------------------------
    # Gaming
    # --------------------------------------------------------
    "video game",
    "video games",
    "gaming",
    "game release",
    "game releases",
    "playstation",
    "xbox",
    "nintendo",
    "steam game",
    "gameplay",
    "gaming console",
    "gaming consoles",
    # --------------------------------------------------------
    # Lifestyle
    # --------------------------------------------------------
    "recipe",
    "recipes",
    "restaurant",
    "travel",
    "tourism",
    "fashion",
    "beauty",
    "fitness",
    "relationship",
    "relationships",
    "vacation",
    "dating",
    # --------------------------------------------------------
    # Emotional / Social AI
    # --------------------------------------------------------
    "emotional support",
    "emotional ai",
    "mental health",
    "feelings",
    "loneliness",
    "anxiety",
    "anxious",
    "therapy chatbot",
    "ai therapist",
    "ai companion",
    "virtual companion",
    "emotional companion",
    "talk to ai",
    "talking to ai",
    "comforting",
    "comfort",
    "difficult feelings",
    # --------------------------------------------------------
    # Finance-only content
    # --------------------------------------------------------
    "stock market",
    "stock price",
    "share price",
    "shares rise",
    "shares fall",
    "investor",
    "investors",
    "trading",
    "trader",
    "market rally",
    "market crash",
    "earnings",
    "dividend",
}


# ============================================================
# TEXT CLEANING
# ============================================================


def clean_text(value: Any) -> str:
    """
    Convert a value into normalized searchable text.
    """

    if value is None:
        return ""

    text = str(value)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip().lower()


# ============================================================
# BUILD SEARCH TEXT
# ============================================================


def build_search_text(
    article: Dict[str, Any],
) -> str:
    """
    Combine title, description, content and source.
    """

    title = clean_text(article.get("title"))

    description = clean_text(article.get("description"))

    content = clean_text(article.get("content"))

    source = clean_text(article.get("source"))

    return " ".join(
        [
            title,
            description,
            content,
            source,
        ]
    )


# ============================================================
# CHECK EXCLUDED TOPICS
# ============================================================


def contains_excluded_topic(
    article: Dict[str, Any],
) -> bool:
    """
    Reject articles that are clearly unrelated
    to professional technology news.
    """

    title = clean_text(article.get("title"))

    description = clean_text(article.get("description"))

    content = clean_text(article.get("content"))

    # --------------------------------------------------------
    # Important:
    #
    # Exclusion in the TITLE is stronger than exclusion
    # appearing somewhere deep in the article content.
    # --------------------------------------------------------

    for keyword in EXCLUDE_KEYWORDS:

        if keyword in title:
            return True

    # --------------------------------------------------------
    # For description/content, require stronger confidence.
    # --------------------------------------------------------

    exclusion_count = 0

    combined = " ".join(
        [
            description,
            content,
        ]
    )

    for keyword in EXCLUDE_KEYWORDS:

        if keyword in combined:
            exclusion_count += 1

    return exclusion_count >= 2


# ============================================================
# TECHNOLOGY RELEVANCE SCORE
# ============================================================


def technology_relevance_score(
    article: Dict[str, Any],
) -> int:
    """
    Calculate how strongly the article is related
    to professional AI / IT / technology.
    """

    title = clean_text(article.get("title"))

    description = clean_text(article.get("description"))

    content = clean_text(article.get("content"))

    source = clean_text(article.get("source"))

    score = 0

    # --------------------------------------------------------
    # Strong technology keywords
    # --------------------------------------------------------

    for keyword in STRONG_TECH_KEYWORDS:

        if keyword in title:

            score += 15

        elif keyword in description:

            score += 8

        elif keyword in content:

            score += 3

        elif keyword in source:

            score += 2

    # --------------------------------------------------------
    # General technology keywords
    # --------------------------------------------------------

    for keyword in TECHNOLOGY_KEYWORDS:

        if keyword in title:

            score += 6

        elif keyword in description:

            score += 3

        elif keyword in content:

            score += 1

    return score


# ============================================================
# CHECK TECHNOLOGY RELEVANCE
# ============================================================


def is_technology_article(
    article: Dict[str, Any],
) -> bool:
    """
    Return True only for meaningful professional
    technology / AI / IT articles.
    """

    text = build_search_text(article)

    if not text:
        return False

    # --------------------------------------------------------
    # Reject lifestyle / emotional / entertainment etc.
    # --------------------------------------------------------

    if contains_excluded_topic(article):
        return False

    title = clean_text(article.get("title"))

    description = clean_text(article.get("description"))

    content = clean_text(article.get("content"))

    # --------------------------------------------------------
    # Require technology relevance.
    # --------------------------------------------------------

    score = technology_relevance_score(article)

    # --------------------------------------------------------
    # Professional AI/IT keyword in title.
    # --------------------------------------------------------

    professional_title_terms = {
        "ai",
        "artificial intelligence",
        "generative ai",
        "machine learning",
        "deep learning",
        "llm",
        "large language model",
        "software",
        "software development",
        "developer",
        "developers",
        "programming",
        "coding",
        "cloud",
        "cloud computing",
        "cybersecurity",
        "cyber security",
        "robotics",
        "robot",
        "semiconductor",
        "chip",
        "gpu",
        "data center",
        "data centres",
        "openai",
        "chatgpt",
        "gemini",
        "anthropic",
        "claude",
        "nvidia",
        "github",
        "kubernetes",
        "docker",
        "langchain",
        "langgraph",
        "rag",
        "pytorch",
        "tensorflow",
        "quantum computing",
    }

    has_professional_title = any(
        keyword in title for keyword in professional_title_terms
    )

    # --------------------------------------------------------
    # Strong AI/IT article
    # --------------------------------------------------------

    if has_professional_title and score >= 8:

        return True

    # --------------------------------------------------------
    # Strong technology article based on body
    # --------------------------------------------------------

    if score >= 15:

        return True

    return False


# ============================================================
# CLEAN ARTICLE
# ============================================================


def clean_article(
    article: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert GNews article to Streamlit structure.
    """

    source_data = article.get(
        "source",
        {},
    )

    if isinstance(
        source_data,
        dict,
    ):

        source_name = source_data.get("name") or "Unknown Source"

    else:

        source_name = str(source_data or "Unknown Source")

    article_url = article.get("url") or ""

    # --------------------------------------------------------
    # If URL accidentally arrives as Markdown:
    #
    # [https://example.com](https://example.com)
    #
    # extract the actual URL.
    # --------------------------------------------------------

    markdown_match = re.search(
        r"\]\((https?://[^)]+)\)",
        article_url,
    )

    if markdown_match:

        article_url = markdown_match.group(1)

    return {
        "title": (article.get("title") or "Technology News"),
        "description": (article.get("description") or ""),
        "content": (article.get("content") or ""),
        "url": article_url,
        "image": (article.get("image") or ""),
        "publishedAt": (article.get("publishedAt") or ""),
        "source": source_name,
    }


# ============================================================
# REMOVE DUPLICATES
# ============================================================


def remove_duplicate_articles(
    articles: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Remove duplicate articles using URL/title.
    """

    unique_articles = []

    seen = set()

    for article in articles:

        url = clean_text(article.get("url"))

        title = clean_text(article.get("title"))

        identifier = url if url else title

        if not identifier:
            continue

        if identifier in seen:
            continue

        seen.add(identifier)

        unique_articles.append(article)

    return unique_articles


# ============================================================
# FETCH GNEWS
# ============================================================


async def fetch_gnews_articles() -> List[Dict[str, Any]]:
    """
    Fetch technology headlines from GNews.
    """

    # --------------------------------------------------------
    # Read environment variable again at request time.
    # --------------------------------------------------------

    api_key = os.getenv("GNEWS_API_KEY")

    if not api_key:

        raise HTTPException(
            status_code=500,
            detail=(
                "GNEWS_API_KEY is not configured. "
                "Add GNEWS_API_KEY to your .env file."
            ),
        )

    params = {
        "apikey": api_key,
        "category": CATEGORY,
        "country": COUNTRY,
        "lang": "en",
        "max": GNEWS_FETCH_COUNT,
    }

    try:

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(
                GNEWS_API_URL,
                params=params,
            )

        # ----------------------------------------------------
        # GNews API error
        # ----------------------------------------------------

        if response.status_code != 200:

            try:

                error_data = response.json()

            except Exception:

                error_data = {"error": response.text}

            raise HTTPException(
                status_code=response.status_code,
                detail=error_data,
            )

        # ----------------------------------------------------
        # Parse response
        # ----------------------------------------------------

        data = response.json()

        articles = data.get(
            "articles",
            [],
        )

        if not isinstance(
            articles,
            list,
        ):

            return []

        return articles

    except httpx.TimeoutException:

        raise HTTPException(
            status_code=504,
            detail="GNews request timed out.",
        )

    except httpx.RequestError as error:

        raise HTTPException(
            status_code=502,
            detail=("Unable to connect to GNews: " f"{str(error)}"),
        )


# ============================================================
# TECHNOLOGY NEWS ENDPOINT
# ============================================================


@router.get("/technology")
async def get_technology_news():
    """
    Return the top 5 professional AI / IT /
    technology news articles.

    Pipeline:

        GNews
          ↓
        Technology category
          ↓
        Clean articles
          ↓
        Remove duplicates
          ↓
        Remove lifestyle / entertainment / sports /
        emotional AI / finance-only content
          ↓
        Technology relevance scoring
          ↓
        Sort by relevance + date
          ↓
        Return top 5
    """

    # ========================================================
    # FETCH
    # ========================================================

    raw_articles = await fetch_gnews_articles()

    # ========================================================
    # CLEAN
    # ========================================================

    cleaned_articles = []

    for article in raw_articles:

        if not isinstance(
            article,
            dict,
        ):

            continue

        cleaned = clean_article(article)

        cleaned_articles.append(cleaned)

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    cleaned_articles = remove_duplicate_articles(cleaned_articles)

    # ========================================================
    # FILTER TECHNOLOGY ARTICLES
    # ========================================================

    technology_articles = []

    for article in cleaned_articles:

        if is_technology_article(article):

            score = technology_relevance_score(article)

            article["_technology_score"] = score

            technology_articles.append(article)

    # ========================================================
    # SORT
    # ========================================================

    technology_articles.sort(
        key=lambda article: (
            article.get(
                "_technology_score",
                0,
            ),
            article.get(
                "publishedAt",
                "",
            ),
        ),
        reverse=True,
    )

    # ========================================================
    # TOP 5
    # ========================================================

    technology_articles = technology_articles[:MAX_NEWS]

    # ========================================================
    # REMOVE INTERNAL SCORE
    # ========================================================

    final_articles = []

    for article in technology_articles:

        article.pop(
            "_technology_score",
            None,
        )

        final_articles.append(article)

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "category": "technology",
        "focus": (
            "Professional AI, Artificial Intelligence, "
            "Software, IT, Cloud, Cybersecurity, "
            "Developer Technology, Data, Robotics "
            "and Semiconductors"
        ),
        "count": len(final_articles),
        "articles": final_articles,
    }
