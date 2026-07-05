from app.ai.router.classifier import IntentClassifier
from app.ai.router.entities import EntityExtractor
from app.ai.router.router_service import RouterService
from app.ai.router.enums import Intent, Skill, DataSource


def test_intent_classifier_detects_review_and_ownership_questions():
    classifier = IntentClassifier()

    assert classifier.classify("Who reviewed this PR?") == Intent.REVIEW_HISTORY
    assert classifier.classify("Who owns the payment service?") == Intent.OWNERSHIP


def test_entity_extractor_extracts_basic_entities():
    extractor = EntityExtractor()
    entities = extractor.extract("Show me the architecture for repo demo in file app/main.py")

    assert any(entity.value == "demo" for entity in entities)
    assert any(entity.value == "app/main.py" for entity in entities)


def test_router_service_builds_a_complete_route_decision():
    service = RouterService()
    decision = service.route("Who owns the payment service in repo demo?")

    assert decision.intent == Intent.OWNERSHIP
    assert decision.skill == Skill.OWNERSHIP
    assert DataSource.POSTGRES in decision.required_sources
    assert decision.filters.repository == "demo"
