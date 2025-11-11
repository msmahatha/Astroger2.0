

def get_category(question: str) -> str:
    # fallback for classification if API fails
    categories = {
        "career": ["job", "work", "promotion"],
        "health": ["health", "illness", "pain"],
        "marriage": ["marriage", "wed", "spouse"],
        "finance": ["money", "finance", "loan", "wealth"],
        "education": ["study", "exam", "college"],
        "relationships": ["love", "relationship"],
        "travel": ["travel", "journey", "abroad"],
        "spirituality": ["spiritual", "karma", "meditation"],
        "property": ["house", "property", "land"],
        "legal": ["legal", "court", "case"],
    }
    q = question.lower()
    for cat, kws in categories.items():
        if any(k in q for k in kws):
            return cat.title()
    return "General"
