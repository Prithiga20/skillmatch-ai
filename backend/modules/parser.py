import re
import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from docx import Document

# Curated skill keywords for extraction
SKILL_KEYWORDS = {
    "python", "java", "javascript", "typescript", "react", "node.js", "nodejs",
    "flask", "django", "sql", "mysql", "mongodb", "postgresql", "html", "css",
    "machine learning", "deep learning", "nlp", "data analysis", "tensorflow",
    "pytorch", "scikit-learn", "aws", "azure", "docker", "kubernetes", "git",
    "rest api", "graphql", "c++", "c#", "php", "ruby", "swift", "kotlin",
    "excel", "power bi", "tableau", "communication", "leadership", "teamwork",
    "problem solving", "agile", "scrum", "linux", "devops", "ci/cd",
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    output = io.StringIO()
    extract_text_to_fp(io.BytesIO(file_bytes), output, laparams=LAParams())
    return output.getvalue()


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = [skill for skill in SKILL_KEYWORDS if skill in text_lower]
    return sorted(set(found))


def extract_experience(text: str) -> str:
    pattern = r"(\d+)\s*\+?\s*years?\s*(?:of\s+)?(?:experience|exp)"
    match = re.search(pattern, text, re.IGNORECASE)
    return f"{match.group(1)} years" if match else "Not specified"


def extract_education(text: str) -> str:
    degrees = ["phd", "ph.d", "master", "msc", "mba", "bachelor", "bsc", "b.tech", "m.tech", "be", "me"]
    text_lower = text.lower()
    found = [d.upper() for d in degrees if d in text_lower]
    return ", ".join(found) if found else "Not specified"


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith((".docx", ".doc")):
        text = extract_text_from_docx(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    return {
        "raw_text": text,
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
    }
