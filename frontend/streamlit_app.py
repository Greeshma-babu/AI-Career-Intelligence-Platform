import re
import html
import streamlit as st
import requests
import plotly.graph_objects as go

# ============================================================
# HELPERS
# ============================================================


def entity_icon(entity, index=0):
    """Pick a display icon for a named entity."""

    default_cycle = ["👤", "🎓", "🏢", "📅", "📍"]

    if isinstance(entity, dict):

        etype = (entity.get("type") or "").upper()
        text = entity.get("text", entity.get("name", ""))

        type_icons = {
            "PERSON": "👤",
            "PER": "👤",
            "ORG": "🏢",
            "ORGANIZATION": "🏢",
            "EDU": "🎓",
            "EDUCATION": "🎓",
            "GPE": "📍",
            "LOC": "📍",
            "LOCATION": "📍",
            "DATE": "📅",
            "DURATION": "📅",
        }

        if etype in type_icons:
            return type_icons[etype], text

        entity = text

    text = str(entity)
    lowered = text.lower()

    if re.search(r"\byears?\b|\bmonths?\b|\d{4}\b", lowered):
        return "📅", text

    if any(
        k in lowered
        for k in [
            "university",
            "institute",
            "college",
            "school",
        ]
    ):
        return "🎓", text

    if any(
        k in lowered
        for k in [
            "inc",
            "llc",
            "corp",
            "ltd",
            "technologies",
            "systems",
        ]
    ):
        return "🏢", text

    return (
        default_cycle[index % len(default_cycle)],
        text,
    )


# ============================================================
# CAREER COACH RESPONSE CLEANING
# ============================================================


def clean_career_response(answer):
    """
    Clean Gemini Career Coach response.

    Ensures:
    - plain text
    - no Markdown
    - no HTML
    - no SVG artifacts
    - maximum 3 sentences
    """

    if not answer:
        return ""

    answer = str(answer).strip()

    # --------------------------------------------------------
    # Remove SVG / localhost / Markdown link artifacts
    # --------------------------------------------------------

    answer = re.sub(
        r"\[.*?\]\((?:https?://|/)[^)]+\)",
        "",
        answer,
        flags=re.IGNORECASE,
    )

    answer = re.sub(
        r"\[svg\]",
        "",
        answer,
        flags=re.IGNORECASE,
    )

    answer = re.sub(
        r"https?://localhost:\d+[^\s)]*",
        "",
        answer,
        flags=re.IGNORECASE,
    )

    # --------------------------------------------------------
    # Remove HTML tags
    # --------------------------------------------------------

    answer = re.sub(
        r"<[^>]*>",
        "",
        answer,
    )

    # --------------------------------------------------------
    # Remove Markdown formatting
    # --------------------------------------------------------

    answer = re.sub(
        r"```.*?```",
        "",
        answer,
        flags=re.DOTALL,
    )

    answer = re.sub(
        r"^#{1,6}\s*",
        "",
        answer,
        flags=re.MULTILINE,
    )

    answer = re.sub(
        r"^\s*[-*•]\s*",
        "",
        answer,
        flags=re.MULTILINE,
    )

    answer = re.sub(
        r"^\s*\d+[.)]\s*",
        "",
        answer,
        flags=re.MULTILINE,
    )

    answer = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        answer,
    )

    answer = re.sub(
        r"__(.*?)__",
        r"\1",
        answer,
    )

    answer = re.sub(
        r"\*(.*?)\*",
        r"\1",
        answer,
    )

    answer = re.sub(
        r"`(.*?)`",
        r"\1",
        answer,
    )

    # --------------------------------------------------------
    # Decode HTML entities
    # --------------------------------------------------------

    answer = html.unescape(answer)

    # --------------------------------------------------------
    # Remove excessive whitespace
    # --------------------------------------------------------

    answer = re.sub(
        r"\s+",
        " ",
        answer,
    ).strip()

    # --------------------------------------------------------
    # Maximum 3 sentences
    # --------------------------------------------------------

    sentence_matches = re.findall(
        r"[^.!?]+[.!?]+|[^.!?]+$",
        answer,
    )

    if sentence_matches:

        sentences = [
            sentence.strip() for sentence in sentence_matches if sentence.strip()
        ]

        answer = " ".join(sentences[:3]).strip()

    return answer


# ============================================================
# MARKET TRENDS API
# ============================================================


MARKET_TRENDS_URL = "http://127.0.0.1:8000/api/market/trends"


def fetch_market_trends(
    query="AI Engineer",
    location=None,
):
    """
    Fetch market trend information from FastAPI.

    Streamlit does not communicate directly with Adzuna.
    FastAPI handles the Adzuna API communication.
    """

    params = {
        "query": query,
        "country": "in",
        "pages": 2,
        "results_per_page": 50,
    }

    if location and location.strip():

        params["location"] = location.strip()

    try:

        response = requests.get(
            MARKET_TRENDS_URL,
            params=params,
            timeout=120,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ Cannot connect to FastAPI.\n\n"
            "Start your backend with:\n\n"
            "`python -m uvicorn main:app --reload`"
        )

        return None

    except requests.exceptions.Timeout:

        st.error("❌ Market Trends request timed out. " "Please try again.")

        return None

    except requests.exceptions.HTTPError:

        st.error(f"❌ Market Trends API Error: " f"{response.status_code}")

        try:

            error_data = response.json()

            st.json(error_data)

        except Exception:

            st.write(response.text)

        return None

    except Exception as e:

        st.error(f"❌ Error while fetching market trends: {e}")

        return None


# ============================================================
# NEWS FEED API
# ============================================================


NEWS_FEED_URL = "http://127.0.0.1:8000/api/news/technology"


def fetch_technology_news():
    """
    Fetch top 5 technology news articles
    from the FastAPI GNews endpoint.
    """

    try:

        response = requests.get(
            NEWS_FEED_URL,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ Cannot connect to FastAPI.\n\n"
            "Start your backend with:\n\n"
            "`python -m uvicorn main:app --reload`"
        )

        return None

    except requests.exceptions.Timeout:

        st.error("❌ Technology News request timed out. " "Please try again.")

        return None

    except requests.exceptions.HTTPError:

        st.error(f"❌ News Feed API Error: " f"{response.status_code}")

        try:

            error_data = response.json()

            st.json(error_data)

        except Exception:

            st.write(response.text)

        return None

    except Exception as e:

        st.error(f"❌ Error while fetching technology news: {e}")

        return None


