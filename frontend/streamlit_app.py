import re
import streamlit as st
import requests

# ============================================================
# HELPERS
# ============================================================


def entity_icon(entity, index=0):
    """Pick a display icon for a named entity.

    Uses the entity's ``type`` when the backend provides structured
    entities (dicts), otherwise falls back to light keyword heuristics
    on the raw text, and finally cycles through a default icon set.
    """

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

    if any(k in lowered for k in ["university", "institute", "college", "school"]):
        return "🎓", text

    if any(
        k in lowered for k in ["inc", "llc", "corp", "ltd", "technologies", "systems"]
    ):
        return "🏢", text

    return default_cycle[index % len(default_cycle)], text


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
       REMOVE DARK STREAMLIT HEADER
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
       RESUME FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D9E2EC !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
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

    /* Browse Files button */

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
       JOB DESCRIPTION TEXT AREA
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
       TEXT INPUT
       ======================================================== */

    [data-testid="stTextInput"] input {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #4338CA !important;
        box-shadow: 0 0 0 1px #4338CA !important;
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

    div.stButton > button:focus:not([kind="primary"]) {
        background-color: #EEF2FF !important;
        color: #3730A3 !important;
        border-color: #4338CA !important;
        box-shadow: none !important;
    }


    /* ========================================================
       ANALYZE RESUME BUTTON
       ======================================================== */

    div.stButton > button[kind="primary"] {
        background-color: #7B68EE !important;
        color: #CBC3E3 !important;
        border: 1px solid #7B68EE !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 240px !important;
        min-height: 42px !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 2px 5px rgba(123, 104, 238, 0.20) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #6A5ACD !important;
        color: #CBC3E3 !important;
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
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
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
       ENTITY CHIPS (Named Entities)
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
       MATCHED SKILL CHIPS
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
       MISSING SKILL CHIPS
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
       ALERT BOXES
       ======================================================== */

    [data-testid="stAlert"] {
        background-color: #FFFFFF !important;
        border-radius: 9px !important;
    }

    [data-testid="stAlert"] p {
        color: #334155 !important;
    }


    /* ========================================================
       DATAFRAME
       ======================================================== */

    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }


    /* ========================================================
       CODE BLOCK
       ======================================================== */

    [data-testid="stCodeBlock"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }


    /* ========================================================
       PROGRESS
       ======================================================== */

    [data-testid="stProgress"] {
        background-color: #E2E8F0 !important;
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
    st.session_state.active_tab = "My Resume"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# ============================================================
# NAVIGATION
# ============================================================

nav_cols = st.columns(6)

tabs = [
    "📄 My Resume",
    "📊 Market Trends",
    "🎯 Skill Gap",
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

if active_tab == "📄 My Resume" or active_tab == "My Resume":

    st.markdown(
        '<div class="section-title">Resume & Job Description</div>',
        unsafe_allow_html=True,
    )

    resume_col, jd_col = st.columns(2)

    # ========================================================
    # RESUME UPLOAD
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
                "We are looking for an AI/ML Engineer with experience "
                "in Python, Machine Learning, NLP, LangChain, RAG, "
                "FastAPI and Docker."
            ),
            height=100,
            label_visibility="collapsed",
        )
    response = requests.post(
        "http://localhost:8000/api/job/description",
        data={"job_description": job_description},
        timeout=60,
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

        elif not job_description.strip():

            st.warning("⚠️ Please enter the job description before analyzing.")

        else:

            with st.spinner("Analyzing resume against the job description..."):

                try:

                    response = requests.post(
                        "http://localhost:8000/api/resume/upload",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        },
                        data={"job_description": job_description},
                        timeout=60,
                    )

                    # ====================================================
                    # SUCCESS
                    # ====================================================

                    if response.status_code == 200:

                        result = response.json()

                        st.session_state.analysis_result = result

                        st.success(
                            "✅ Resume and Job Description analyzed successfully."
                        )

                    # ====================================================
                    # API ERROR
                    # ====================================================

                    else:

                        st.error(f"❌ API Error: {response.status_code}")

                        try:

                            st.json(response.json())

                        except Exception:

                            st.write(response.text)

                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ Cannot connect to FastAPI.\n\n"
                        "Please make sure your backend is running:\n\n"
                        "`http://localhost:8000`"
                    )

                except requests.exceptions.Timeout:

                    st.error("❌ FastAPI request timed out. Please try again.")

                except Exception as e:

                    st.error(f"❌ Error while analyzing resume: {e}")

    # ========================================================
    # ANALYSIS RESULT
    # ========================================================

    if st.session_state.analysis_result:

        result = st.session_state.analysis_result

        st.markdown(
            '<div class="section-title">Resume Analysis</div>',
            unsafe_allow_html=True,
        )

        # ====================================================
        # METRICS
        # ====================================================

        match_score = result.get(
            "match_score",
            82,
        )

        skills_found = result.get(
            "skills_found",
            12,
        )

        language_grade = result.get(
            "language_grade",
            "Strong",
        )

        metric1, metric2, metric3 = st.columns(3)

        with metric1:

            st.markdown(
                '<div class="metric-card">'
                f'<div class="metric-value">{match_score}%</div>'
                '<div class="metric-label">Match Score</div>'
                "</div>",
                unsafe_allow_html=True,
            )

        with metric2:

            st.markdown(
                '<div class="metric-card">'
                f'<div class="metric-value">{skills_found}</div>'
                '<div class="metric-label">Skills Found</div>'
                "</div>",
                unsafe_allow_html=True,
            )

        with metric3:

            st.markdown(
                '<div class="metric-card">'
                f'<div class="metric-value">{language_grade}</div>'
                '<div class="metric-label">Resume Language</div>'
                "</div>",
                unsafe_allow_html=True,
            )

        # ====================================================
        # EXTRACTED SKILLS
        # ====================================================

        st.markdown(
            '<div class="section-title">🛠️ Skills Detected</div>',
            unsafe_allow_html=True,
        )

        skills = result.get(
            "skills",
            [
                "Python",
                "NLP",
                "FastAPI",
                "Docker",
                "PostgreSQL",
                "NLTK",
            ],
        )

        if skills:

            skill_html = ""

            for skill in skills:

                skill_html += f'<span class="skill-chip">{skill}</span>'

            st.markdown(
                skill_html,
                unsafe_allow_html=True,
            )

        else:

            st.info("No skills were detected.")

        # ====================================================
        # NER ENTITIES
        # ====================================================

        st.markdown(
            '<div class="section-title">🔎 Named Entities</div>',
            unsafe_allow_html=True,
        )

        entities = result.get(
            "entities",
            [
                "John Smith",
                "MIT",
                "Google",
                "4 years",
                "New York",
            ],
        )

        if entities:

            entity_html = ""

            for i, entity in enumerate(entities):

                icon, text = entity_icon(entity, i)

                entity_html += f'<span class="entity-chip">{icon} {text}</span>'

            st.markdown(
                entity_html,
                unsafe_allow_html=True,
            )

        else:

            st.info("No named entities detected.")

        # ====================================================
        # MATCHED SKILLS
        # ====================================================

        st.markdown(
            '<div class="section-title">✅ Matched Skills</div>',
            unsafe_allow_html=True,
        )

        matched_skills = result.get(
            "matched_skills",
            skills,
        )

        if matched_skills:

            matched_html = ""

            for skill in matched_skills:

                matched_html += f'<span class="matched-chip">✓ {skill}</span>'

            st.markdown(
                matched_html,
                unsafe_allow_html=True,
            )

        else:

            st.info("No matched skills yet.")

        # ====================================================
        # MISSING SKILLS
        # ====================================================

        st.markdown(
            '<div class="section-title">⚠️ Missing Skills</div>',
            unsafe_allow_html=True,
        )

        missing_skills = result.get(
            "missing_skills",
            [
                "Machine Learning",
                "LangChain",
                "LangGraph",
                "RAG",
            ],
        )

        if missing_skills:

            missing_html = ""

            for skill in missing_skills:

                missing_html += f'<span class="missing-chip">⚠ {skill}</span>'

            st.markdown(
                missing_html,
                unsafe_allow_html=True,
            )

        else:

            st.success("🎉 No major skill gaps detected!")

        # ====================================================
        # RECOMMENDATION
        # ====================================================

        st.markdown(
            '<div class="section-title">💡 AI Recommendation</div>',
            unsafe_allow_html=True,
        )

        recommendation = result.get(
            "recommendation",
            (
                "Your resume has a strong foundation in Python, "
                "NLP and backend technologies. Consider adding "
                "hands-on projects using LangChain, LangGraph, "
                "RAG and Generative AI to improve your match "
                "for AI/ML Engineer roles."
            ),
        )

        st.info(recommendation)


