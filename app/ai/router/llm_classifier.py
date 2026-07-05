from app.ai.router.classifier import IntentClassifier
from app.ai.router.enums import Intent


class LLMIntentClassifier:

    def __init__(self, fallback_classifier: IntentClassifier | None = None):
        self.fallback_classifier = fallback_classifier or IntentClassifier()

    def classify(self, question: str) -> Intent:
        if not question or not str(question).strip():
            return Intent.MIXED

        return self.fallback_classifier.classify(question)