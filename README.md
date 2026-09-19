# TalentPulse

AI Career Intelligence Platform: resume analysis, live job market trends, tech news, and a RAG-powered AI career coach.

## Features

- **Resume Analysis**: upload a PDF/DOCX resume and a job description to get extracted skills, matched and missing skills, and a skill match percentage.
- **Market Trends**: live job data from Adzuna, showing trending skills and role distribution by role and location.
- **News Feed**: filtered technology news (AI, software, cloud, cybersecurity) from GNews.
- **Career Coach**: a short, personalized answer grounded in your resume and a career knowledge base, powered by Gemini.

## Tech Stack

Python · Streamlit · FastAPI · spaCy · NLTK · Sentence Transformers · LangChain · FAISS · Google Gemini · Plotly

## Project Structure

```
app/
├── api/         # FastAPI routes: career, market, news, Adzuna client
├── documents/   # Career knowledge base (PDFs) used for RAG
├── ingestion/   # Market trends processing
├── matching/    # Resume-to-job matching
├── nlp/         # Text extraction and preprocessing
└── rag/         # Embeddings, vector store, retriever, prompt, chain
frontend/        # Streamlit UI
main.py          # FastAPI entry point
```

## Setup

```bash
git clone <your-repo-url>
cd AI-Career-Intelligence-Platform
python -m venv venv
venv\Scripts\activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_key
GNEWS_API_KEY=your_key
ADZUNA_APP_ID=your_id
ADZUNA_APP_KEY=your_key
```

## Run

Start the backend, then the frontend in a second terminal:

```bash
python -m uvicorn main:app --reload
streamlit run frontend/streamlit_app.py
```

API docs are available at http://127.0.0.1:8000/docs.

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/resume/upload` | Analyze resume against a job description |
| GET | `/api/market/trends` | Job market skills and roles |
| GET | `/api/news/technology` | Top technology news |
| POST | `/api/career/ask` | Ask the AI Career Coach |

#### Screenshots: 
<img width="1885" height="880" alt="image" src="https://github.com/user-attachments/assets/de57d879-e1ac-455d-bbd9-0f59d8e16134" />
<img width="1865" height="855" alt="image" src="https://github.com/user-attachments/assets/f3bc843b-cc82-4fa9-a141-4f67f9f66f1d" />
<img width="1885" height="807" alt="image" src="https://github.com/user-attachments/assets/9bfa3bfd-8382-4a2b-a7c2-c6467d270412" />
<img width="1866" height="832" alt="image" src="https://github.com/user-attachments/assets/179bf926-8caa-48ad-ae68-eb74a9e0ef54" />
<img width="1877" height="860" alt="4" src="https://github.com/user-attachments/assets/b5a5efa2-bbe8-4910-bb32-606f18efc44b" />


## Author

Greeshma Babu






