from app.ai.router.enums import Intent

class IntentClassifier:

    def classify(self, question: str):
        question = question.lower()

        if "who reviewed" in question:
            return Intent.REVIEW_HISTORY

        if "who owns" in question:
            return Intent.OWNERSHIP

        if "architecture" in question:
            return Intent.ARCHITECTURE
        return Intent.MIXED
    
    