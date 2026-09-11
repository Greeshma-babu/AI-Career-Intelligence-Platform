import streamlit as st

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

    /* Remove default Streamlit spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1400px;
    }

    /* Main background */
    .stApp {
        background-color: #ffffff;
    }

    /* Header */
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 2px;
    }

    .main-title .brand {
        color: #111827;
    }

    .subtitle {
        color: #64748b;
        font-size: 16px;
        margin-left: 10px;
        font-weight: 400;
    }

    .description {
        color: #475569;
        font-size: 14px;
        margin-top: 4px;
        margin-bottom: 15px;
    }

    /* Navigation buttons */
    div.stButton > button {
        width: 100%;
        height: 48px;
        border-radius: 8px;
        border: 1px solid #d9dee7;
        background-color: #f8fafc;
        color: #334155;
        font-size: 15px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        border-color: #3b82f6;
        color: #2563eb;
    }

    /* Upload box */
    [data-testid="stFileUploader"] {
        border: 2px dashed #dce2e9;
        border-radius: 10px;
        padding: 8px;
        background-color: #fafbfc;
    }

    /* Metric cards */
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #dfe4ea;
        border-radius: 10px;
        padding: 22px 10px;
        text-align: center;
        min-height: 115px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
        color: #3b82d0;
        margin-bottom: 4px;
    }

    .metric-value.green {
        color: #07883e;
        font-size: 23px;
    }

    .metric-label {
        color: #475569;
        font-size: 14px;
    }

    /* Section title */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #111827;
        margin-top: 12px;
        margin-bottom: 8px;
    }

    /* Entity chips */
    .chip {
        display: inline-block;
        padding: 7px 13px;
        margin-right: 6px;
        margin-bottom: 7px;
        background-color: #dff8e9;
        color: #14532d;
        border-radius: 18px;
        font-size: 13px;
        font-weight: 600;
    }

    /* Skills */
    .skill-chip {
        display: inline-block;
        padding: 7px 14px;
        margin-right: 7px;
        margin-bottom: 7px;
        background-color: #dff8e9;
        color: #14532d;
        border-radius: 18px;
        font-size: 13px;
        font-weight: 600;
    }

    /* File success message */
    .success-box {
        padding: 12px 15px;
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 8px;
        color: #065f46;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    /* Hide Streamlit menu/footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        <span class="brand">TalentPulse</span>
        <span class="subtitle">AI Career Intelligence Platform</span>
    </div>

    <div class="description">
        Resume Analysis &nbsp;·&nbsp; Live Market Trends &nbsp;·&nbsp; AI Career Coach
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NAVIGATION
# ============================================================

nav1, nav2, nav3, nav4, nav5 = st.columns(5)

with nav1:
    resume_tab = st.button("My Resume", use_container_width=True)

with nav2:
    market_tab = st.button("Market Trends", use_container_width=True)

with nav3:
    skill_tab = st.button("Skill Gap", use_container_width=True)

with nav4:
    news_tab = st.button("My News Feed", use_container_width=True)

with nav5:
    coach_tab = st.button("Career Coach", use_container_width=True)


st.divider()


# ============================================================
# SESSION STATE
# ============================================================

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "resume"

if resume_tab:
    st.session_state.active_tab = "resume"

if market_tab:
    st.session_state.active_tab = "market"

if skill_tab:
    st.session_state.active_tab = "skill"

if news_tab:
    st.session_state.active_tab = "news"

if coach_tab:
    st.session_state.active_tab = "coach"


# ============================================================
# RESUME ANALYSIS
# ============================================================

if st.session_state.active_tab == "resume":

    st.markdown(
        "<h3 style='font-size:18px;'>Tab 1 — Resume Analysis</h3>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Resume Upload
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload your resume", type=["pdf", "docx"], label_visibility="collapsed"
    )

    if uploaded_file:

        st.markdown(
            f"""
            <div class="success-box">
                Resume uploaded successfully: <b>{uploaded_file.name}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value">82</div>
                <div class="metric-label">Match Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value">12</div>
                <div class="metric-label">Skills Found</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value green">Strong</div>
                <div class="metric-label">Language Grade</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # NER Extracted Entities
    # --------------------------------------------------------

    st.markdown(
        "<div class='section-title'>NER — Extracted Entities</div>",
        unsafe_allow_html=True,
    )

    entities = ["John Smith", "MIT", "Google", "4 years", "New York"]

    entity_html = ""

    for entity in entities:
        entity_html += f"""
        <span class="chip">{entity}</span>
        """

    st.markdown(entity_html, unsafe_allow_html=True)

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    st.markdown(
        "<div class='section-title'>Skills on Resume</div>", unsafe_allow_html=True
    )

    skills = ["Python", "NLP", "FastAPI", "Docker", "PostgreSQL", "NLTK"]

    skill_html = ""

    for skill in skills:
        skill_html += f"""
        <span class="skill-chip">{skill}</span>
        """

    st.markdown(skill_html, unsafe_allow_html=True)


# ============================================================
# MARKET TRENDS
# ============================================================

elif st.session_state.active_tab == "market":

    st.markdown(
        "<h3 style='font-size:18px;'>Tab 2 — Market Trends</h3>", unsafe_allow_html=True
    )

    st.info(
        "Market Trends module will display current job demand, "
        "technology trends and salary insights."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("AI Jobs", "24,580", "+18%")

    with col2:
        st.metric("Python Demand", "High", "+12%")

    with col3:
        st.metric("GenAI Demand", "Very High", "+35%")


# ============================================================
# SKILL GAP
# ============================================================

elif st.session_state.active_tab == "skill":

    st.markdown(
        "<h3 style='font-size:18px;'>Tab 3 — Skill Gap Analysis</h3>",
        unsafe_allow_html=True,
    )

    st.write(
        "Compare your current resume skills with skills required "
        "for your target AI job."
    )

    required_skills = [
        "Python",
        "Machine Learning",
        "LangChain",
        "LangGraph",
        "RAG",
        "FastAPI",
        "Docker",
    ]

    st.markdown(
        "<div class='section-title'>Recommended Skills</div>", unsafe_allow_html=True
    )

    skill_html = ""

    for skill in required_skills:
        skill_html += f"""
        <span class="skill-chip">{skill}</span>
        """

    st.markdown(skill_html, unsafe_allow_html=True)


# ============================================================
# NEWS FEED
# ============================================================

elif st.session_state.active_tab == "news":

    st.markdown(
        "<h3 style='font-size:18px;'>Tab 4 — My News Feed</h3>", unsafe_allow_html=True
    )

    st.write("Personalized AI and technology news based on your career profile.")

    st.info("News feed integration can be connected to an external news API.")


# ============================================================
# CAREER COACH
# ============================================================

elif st.session_state.active_tab == "coach":

    st.markdown(
        "<h3 style='font-size:18px;'>Tab 5 — Career Coach</h3>", unsafe_allow_html=True
    )

    question = st.text_input(
        "Ask your AI Career Coach",
        placeholder="Example: What AI skills should I learn next?",
    )

    if st.button("Get Career Advice"):

        if question:

            st.markdown(
                """
                <div class="success-box">
                    Based on your profile, focus on Generative AI,
                    RAG, LangGraph, FastAPI and deployment skills.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            st.warning("Please enter a question.")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <br>
    <hr>
    <div style="text-align:center;color:#94a3b8;font-size:12px;">
        TalentPulse — AI Career Intelligence Platform
    </div>
    """,
    unsafe_allow_html=True,
)