# ============================================================
# CLEAN NEWS URL
# ============================================================


def clean_news_url(article_url):
    """
    Convert a Markdown-style URL into a real URL.
    """

    if not article_url:
        return ""

    article_url = str(article_url).strip()

    markdown_match = re.search(
        r"\]\((https?://[^)\s]+)\)",
        article_url,
    )

    if markdown_match:

        article_url = markdown_match.group(1)

    if article_url.startswith("["):

        second_match = re.search(
            r"\[.*?\]\((https?://[^)\s]+)\)",
            article_url,
        )

        if second_match:

            article_url = second_match.group(1)

    article_url = article_url.strip("\"'")

    return article_url


# ============================================================
# PAGE CONFIGURATION
# ============================================================


st.set_page_config(
    page_title="TalentPulse - AI Career Intelligence Platform",
    page_icon="👩🏻‍💻",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================


st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL PAGE
       ======================================================== */

    html,
    body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    section.main,
    .main {

        background-color: #F8FAFC !important;

    }

    [data-testid="stMain"] {

        background-color: #F8FAFC !important;

    }

    .block-container {

        background-color: #F8FAFC !important;
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;

    }


    /* ========================================================
       STREAMLIT HEADER
       ======================================================== */

    [data-testid="stHeader"] {

        background-color: #F8FAFC !important;

    }

    [data-testid="stToolbar"] {

        background-color: #F8FAFC !important;

    }


    /* ========================================================
       HEADER
       ======================================================== */

    .tp-header {

        background-color: #F8FAFC !important;
        padding: 15px 0 10px 0;

    }

    .tp-title {

        font-size: 32px;
        font-weight: 700;
        color: #172033 !important;
        margin-bottom: 5px;

    }

    .tp-subtitle {

        font-size: 15px;
        color: #64748B !important;
        margin-bottom: 20px;
        line-height: 1.5;

    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .section-title {

        font-size: 21px;
        font-weight: 650;
        color: #172033 !important;
        margin-top: 18px;
        margin-bottom: 14px;

    }


    /* ========================================================
       HEADINGS
       ======================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {

        color: #172033 !important;

    }


    /* ========================================================
       NORMAL TEXT
       ======================================================== */

    p {

        color: #334155 !important;

    }


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploader"] {

        background-color: #FFFFFF !important;
        border: 1px solid #D9E2EC !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow:
            0 2px 8px rgba(
                15,
                23,
                42,
                0.04
            ) !important;

    }

    [data-testid="stFileUploaderDropzone"] {

        background-color: #FFFFFF !important;
        border: 1.5px dashed #CBD5E1 !important;
        border-radius: 10px !important;

    }

    [data-testid="stFileUploaderDropzone"] p {

        color: #475569 !important;

    }

    [data-testid="stFileUploaderDropzone"] span {

        color: #475569 !important;

    }

    [data-testid="stFileUploaderDropzone"] button {

        background-color: #7B68EE !important;
        color: #FFFFFF !important;
        border: 1px solid #7B68EE !important;
        border-radius: 7px !important;
        font-weight: 600 !important;

    }

    [data-testid="stFileUploaderDropzone"] button:hover {

        background-color: #6A5ACD !important;
        color: #FFFFFF !important;
        border-color: #6A5ACD !important;

    }


    /* ========================================================
       UPLOADED FILE
       ======================================================== */

    [data-testid="stFileUploaderFile"] {

        background-color: #F8FAFC !important;
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;

    }


    /* ========================================================
       SUCCESS BOX
       ======================================================== */

    .success-box {

        padding: 10px 15px;
        border-radius: 8px;
        background-color: #ECFDF5 !important;
        border: 1px solid #BBF7D0 !important;
        margin-top: 10px;
        margin-bottom: 10px;
        color: #166534 !important;

    }

    .success-box b {

        color: #166534 !important;

    }


    /* ========================================================
       TEXT AREA
       ======================================================== */

    [data-testid="stTextArea"] {

        background-color: #FFFFFF !important;

    }

    [data-testid="stTextArea"] textarea {

        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;

    }

    [data-testid="stTextArea"] textarea:focus {

        border-color: #4338CA !important;
        box-shadow: 0 0 0 1px #4338CA !important;

    }

    [data-testid="stTextArea"] textarea::placeholder {

        color: #94A3B8 !important;

    }


    /* ========================================================
       SELECT BOX
       ======================================================== */

    [data-testid="stSelectbox"] {

        background-color: #F1F5F9 !important;
        border-radius: 10px !important;

    }

    [data-testid="stSelectbox"] > div {

        background-color: #F1F5F9 !important;

    }

    [data-testid="stSelectbox"] label {

        color: #334155 !important;
        font-weight: 600 !important;

    }


    /* ========================================================
       SELECT BOX - BASEWEB LIGHT OVERRIDE
       ======================================================== */

    div[data-baseweb="select"] {

        background-color: #F1F5F9 !important;

    }

    div[data-baseweb="select"] > div {

        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;

    }

    div[data-baseweb="select"] input {

        background-color: #F1F5F9 !important;
        color: #1E293B !important;

    }

    div[data-baseweb="select"] span {

        color: #1E293B !important;

    }

    div[data-baseweb="select"] svg {

        fill: #475569 !important;

    }


    /* ========================================================
       SELECT BOX - POPUP
       ======================================================== */

    div[data-baseweb="popover"] {

        background-color: #FFFFFF !important;

    }

    div[data-baseweb="popover"] > div {

        background-color: #FFFFFF !important;

    }

    div[data-baseweb="menu"] {

        background-color: #FFFFFF !important;

    }

    div[data-baseweb="menu"] li {

        background-color: #FFFFFF !important;
        color: #1E293B !important;

    }

    div[data-baseweb="menu"] li:hover {

        background-color: #F1F5F9 !important;
        color: #0F172A !important;

    }


    /* ========================================================
       MARKET FILTER AREA
       ======================================================== */

    .market-filter-card {

        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 18px 20px 8px 20px !important;
        margin-bottom: 18px !important;
        box-shadow:
            0 2px 8px rgba(
                15,
                23,
                42,
                0.04
            ) !important;

    }

    .market-filter-title {

        color: #172033 !important;
        font-size: 15px !important;
        font-weight: 650 !important;
        margin-bottom: 8px !important;

    }


    /* ========================================================
       MARKET SEARCH SUMMARY
       ======================================================== */

    .market-summary {

        background-color: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 9px !important;
        padding: 11px 15px !important;
        margin-top: 8px !important;
        margin-bottom: 18px !important;
        color: #334155 !important;
        font-size: 14px !important;

    }

    .market-summary b {

        color: #172033 !important;

    }


    /* ========================================================
       NAVIGATION BUTTONS
       ======================================================== */

    div.stButton > button {

        background-color: #FFFFFF !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        min-height: 38px !important;

    }

    div.stButton > button:hover {

        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        border-color: #CBD5E1 !important;

    }


    /* ========================================================
       ANALYZE BUTTON
       ======================================================== */

    div.stButton > button[kind="primary"] {

        background-color: #7B68EE !important;
        color: #FFFFFF !important;
        border: 1px solid #7B68EE !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 240px !important;
        min-height: 42px !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow:
            0 2px 5px rgba(
                123,
                104,
                238,
                0.20
            ) !important;

    }

    div.stButton > button[kind="primary"]:hover {

        background-color: #6A5ACD !important;
        color: #FFFFFF !important;
        border-color: #6A5ACD !important;

    }


    /* ========================================================
       METRIC CARDS
       ======================================================== */

    .metric-card {

        padding: 18px;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        text-align: center;
        background-color: #FFFFFF !important;
        box-shadow:
            0 2px 8px rgba(
                15,
                23,
                42,
                0.04
            );

    }

    .metric-value {

        font-size: 28px;
        font-weight: 700;
        color: #4338CA !important;

    }

    .metric-label {

        font-size: 14px;
        color: #64748B !important;

    }


    /* ========================================================
       SKILL CHIPS
       ======================================================== */

    .skill-chip {

        display: inline-block;
        padding: 6px 12px;
        margin: 4px;
        border-radius: 20px;
        background-color: #EEF2FF !important;
        border: 1px solid #C7D2FE !important;
        color: #4338CA !important;
        font-size: 14px;
        font-weight: 500;

    }


    /* ========================================================
       ENTITY CHIPS
       ======================================================== */

    .entity-chip {

        display: inline-block;
        padding: 6px 14px;
        margin: 4px;
        border-radius: 20px;
        background-color: #ECFDF5 !important;
        border: 1px solid #A7F3D0 !important;
        color: #065F46 !important;
        font-size: 14px;
        font-weight: 600;

    }


    /* ========================================================
       MATCHED SKILLS
       ======================================================== */

    .matched-chip {

        display: inline-block;
        padding: 6px 14px;
        margin: 4px;
        border-radius: 20px;
        background-color: #ECFDF5 !important;
        border: 1px solid #A7F3D0 !important;
        color: #065F46 !important;
        font-size: 14px;
        font-weight: 600;

    }


    /* ========================================================
       MISSING SKILLS
       ======================================================== */

    .missing-chip {

        display: inline-block;
        padding: 6px 14px;
        margin: 4px;
        border-radius: 20px;
        background-color: #FFF7ED !important;
        border: 1px solid #FED7AA !important;
        color: #9A3412 !important;
        font-size: 14px;
        font-weight: 600;

    }


    /* ========================================================
       NEWS FEED
       ======================================================== */

    .news-description {

        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        margin-top: 8px !important;
        margin-bottom: 12px !important;
        color: #334155 !important;
        font-size: 15px !important;
        line-height: 1.6 !important;

        display: -webkit-box;
        -webkit-line-clamp: 5;
        -webkit-box-orient: vertical;
        overflow: hidden;

    }

    .news-meta {

        color: #64748B !important;
        font-size: 13px !important;
        margin-top: 8px !important;
        margin-bottom: 10px !important;

    }

    .news-read-link {

        display: inline-block;
        padding: 8px 16px;
        background-color: #2563EB;
        color: #FFFFFF !important;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 14px;
        margin-top: 4px;

    }

    .news-read-link:hover {

        background-color: #1D4ED8;
        color: #FFFFFF !important;
        text-decoration: none !important;

    }


    /* ========================================================
       NEWS IMAGE
       ======================================================== */

    .news-image {

        width: 240px !important;
        max-width: 240px !important;
        height: 135px !important;
        object-fit: cover !important;
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
        margin-bottom: 12px !important;

    }


    /* ========================================================
       EXPANDER
       ======================================================== */

    [data-testid="stExpander"] {

        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;

    }

    [data-testid="stExpander"] summary {

        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 16px !important;

    }

    [data-testid="stExpander"] summary:hover {

        color: #2563EB !important;

    }


    /* ========================================================
       ALERTS
       ======================================================== */

    [data-testid="stAlert"] {

        background-color: #FFFFFF !important;
        border-radius: 9px !important;

    }

    [data-testid="stAlert"] p {

        color: #334155 !important;

    }


    /* ========================================================
       CAREER COACH
       ======================================================== */

    .career-chat-container {

        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 18px;
        margin: 12px 0 18px 0;

    }

    .career-message {

        width: 100%;
        margin: 12px 0;

    }

    .career-user-row {

        display: flex;
        justify-content: flex-end;
        align-items: flex-start;
        gap: 10px;
        width: 100%;

    }

    .career-bot-row {

        display: flex;
        justify-content: flex-start;
        align-items: flex-start;
        gap: 10px;
        width: 100%;

    }

    .career-icon {

        width: 38px;
        height: 38px;
        min-width: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 21px;
        box-shadow:
            0 2px 7px rgba(
                15,
                23,
                42,
                .10
            );

    }

    .career-icon.user-icon {

        background: #DBEAFE;
        border: 1px solid #BFDBFE;

    }

    .career-icon.bot-icon {

        background: #EDE9FE;
        border: 1px solid #DDD6FE;

    }

    .career-bubble {

        max-width: 78%;
        padding: 12px 16px;
        border-radius: 16px;
        line-height: 1.6;
        font-size: 14px;
        word-wrap: break-word;

    }

    .career-bubble.user-bubble {

        background: #2563EB;
        color: #FFFFFF;
        border-bottom-right-radius: 5px;

    }

    .career-bubble.bot-bubble {

        background: #FFFFFF;
        color: #000000 !important;
        border: 1px solid #E2E8F0;
        border-bottom-left-radius: 5px;
        box-shadow:
            0 2px 8px rgba(
                15,
                23,
                42,
                .06
            );

    }

    /* ========================================================
       CAREER COACH AI RESPONSE
       ======================================================== */

    .career-ai-response {

        color: #000000 !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        margin-top: 4px !important;
        padding: 0 !important;

    }

    .career-ai-response * {

        color: #000000 !important;

    }

    .career-ai-response p {

        color: #000000 !important;
        margin: 0 !important;
        padding: 0 !important;

    }

    .career-ai-response span {

        color: #000000 !important;

    }

    .career-ai-response div {

        color: #000000 !important;

    }

    .career-role {

        font-size: 11px;
        font-weight: 700;
        margin-bottom: 4px;
        opacity: .75;

    }

    .career-input-label {

        font-weight: 700;
        color: #334155;
        margin-bottom: 6px;

    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {

        text-align: center;
        color: #64748B !important;
        font-size: 13px;
        margin-top: 40px;
        padding: 20px;

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================


st.markdown(
    '<div class="tp-header">'
    '<div class="tp-title">TalentPulse</div>'
    '<div class="tp-subtitle">'
    "AI Career Intelligence Platform<br>"
    "Resume Analysis · Live Market Trends · AI Career Coach"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================


if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📄 My Resume"


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


if "market_result" not in st.session_state:
    st.session_state.market_result = None


# ============================================================
# CAREER COACH SESSION STATE
# ============================================================


if "career_answer" not in st.session_state:
    st.session_state.career_answer = ""


if "career_sources" not in st.session_state:
    st.session_state.career_sources = []


if "career_model" not in st.session_state:
    st.session_state.career_model = ""


if "career_question" not in st.session_state:
    st.session_state.career_question = ""


if "clear_career_question" not in st.session_state:
    st.session_state.clear_career_question = False


if "career_chat_history" not in st.session_state:
    st.session_state.career_chat_history = []


# ============================================================
# NAVIGATION
# ============================================================


nav_cols = st.columns(5)

tabs = [
    "📄 My Resume",
    "📊 Market Trends",
    "📰 My News Feed",
    "🤖 Career Coach",
    "ℹ️ About",
]


for i, tab in enumerate(tabs):

    with nav_cols[i]:

        if st.button(
            tab,
            use_container_width=True,
            key=f"nav_{i}",
        ):

            st.session_state.active_tab = tab


active_tab = st.session_state.active_tab


# ============================================================
# MY RESUME
# ============================================================


if active_tab == "📄 My Resume":

    st.markdown(
        '<div class="section-title">' "Resume & Job Description" "</div>",
        unsafe_allow_html=True,
    )

    resume_col, jd_col = st.columns(2)

    # ========================================================
    # RESUME
    # ========================================================

    with resume_col:

        st.markdown("### 📄 Upload Resume")

        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=["pdf", "docx"],
            label_visibility="collapsed",
        )

        if uploaded_file:

            st.markdown(
                '<div class="success-box">'
                "✅ Resume uploaded successfully<br>"
                f"<b>{uploaded_file.name}</b>"
                "</div>",
                unsafe_allow_html=True,
            )

    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    with jd_col:

        st.markdown("### 💼 Job Description")

        job_description = st.text_area(
            "Paste Job Description",
            placeholder=(
                "Paste the complete job description here...\n\n"
                "Example:\n"
                "We are looking for an AI/ML Engineer with "
                "experience in Python, Machine Learning, NLP, "
                "LangChain, RAG, FastAPI and Docker."
            ),
            height=100,
            label_visibility="collapsed",
        )

    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    st.markdown(
        "<div style='height:8px'></div>",
        unsafe_allow_html=True,
    )

    analyze_button = st.button(
        "🔍 Analyze Resume",
        use_container_width=False,
        type="primary",
    )

    # ========================================================
    # ANALYZE
    # ========================================================

    if analyze_button:

        if uploaded_file is None:

            st.warning("⚠️ Please upload your resume before analyzing.")

            st.stop()

        if not job_description.strip():

            st.warning("⚠️ Please enter the job description before analyzing.")

            st.stop()

        with st.spinner("Processing resume with TalentPulse NLP pipeline..."):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/api/resume/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    },
                    data={"job_description": job_description},
                    timeout=120,
                )

                if response.status_code == 200:

                    result = response.json()

                    st.session_state.analysis_result = result

                    st.session_state.career_answer = ""
                    st.session_state.career_sources = []
                    st.session_state.career_model = ""
                    st.session_state.career_chat_history = []
                    st.session_state.career_question = ""
                    st.session_state.clear_career_question = False

                    st.success(
                        "✅ Resume preprocessing and analysis "
                        "completed successfully."
                    )

                else:

                    st.error(f"❌ FastAPI Error: " f"{response.status_code}")

                    try:

                        st.json(response.json())

                    except Exception:

                        st.write(response.text)

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to FastAPI.\n\n"
                    "Start your backend with:\n\n"
                    "`python -m uvicorn main:app --reload`"
                )

            except requests.exceptions.Timeout:

                st.error("❌ FastAPI request timed out. " "Please try again.")

            except Exception as e:

                st.error(f"❌ Error while analyzing resume: {e}")

    # ========================================================
    # RESULTS
    # ========================================================

    if st.session_state.analysis_result:

        result = st.session_state.analysis_result

        st.markdown(
            '<div class="section-title">' "Resume Analysis" "</div>",
            unsafe_allow_html=True,
        )

        # ====================================================
        # GET BACKEND VALUES
        # ====================================================

        resume_skills = result.get(
            "resume_skills",
            [],
        )

        jd_skills = result.get(
            "job_required_skills",
            [],
        )

        matched_skills = result.get(
            "matched_skills",
            [],
        )

        missing_skills = result.get(
            "missing_skills",
            [],
        )

        skill_match_percentage = result.get(
            "skill_match_percentage",
            0,
        )

        # ====================================================
        # METRICS
        # ====================================================

        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:

            st.markdown(
                '<div class="metric-card">'
                '<div class="metric-value">'
                f"{skill_match_percentage}%"
                "</div>"
                '<div class="metric-label">'
                "Skill Match"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        with metric2:

            st.markdown(
                '<div class="metric-card">'
                '<div class="metric-value">'
                f"{len(resume_skills)}"
                "</div>"
                '<div class="metric-label">'
                "Resume Skills"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        with metric3:

            st.markdown(
                '<div class="metric-card">'
                '<div class="metric-value">'
                f"{len(matched_skills)}"
                "</div>"
                '<div class="metric-label">'
                "Matched Skills"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        with metric4:

            st.markdown(
                '<div class="metric-card">'
                '<div class="metric-value">'
                f"{len(missing_skills)}"
                "</div>"
                '<div class="metric-label">'
                "Missing Skills"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        # ====================================================
        # RESUME SKILLS
        # ====================================================

        st.markdown(
            '<div class="section-title">' "🛠️ Skills Detected in Resume" "</div>",
            unsafe_allow_html=True,
        )

        if resume_skills:

            skill_html = ""

            for skill in resume_skills:

                skill_html += f'<span class="skill-chip">' f"{skill}" f"</span>"

            st.markdown(
                skill_html,
                unsafe_allow_html=True,
            )

        else:

            st.info("No resume skills were detected.")

        # ====================================================
        # JOB DESCRIPTION SKILLS
        # ====================================================

        st.markdown(
            '<div class="section-title">' "🎯 Skills Required by Job" "</div>",
            unsafe_allow_html=True,
        )

        if jd_skills:

            skill_html = ""

            for skill in jd_skills:

                skill_html += f'<span class="skill-chip">' f"{skill}" f"</span>"

            st.markdown(
                skill_html,
                unsafe_allow_html=True,
            )

        else:

            st.info("No job description skills were detected.")

        # ====================================================
        # MATCHED SKILLS
        # ====================================================

        st.markdown(
            '<div class="section-title">' "✅ Matched Skills" "</div>",
            unsafe_allow_html=True,
        )

        if matched_skills:

            matched_html = ""

            for skill in matched_skills:

                matched_html += f'<span class="matched-chip">' f"✓ {skill}" f"</span>"

            st.markdown(
                matched_html,
                unsafe_allow_html=True,
            )

        else:

            st.info("No matching skills found.")

        # ====================================================
        # MISSING SKILLS
        # ====================================================

        st.markdown(
            '<div class="section-title">' "⚠️ Missing Skills" "</div>",
            unsafe_allow_html=True,
        )

        if missing_skills:

            missing_html = ""

            for skill in missing_skills:

                missing_html += f'<span class="missing-chip">' f"⚠ {skill}" f"</span>"

            st.markdown(
                missing_html,
                unsafe_allow_html=True,
            )

        else:

            st.success("🎉 No missing skills detected.")

        # ====================================================
        # API RESPONSE
        # ====================================================

        with st.expander("🔍 View Backend Response"):

            st.json(result)


# ============================================================
# MARKET TRENDS
# ============================================================


elif active_tab == "📊 Market Trends":

    st.markdown(
        '<div class="section-title">' "📊 AI Job Market Trends" "</div>",
        unsafe_allow_html=True,
    )

    # ========================================================
    # SEARCH CONTROLS
    # ========================================================

    st.markdown(
        '<div class="market-filter-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="market-filter-title">' "🔎 Market Search" "</div>",
        unsafe_allow_html=True,
    )

    search_col1, search_col2 = st.columns(2)

    with search_col1:

        market_query = st.selectbox(
            "Job Role",
            [
                "AI Engineer",
                "Machine Learning Engineer",
                "Data Scientist",
                "Data Engineer",
                "Generative AI Engineer",
                "NLP Engineer",
                "Computer Vision Engineer",
                "Software Engineer",
                "Backend Engineer",
                "Python Developer",
                "DevOps Engineer",
                "MLOps Engineer",
                "QA Engineer",
                "Automation Engineer",
            ],
            index=0,
            key="market_job_role",
        )

    with search_col2:

        market_location = st.selectbox(
            "Location",
            [
                "India",
                "Bangalore",
                "Hyderabad",
                "Chennai",
                "Pune",
                "Mumbai",
                "Delhi",
                "Gurugram",
                "Noida",
                "Kochi",
                "Remote",
            ],
            index=0,
            key="market_location",
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # ========================================================
    # FETCH MARKET DATA
    # ========================================================

    fetch_button = st.button(
        "🔍 Fetch Job Market Trends",
        type="primary",
        use_container_width=False,
    )

    if fetch_button:

        with st.spinner("Fetching live job market data..."):

            market_data = fetch_market_trends(
                query=market_query,
                location=market_location,
            )

            if market_data:

                st.session_state.market_result = market_data

                st.success("✅ Job market trends fetched successfully.")

    # ========================================================
    # DISPLAY MARKET RESULTS
    # ========================================================

    if st.session_state.market_result:

        market_data = st.session_state.market_result

        # ====================================================
        # BACKEND VALUES
        # ====================================================

        total_jobs = market_data.get(
            "total_jobs",
            0,
        )

        top_skills = market_data.get(
            "top_skills",
            [],
        )

        top_roles = market_data.get(
            "top_roles",
            [],
        )

        query_used = market_data.get(
            "query",
            market_query,
        )

        location_used = market_data.get(
            "location",
            market_location,
        )

        # ====================================================
        # SEARCH SUMMARY
        # ====================================================

        st.markdown(
            f'<div class="market-summary">'
            f"<b>Search:</b> {query_used}"
            f"&nbsp;&nbsp;&nbsp;&nbsp;"
            f"<b>Location:</b> "
            f"{location_used or 'India'}"
            f"</div>",
            unsafe_allow_html=True,
        )

        # ====================================================
        # METRICS
        # ====================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Jobs Analyzed",
                f"{total_jobs:,}",
            )

        with col2:

            st.metric(
                "Skills Detected",
                len(top_skills),
            )

        with col3:

            st.metric(
                "Roles Detected",
                len(top_roles),
            )

        # ====================================================
        # TRENDING SKILLS + JOB ROLES
        # ====================================================

        chart_col1, chart_col2 = st.columns([1.25, 0.85])

        # ====================================================
        # TRENDING SKILLS — LEFT
        # ====================================================

        with chart_col1:

            st.markdown("### 🔥 Trending Skills")

            st.caption("Skill demand across available job postings.")

            if top_skills:

                skill_names = []
                skill_percentages = []
                skill_job_counts = []

                for item in top_skills:

                    skill_names.append(
                        item.get(
                            "skill",
                            "Unknown",
                        )
                    )

                    skill_percentages.append(
                        float(
                            item.get(
                                "percentage",
                                0,
                            )
                            or 0
                        )
                    )

                    skill_job_counts.append(
                        int(
                            item.get(
                                "job_count",
                                0,
                            )
                            or 0
                        )
                    )

                skill_fig = go.Figure()

                skill_fig.add_trace(
                    go.Bar(
                        x=skill_names,
                        y=skill_percentages,
                        name="Skill Demand (%)",
                        text=[f"{value:.1f}%" for value in skill_percentages],
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate=(
                            "<b>%{x}</b><br>" "Demand: %{y:.1f}%" "<extra></extra>"
                        ),
                        marker=dict(
                            color="#7B68EE",
                        ),
                    )
                )

                skill_fig.add_trace(
                    go.Scatter(
                        x=skill_names,
                        y=skill_job_counts,
                        name="Job Postings",
                        mode="lines+markers+text",
                        yaxis="y2",
                        text=[f"{count:,}" for count in skill_job_counts],
                        textposition="top center",
                        hovertemplate=(
                            "<b>%{x}</b><br>" "Job Postings: %{y:,}" "<extra></extra>"
                        ),
                        line=dict(
                            width=3,
                            color="#F59E0B",
                        ),
                        marker=dict(
                            size=8,
                        ),
                    )
                )

                skill_fig.update_layout(
                    height=430,
                    margin=dict(
                        l=50,
                        r=60,
                        t=45,
                        b=105,
                    ),
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    hovermode="x unified",
                    font=dict(
                        color="#111827",
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        font=dict(
                            color="#111827",
                        ),
                    ),
                    xaxis=dict(
                        title=dict(
                            text="Skills",
                            font=dict(
                                size=13,
                                color="#111827",
                            ),
                        ),
                        tickfont=dict(
                            size=10,
                            color="#111827",
                        ),
                        tickangle=-35,
                        automargin=True,
                        showgrid=False,
                    ),
                    yaxis=dict(
                        title=dict(
                            text="Percentage (%)",
                            font=dict(
                                size=13,
                                color="#111827",
                            ),
                        ),
                        tickfont=dict(
                            size=10,
                            color="#111827",
                        ),
                        ticksuffix="%",
                        rangemode="tozero",
                        showgrid=True,
                        gridcolor="#E2E8F0",
                    ),
                    yaxis2=dict(
                        title=dict(
                            text="No. of Job Postings",
                            font=dict(
                                size=13,
                                color="#111827",
                            ),
                        ),
                        tickfont=dict(
                            size=10,
                            color="#111827",
                        ),
                        overlaying="y",
                        side="right",
                        rangemode="tozero",
                        showgrid=False,
                    ),
                    barmode="group",
                )

                st.plotly_chart(
                    skill_fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": False,
                    },
                )

            else:

                st.info("No trending skills were detected.")

        # ====================================================
        # JOB ROLES — RIGHT
        # ====================================================

        with chart_col2:

            st.markdown("### 💼 Job Roles")

            st.caption("Distribution of detected job roles.")

            if top_roles:

                role_names = []
                role_counts = []

                for item in top_roles:

                    role_names.append(
                        item.get(
                            "role",
                            "Unknown",
                        )
                    )

                    role_counts.append(
                        int(
                            item.get(
                                "job_count",
                                0,
                            )
                            or 0
                        )
                    )

                role_fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=role_names,
                            values=role_counts,
                            hole=0.45,
                            text=[
                                f"{role}<br>{count:,}"
                                for role, count in zip(
                                    role_names,
                                    role_counts,
                                )
                            ],
                            textinfo="text",
                            textposition="inside",
                            insidetextorientation="horizontal",
                            hovertemplate=(
                                "<b>%{label}</b><br>"
                                "Job Postings: %{value:,}<br>"
                                "Share: %{percent}"
                                "<extra></extra>"
                            ),
                            textfont=dict(
                                size=11,
                                color="#111827",
                            ),
                            marker=dict(
                                line=dict(
                                    color="#FFFFFF",
                                    width=2,
                                )
                            ),
                        )
                    ]
                )

                role_fig.update_layout(
                    height=330,
                    margin=dict(
                        l=5,
                        r=5,
                        t=15,
                        b=80,
                    ),
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    font=dict(
                        color="#111827",
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.08,
                        xanchor="center",
                        x=0.5,
                        font=dict(
                            size=9,
                            color="#111827",
                        ),
                    ),
                )

                st.plotly_chart(
                    role_fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": False,
                    },
                )

            else:

                st.info("No job roles were detected.")

        # ====================================================
        # RAW MARKET RESPONSE
        # ====================================================

        with st.expander("🔍 View Market Trends Backend Response"):

            st.json(market_data)

    else:

        st.info(
            "Select a job role and location, then click " "**Fetch Job Market Trends**."
        )


