import pdfplumber
import unicodedata

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words("english"))

lemmatizer = WordNetLemmatizer()


def extract_text_from_pdf(file_path):

    text = ""

    # 1. Read PDF
    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    # 2. Unicode normalization
    text = (
        unicodedata.normalize("NFKD", text)
        .replace("-", "")
        .replace("\n", " ")
        .replace("(", " ")
        .replace(")", " ")
    )

    # 3. Lowercase
    text = text.lower()

    # 4. Tokenization
    tokens = word_tokenize(text)

    # 5. Stopword removal
    tokens = [word for word in tokens if word not in stop_words]

    # 6. Lemmatization
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # 7. Convert tokens back to text
    text = " ".join(tokens)

    return text


extracted_pdf_text = extract_text_from_pdf("data/resume/uploaded_resume.pdf")

print("Extracted text from PDF:")
print(extracted_pdf_text)
