import re

SKILL_PATTERNS = {
    "python_score": [r"\bpython\b", r"\bdjango\b", r"\bflask\b", r"\bfastapi\b", r"\bpandas\b", r"\bnumpy\b"],
    "java_score": [r"\bjava\b", r"\bspring\b", r"\bhibernate\b"],
    "sql_score": [r"\bsql\b", r"\bpostgres\b", r"\bmysql\b", r"\boracle\b", r"\bdatabase\b"],
    "dsa_score": [r"\bdsa\b", r"\balgorithms\b", r"\bleetcode\b", r"\bdata structures\b"],
    "cloud_score": [r"\baws\b", r"\bazure\b", r"\bgcp\b", r"\bdocker\b", r"\bkubernetes\b", r"\bdevops\b"],
    "web_score": [r"\breact\b", r"\bnode\b", r"\bhtml\b", r"\bcss\b", r"\bjavascript\b", r"\btypescript\b"],
    "ml_score": [r"\bmachine learning\b", r"\bdeep learning\b", r"\bopencv\b", r"\bcnn\b", r"\btensorflow\b", r"\bpytorch\b"],
    "cybersecurity_score": [r"\bcybersecurity\b", r"\bpenetration testing\b", r"\bethical hacking\b", r"\bnetwork security\b"]
}

def extract_resume_skills(text: str) -> dict:
    text_lower = text.lower()
    extracted_skills = []

    for skill_key, patterns in SKILL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                extracted_skills.append({
                    "skill": skill_key.replace("_score", "").upper(),
                    "matched_keyword": pat.replace(r"\b", "")
                })
                break

    # Estimate complexity based on text depth & keyword count
    keyword_count = len(extracted_skills)
    if keyword_count >= 5 or "deep learning" in text_lower or "kubernetes" in text_lower or "system architecture" in text_lower:
        complexity = 3 # Advanced
        complexity_label = "Advanced"
    elif keyword_count >= 2:
        complexity = 2 # Intermediate
        complexity_label = "Intermediate"
    else:
        complexity = 1 # Basic
        complexity_label = "Basic"

    return {
        "extracted_skills": extracted_skills,
        "skill_count": keyword_count,
        "estimated_complexity_level": complexity,
        "complexity_label": complexity_label,
        "data_provenance": "DERIVED"
    }
