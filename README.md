TalentPulse is a full-stack AI Career Intelligence Platform that combines resume analysis, job market
intelligence, and personalized career coaching into a single, production-grade application. The system
accepts a candidate's resume in PDF or DOCX format alongside a job description and applies a
complete Natural Language Processing pipeline — covering text normalization, tokenization, stemming,
lemmatization, Part-of-Speech tagging, dependency parsing, Named Entity Recognition, and skill
extraction using NLTK and SpaCy.
The platform demonstrates the full evolution of text representation in NLP: from classical methods
including Bag of Words, N-grams, and TF-IDF, through traditional word embeddings with Word2Vec
and GloVe, to modern contextual embeddings using Sentence Transformers. A matching engine
combines semantic similarity, skill overlap, and experience matching to produce a transparent,
explainable ATS-style match score.
Live job postings and technology news are automatically collected every 30 minutes using APScheduler
and httpx, processed through the NLP pipeline, and stored in PostgreSQL with pgvector for semantic
similarity search. Sentiment analysis is performed using both rule-based VADER and transformer-based
DistilBERT. A LangChain Retrieval-Augmented Generation pipeline retrieves relevant job market
chunks from pgvector and passes them to a locally running Ollama LLM to generate grounded, sourcecited career coaching responses — with no cloud API dependency

###### Job Description
An AI Engineer develops intelligent applications using Python, LLMs, RAG, LangChain, LangGraph, and AI Agents. They build NLP, Computer Vision, and Generative AI solutions using frameworks such as PyTorch, TensorFlow, and Hugging Face Transformers. They implement embeddings, vector databases, FAISS, prompt engineering, and model fine-tuning for AI applications. They develop and deploy AI services using FastAPI, REST APIs, Docker, and cloud platforms. They integrate and optimize AI systems using MCP, Ollama, MLOps, CI/CD, and model evaluation techniques


##### Instruction to run

python -m uvicorn main:app --reload

streamlit run .\frontend\streamlit_app.py

python app\nlp\preprocessing.py

Screenshots: 
<img width="1885" height="880" alt="image" src="https://github.com/user-attachments/assets/de57d879-e1ac-455d-bbd9-0f59d8e16134" />
<img width="1865" height="855" alt="image" src="https://github.com/user-attachments/assets/f3bc843b-cc82-4fa9-a141-4f67f9f66f1d" />
<img width="1885" height="807" alt="image" src="https://github.com/user-attachments/assets/9bfa3bfd-8382-4a2b-a7c2-c6467d270412" />
<img width="1866" height="832" alt="image" src="https://github.com/user-attachments/assets/179bf926-8caa-48ad-ae68-eb74a9e0ef54" />
<img width="1877" height="860" alt="4" src="https://github.com/user-attachments/assets/b5a5efa2-bbe8-4910-bb32-606f18efc44b" />





