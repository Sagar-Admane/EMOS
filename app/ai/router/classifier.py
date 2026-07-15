from app.ai.router.enums import Intent

class IntentClassifier:

    def classify(self, question: str):
        question = question.lower()

        if "who reviewed" in question:
            return Intent.REVIEW_HISTORY

        if "who owns" in question:
            return Intent.OWNERSHIP

        if "architecture" in question or "system design" in question:
            return Intent.ARCHITECTURE
            
        if any(kw in question for kw in ["where is", "written", "file", "implementation", "implemented", "database", "auth"]):
            return Intent.CODE_SEARCH
            
        return Intent.MIXED
    
    