# ============================================================
# MARKET TRENDS
# ============================================================

elif active_tab == "📊 Market Trends":

    st.markdown(
        '<div class="section-title">📊 AI Job Market Trends</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "AI Jobs",
            "24,580",
            "+18%",
        )

    with col2:

        st.metric(
            "Python Demand",
            "High",
            "+12%",
        )

    with col3:

        st.metric(
            "Generative AI",
            "Very High",
            "+35%",
        )

    st.markdown("### 🔥 Trending Skills")

    trending_skills = [
        "Python",
        "Generative AI",
        "LLM",
        "RAG",
        "LangChain",
        "LangGraph",
        "FastAPI",
        "Docker",
        "AWS",
    ]

    for skill in trending_skills:

        st.markdown(
            f'<span class="skill-chip">{skill}</span>',
            unsafe_allow_html=True,
        )


# ============================================================
# SKILL GAP
# ============================================================

elif active_tab == "🎯 Skill Gap":

    st.markdown(
        '<div class="section-title">🎯 Skill Gap Analysis</div>',
        unsafe_allow_html=True,
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

    st.markdown("### Skills Recommended for AI/ML Roles")

    for skill in required_skills:

        st.progress(
            0.75,
            text=f"{skill} - 75%",
        )


# ============================================================
# NEWS FEED
# ============================================================

elif active_tab == "📰 My News Feed":

    st.markdown(
        '<div class="section-title">📰 AI Career News</div>',
        unsafe_allow_html=True,
    )

    st.info("External AI/job news API can be connected here.")

    st.markdown(
        "### 🤖 Generative AI\n"
        "Latest developments in LLMs, RAG, AI agents "
        "and enterprise AI.\n\n"
        "### 💼 AI Jobs\n"
        "Track AI/ML Engineer, GenAI Engineer, "
        "NLP Engineer and AI Automation roles.\n\n"
        "### 🚀 Technology\n"
        "Follow LangChain, LangGraph, FastAPI, "
        "Hugging Face and other AI technologies."
    )


# ============================================================
# CAREER COACH
# ============================================================

elif active_tab == "🤖 Career Coach":

    st.markdown(
        '<div class="section-title">🤖 AI Career Coach</div>',
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
        '<div class="section-title">ℹ️ About TalentPulse</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "**TalentPulse** is an AI-powered Career Intelligence Platform.\n\n"
        "The platform analyzes a candidate's resume against "
        "a target job description and provides:\n\n"
        "- Resume parsing\n"
        "- NLP preprocessing\n"
        "- Skill extraction\n"
        "- Named Entity Recognition\n"
        "- Job description analysis\n"
        "- Resume-JD matching\n"
        "- Skill gap analysis\n"
        "- Career recommendations\n"
        "- AI career coaching"
    )

    st.markdown("### 🏗️ Architecture")

    st.code(
        """User
  │
  ▼
Streamlit Frontend
  │
  ▼
FastAPI Backend
  │
  ├── Resume Parser
  │
  ├── NLP Preprocessing
  │
  ├── Skill Extraction
  │
  ├── NER
  │
  ├── Job Description Analysis
  │
  └── Resume-JD Matching
          │
          ▼
      AI Results""",
        language="text",
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
