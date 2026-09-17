import re
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

    Example:

    [https://example.com/article](https://example.com/article)

    becomes:

    https://example.com/article
    """

    if not article_url:
        return ""

    article_url = str(article_url).strip()

    # --------------------------------------------------------
    # Markdown link:
    # [text](https://example.com)
    # --------------------------------------------------------

    markdown_match = re.search(
        r"\]\((https?://[^)\s]+)\)",
        article_url,
    )

    if markdown_match:

        article_url = markdown_match.group(1)

    # --------------------------------------------------------
    # If the whole value is:
    #
    # [https://example.com](https://example.com)
    #
    # extract URL again safely.
    # --------------------------------------------------------

    if article_url.startswith("["):

        second_match = re.search(
            r"\[.*?\]\((https?://[^)\s]+)\)",
            article_url,
        )

        if second_match:

            article_url = second_match.group(1)

    # --------------------------------------------------------
    # Remove accidental surrounding quotes.
    # --------------------------------------------------------

    article_url = article_url.strip("\"'")

    return article_url


# ============================================================
# PAGE CONFIGURATION
# ============================================================


st.set_page_config(
    page_title="TalentPulse - AI Career Intelligence Platform",
    page_icon="📃",
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

                # =================================================
                # SUCCESS
                # =================================================

                if response.status_code == 200:

                    result = response.json()

                    st.session_state.analysis_result = result

                    st.success(
                        "✅ Resume preprocessing and analysis "
                        "completed successfully."
                    )

                # =================================================
                # API ERROR
                # =================================================

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
        # SIDE BY SIDE
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

                # ------------------------------------------------
                # BAR = SKILL PERCENTAGE
                # ------------------------------------------------

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

                # ------------------------------------------------
                # SECONDARY AXIS = JOB POSTINGS
                # ------------------------------------------------

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

                # ------------------------------------------------
                # CHART LAYOUT
                # ------------------------------------------------

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
                    # Smaller height so the full
                    # chart fits within the page.
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

        # Always restrict frontend to top 5
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

                # =================================================
                # CLEAN URL
                # =================================================

                article_url = clean_news_url(article_url)

                # =================================================
                # NEWS BOX
                # =================================================

                with st.expander(
                    f"📰 {index}. {title}",
                    expanded=False,
                ):

                    # =============================================
                    # IMAGE
                    # =============================================

                    if image_url:

                        try:

                            st.image(
                                image_url,
                                width=240,
                            )

                        except Exception:

                            pass

                    # =============================================
                    # DESCRIPTION
                    # =============================================

                    if description.strip():

                        description_text = description.strip()

                        # Limit description to approximately
                        # five readable lines.
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

                    # =============================================
                    # SOURCE + DATE
                    # =============================================

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

                    # =============================================
                    # READ FULL ARTICLE
                    # =============================================

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
# CAREER COACH
# ============================================================


elif active_tab == "🤖 Career Coach":

    st.markdown(
        '<div class="section-title">' "🤖 AI Career Coach" "</div>",
        unsafe_allow_html=True,
    )

    user_question = st.text_input(
        "Ask your AI Career Coach",
        placeholder=(
            "Example: What skills should I learn " "to become an AI Engineer?"
        ),
    )

    if st.button(
        "Ask Career Coach",
        use_container_width=True,
    ):

        if user_question.strip():

            st.success("AI Career Coach")

            st.markdown(
                "Based on your question, focus on:\n\n"
                "1. Python\n"
                "2. Machine Learning\n"
                "3. NLP\n"
                "4. Generative AI\n"
                "5. RAG\n"
                "6. LangChain\n"
                "7. LangGraph\n"
                "8. FastAPI\n"
                "9. Docker\n"
                "10. Cloud deployment"
            )

        else:

            st.warning("Please enter your question.")


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
        "LangChain · RAG · Ollama · Docker\n\n"
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
