from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_match_score(candidate_skills: list[str], job_skills: list[str]) -> float:
    """Returns a 0–100 match score using TF-IDF cosine similarity."""
    if not candidate_skills or not job_skills:
        return 0.0

    candidate_text = " ".join(candidate_skills)
    job_text = " ".join(job_skills)

    vectorizer = TfidfVectorizer()
    try:
        tfidf = vectorizer.fit_transform([candidate_text, job_text])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception:
        return 0.0