# ============================================================
# NEWS FEED
# ============================================================


elif active_tab == "📰 My News Feed":

    st.markdown(
        '<div class="section-title">' "📰 Latest Technology News" "</div>",
        unsafe_allow_html=True,
    )

    # ========================================================
    # FETCH NEWS
    # ========================================================

    with st.spinner("Fetching latest technology news..."):

        news_data = fetch_technology_news()

    # ========================================================
    # DISPLAY NEWS
    # ========================================================

    if news_data:

        articles = news_data.get(
            "articles",
            [],
        )

        articles = articles[:5]

        if articles:

            for index, article in enumerate(
                articles,
                start=1,
            ):

                title = (
                    article.get(
                        "title",
                        "Technology News",
                    )
                    or "Technology News"
                )

                description = (
                    article.get(
                        "description",
                        "",
                    )
                    or ""
                )

                source = (
                    article.get(
                        "source",
                        "Unknown Source",
                    )
                    or "Unknown Source"
                )

                published_at = (
                    article.get(
                        "publishedAt",
                        "",
                    )
                    or ""
                )

                article_url = (
                    article.get(
                        "url",
                        "",
                    )
                    or ""
                )

                image_url = (
                    article.get(
                        "image",
                        "",
                    )
                    or ""
                )

                article_url = clean_news_url(article_url)

                with st.expander(
                    f"📰 {index}. {title}",
                    expanded=False,
                ):

                    if image_url:

                        try:

                            st.image(
                                image_url,
                                width=240,
                            )

                        except Exception:

                            pass

                    if description.strip():

                        description_text = description.strip()

                        words = description_text.split()

                        if len(words) > 70:

                            description_text = " ".join(words[:70]) + "..."

                        st.markdown(
                            f"""
                            <div class="news-description">
                                {description_text}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    else:

                        st.markdown(
                            """
                            <div class="news-description">
                                Description is not available
                                for this article.
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    meta_parts = []

                    if source:

                        meta_parts.append(f"📰 {source}")

                    if published_at:

                        meta_parts.append(f"🕒 {published_at}")

                    if meta_parts:

                        st.markdown(
                            '<div class="news-meta">'
                            + " &nbsp;&nbsp; ".join(meta_parts)
                            + "</div>",
                            unsafe_allow_html=True,
                        )

                    if article_url:

                        st.link_button(
                            "Read Full Article →",
                            article_url,
                            type="primary",
                        )

                    else:

                        st.caption("Article link is not available.")

        else:

            st.info("No technology news articles were found.")

    else:

        st.info("Technology news is currently unavailable.")


# ============================================================
# CAREER COACH — RAG + GEMINI
# ============================================================


elif active_tab == "🤖 Career Coach":

    st.markdown(
        '<div class="section-title">' "🤖 AI Career Coach" "</div>",
        unsafe_allow_html=True,
    )

    # ========================================================
    # CAREER CHAT HISTORY
    # ========================================================

    if "career_chat_history" not in st.session_state:

        st.session_state.career_chat_history = []

    # ========================================================
    # CLEAR QUESTION BEFORE WIDGET CREATION
    # ========================================================

    if st.session_state.clear_career_question:

        st.session_state.career_question = ""

        st.session_state.clear_career_question = False

    # ========================================================
    # RESUME CHECK
    # ========================================================

    if not st.session_state.analysis_result:

        st.info("📄 Please analyze your resume first " "to use the AI Career Coach.")

    else:

        # ====================================================
        # CAREER COACH DESCRIPTION
        # ====================================================

        st.markdown(
            """
            <div class="market-summary">
                <b>RAG-powered Career Intelligence</b>
                &nbsp;&nbsp;&nbsp;&nbsp;
                Ask questions about your resume, skills,
                career path and target job.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ====================================================
        # QUICK QUESTIONS
        # ====================================================

        st.markdown("#### 💡 Try asking")

        example_col1, example_col2, example_col3 = st.columns(3)

        # ====================================================
        # SKILL GAP
        # ====================================================

        with example_col1:

            if st.button(
                "🎯 Skill Gap",
                use_container_width=True,
                key="career_skill_gap",
            ):

                st.session_state.career_question = (
                    "What skills am I missing for my target job?"
                )

                st.rerun()

        # ====================================================
        # CAREER PATH
        # ====================================================

        with example_col2:

            if st.button(
                "🚀 Career Path",
                use_container_width=True,
                key="career_path",
            ):

                st.session_state.career_question = (
                    "How can I transition my current experience "
                    "into an AI Engineer career?"
                )

                st.rerun()

        # ====================================================
        # WHAT TO LEARN
        # ====================================================

        with example_col3:

            if st.button(
                "📚 What to Learn",
                use_container_width=True,
                key="career_learning",
            ):

                st.session_state.career_question = (
                    "What should I learn next to become an AI Engineer?"
                )

                st.rerun()

        # ====================================================
        # CHAT HISTORY
        # ====================================================

        if st.session_state.career_chat_history:

            st.markdown(
                '<div class="career-chat-container">',
                unsafe_allow_html=True,
            )

            for message in st.session_state.career_chat_history:

                content = str(
                    message.get(
                        "content",
                        "",
                    )
                )

                # =================================================
                # USER MESSAGE
                # =================================================

                if message.get("role") == "user":

                    st.markdown(
                        '<div class="career-message">',
                        unsafe_allow_html=True,
                    )

                    user_col1, user_col2 = st.columns([0.88, 0.12])

                    with user_col1:

                        st.markdown(
                            """
                            <div style="
                                display:flex;
                                justify-content:flex-end;
                            ">
                                <div class="career-bubble user-bubble">
                                    <div class="career-role">
                                        You
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # User content remains plain Streamlit text.
                        st.markdown(content)

                    with user_col2:

                        st.markdown(
                            """
                            <div class="career-icon user-icon">
                                👤
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True,
                    )

                # =================================================
                # AI MESSAGE
                # =================================================

                else:

                    # Clean any previously stored answer too.
                    clean_content = clean_career_response(content)

                    st.markdown(
                        '<div class="career-message">',
                        unsafe_allow_html=True,
                    )

                    bot_col1, bot_col2 = st.columns([0.08, 0.92])

                    with bot_col1:

                        st.markdown(
                            """
                            <div class="career-icon bot-icon">
                                🤖
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with bot_col2:

                        st.markdown(
                            """
                            <div class="career-bubble bot-bubble">
                                <div class="career-role">
                                    AI Career Coach
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # =================================================
                        # CLEAN BLACK AI RESPONSE
                        # =================================================
                        #
                        # IMPORTANT:
                        # Do not render Gemini content with
                        # unsafe_allow_html=True.
                        #
                        # The content is cleaned first and then
                        # displayed inside a black-text container.
                        #

                        safe_content = html.escape(clean_content)

                        st.markdown(
                            f"""
                            <div class="career-ai-response">
                                {safe_content}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True,
                    )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        # ====================================================
        # QUESTION INPUT
        # ====================================================

        st.markdown(
            '<div class="career-input-label">' "💬 Ask your AI Career Coach" "</div>",
            unsafe_allow_html=True,
        )

        user_question = st.text_area(
            "Ask your AI Career Coach",
            placeholder=(
                "Example: What skills should I learn next " "to become an AI Engineer?"
            ),
            height=100,
            key="career_question",
            label_visibility="collapsed",
        )

        # ====================================================
        # ACTION BUTTONS
        # ====================================================

        action_col1, action_col2 = st.columns([1, 0.35])

        # ====================================================
        # ASK BUTTON
        # ====================================================

        with action_col1:

            ask_button = st.button(
                "🤖 Get Career Advice",
                type="primary",
                use_container_width=False,
                key="ask_career_coach",
            )

        # ====================================================
        # CLEAR CHAT
        # ====================================================

        with action_col2:

            clear_button = st.button(
                "🗑️ Clear Chat",
                use_container_width=False,
                key="clear_career_chat",
            )

        # ====================================================
        # CLEAR CHAT
        # ====================================================

        if clear_button:

            st.session_state.career_chat_history = []

            st.session_state.career_answer = ""

            st.session_state.career_sources = []

            st.session_state.career_model = ""

            st.session_state.clear_career_question = True

            st.rerun()

        # ====================================================
        # ASK CAREER COACH
        # ====================================================

        if ask_button:

            question = (user_question or "").strip()

            # =================================================
            # EMPTY QUESTION
            # =================================================

            if not question:

                st.warning("Please enter your career question.")

            else:

                with st.spinner(
                    "🧠 Career Coach is retrieving your "
                    "career context and generating advice..."
                ):

                    try:

                        # =========================================
                        # CALL FASTAPI
                        # =========================================

                        response = requests.post(
                            "http://127.0.0.1:8000/api/career/ask",
                            json={
                                "question": question,
                                "analysis_result": (st.session_state.analysis_result),
                            },
                            timeout=180,
                        )

                        # =========================================
                        # CHECK RESPONSE
                        # =========================================

                        response.raise_for_status()

                        career_data = response.json()

                        # =========================================
                        # ANSWER
                        # =========================================

                        raw_answer = career_data.get(
                            "answer",
                            "",
                        )

                        # =========================================
                        # CLEAN ANSWER
                        # =========================================

                        answer = clean_career_response(raw_answer)

                        if not answer:

                            answer = (
                                "I could not generate a career "
                                "recommendation. Please try again."
                            )

                        # =========================================
                        # STORE ANSWER
                        # =========================================

                        st.session_state.career_answer = answer

                        # =========================================
                        # STORE SOURCES
                        # =========================================

                        st.session_state.career_sources = career_data.get(
                            "sources",
                            [],
                        )

                        # =========================================
                        # STORE MODEL
                        # =========================================

                        st.session_state.career_model = career_data.get(
                            "model",
                            "",
                        )

                        # =========================================
                        # ADD USER MESSAGE
                        # =========================================

                        st.session_state.career_chat_history.append(
                            {
                                "role": "user",
                                "content": question,
                            }
                        )

                        # =========================================
                        # ADD AI MESSAGE
                        # =========================================

                        st.session_state.career_chat_history.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                        # =========================================
                        # CLEAR INPUT ON NEXT RERUN
                        # =========================================

                        st.session_state.clear_career_question = True

                        st.rerun()

                    # =============================================
                    # FASTAPI CONNECTION ERROR
                    # =============================================

                    except requests.exceptions.ConnectionError:

                        st.error(
                            "❌ Cannot connect to FastAPI.\n\n"
                            "Make sure FastAPI is running and the "
                            "Career Coach endpoint is available:\n\n"
                            "`POST /api/career/ask`"
                        )

                    # =============================================
                    # TIMEOUT
                    # =============================================

                    except requests.exceptions.Timeout:

                        st.error(
                            "❌ Career Coach request timed out.\n\n"
                            "Please check your Gemini API connection "
                            "and try again."
                        )

                    # =============================================
                    # HTTP ERROR
                    # =============================================

                    except requests.exceptions.HTTPError:

                        st.error(
                            f"❌ Career Coach API Error: " f"{response.status_code}"
                        )

                        try:

                            error_data = response.json()

                            st.error(
                                str(
                                    error_data.get(
                                        "detail",
                                        "Unknown Career Coach error.",
                                    )
                                )
                            )

                        except Exception:

                            st.write(response.text)

                    # =============================================
                    # OTHER ERROR
                    # =============================================

                    except Exception as e:

                        st.error(f"❌ Career Coach error: {e}")

        # ====================================================
        # RAG SOURCES + MODEL
        # ====================================================

        sources = st.session_state.get(
            "career_sources",
            [],
        )

        model = st.session_state.get(
            "career_model",
            "",
        )

        info_parts = []

        # ====================================================
        # RAG CONTEXT
        # ====================================================

        if sources:

            info_parts.append(
                "RAG Context: " + ", ".join(str(source) for source in sources)
            )

        # ====================================================
        # MODEL
        # ====================================================

        if model:

            info_parts.append(f"Model: {model}")

        # ====================================================
        # DISPLAY
        # ====================================================

        if info_parts:

            st.caption("  |  ".join(info_parts))


# ============================================================
# ABOUT
# ============================================================


elif active_tab == "ℹ️ About":

    st.markdown(
        '<div class="section-title">' "ℹ️ About TalentPulse" "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "**TalentPulse** is an AI-powered Career Intelligence Platform "
        "that transforms resumes and job descriptions into actionable career insights. "
        "It combines NLP, semantic similarity, skill extraction, ATS-style matching, "
        "RAG, and Generative AI to evaluate career alignment, identify skill gaps, "
        "recommend relevant learning areas, and provide personalized AI-powered "
        "career guidance.\n\n"
        "**Core Technologies:** Python · NLP · spaCy · NLTK · "
        "Sentence Transformers · FastAPI · Streamlit · PostgreSQL · pgvector · "
        "LangChain · RAG · Google Gemini API · Docker\n\n"
        "**Author:** Greeshma Babu"
    )


# ============================================================
# FOOTER
# ============================================================


st.markdown(
    '<div class="footer">'
    "TalentPulse · AI Career Intelligence Platform<br>"
    "Resume Analysis · NLP · AI · Career Intelligence"
    "</div>",
    unsafe_allow_html=True,
)
