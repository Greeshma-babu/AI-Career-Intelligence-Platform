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
