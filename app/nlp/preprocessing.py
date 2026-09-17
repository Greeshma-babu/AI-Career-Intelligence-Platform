import pdfplumber
import unicodedata

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ============================================================
# NLP SETUP
# ============================================================

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


# ============================================================
# TEXT PREPROCESSING
# ============================================================


def preprocess_text(text):
    """
    Clean and preprocess extracted text.

    Steps:
    1. Unicode normalization
    2. Remove unwanted characters
    3. Lowercase
    4. Tokenization
    5. Stopword removal
    6. Lemmatization
    7. Convert tokens back to text
    """

    # 1. Unicode normalization
    text = unicodedata.normalize("NFKD", text)

    # 2. Basic text cleaning
    text = text.replace("-", " ").replace("\n", " ").replace("(", " ").replace(")", " ")

    # Remove extra spaces
    text = " ".join(text.split())

    # 3. Lowercase
    text = text.lower()

    # 4. Tokenization
    tokens = word_tokenize(text)

    # 5. Stopword removal
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]

    # 6. Lemmatization
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # 7. Convert tokens back to text
    return " ".join(tokens)


# ============================================================
# PDF EXTRACTION
# ============================================================


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file and preprocess it.
    """

    text = ""

    # Read PDF
    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    # Preprocess extracted text
    text = preprocess_text(text)

    return text


# ============================================================
# TXT EXTRACTION
# ============================================================


def extract_text_from_job_description(file_path):
    """
    Read a TXT job description and preprocess it.
    """

    # Read TXT file
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Preprocess extracted text
    text = preprocess_text(text)

    return text


# ============================================================
# DOCX EXTRACTION
# ============================================================


def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX resume and preprocess it.
    """

    document = Document(file_path)

    text_parts = []

    # --------------------------------------------------------
    # Paragraphs
    # --------------------------------------------------------

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text_parts.append(paragraph.text)

    # --------------------------------------------------------
    # Tables
    # --------------------------------------------------------

    for table in document.tables:

        for row in table.rows:

            for cell in row.cells:

                if cell.text.strip():

                    text_parts.append(cell.text)

    # --------------------------------------------------------
    # Combine text
    # --------------------------------------------------------

    text = "\n".join(text_parts)

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    text = preprocess_text(text)

    return text


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    resume_path = "data/resume/uploaded_resume.pdf"
    job_description_path = "data/job/description.txt"

    # Extract resume
    extracted_pdf_text = extract_text_from_pdf(resume_path)

    # Extract job description
    extracted_job_text = extract_text_from_job_description(job_description_path)

    print("\n================ RESUME TEXT ================\n")
    print(extracted_pdf_text)

    print("\n================ JOB DESCRIPTION ================\n")
    print(extracted_job_text)
