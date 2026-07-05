from app.ai.router.classifier import IntentClassifier
from app.ai.router.datasource_selector import DataSourceSelector
from app.ai.router.entities import EntityExtractor
from app.ai.router.enums import DataSoruce, Intent, RetrievalStrategy, Skill
from app.ai.router.schemas import QueryFilters, RouteDecision
from app.ai.router.skill_selector import SkillSelector
from app.ai.router.utils import infer_filters


class RouterService:

    def __init__(
        self,
        intent_classifier: IntentClassifier | None = None,
        entity_extractor: EntityExtractor | None = None,
        datasource_selector: DataSourceSelector | None = None,
        skill_selector: SkillSelector | None = None,
    ):
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.datasource_selector = datasource_selector or DataSourceSelector()
        self.skill_selector = skill_selector or SkillSelector()

    def route(self, question: str) -> RouteDecision:
        intent = self.intent_classifier.classify(question)
        entities = self.entity_extractor.extract(question)
        required_sources = self.datasource_selector.select(intent, question)
        skill = self.skill_selector.select(intent, question)
        strategy = self._select_strategy(intent, required_sources)
        filters = QueryFilters(**infer_filters(question))
        reasoning = self._build_reasoning(intent, skill, required_sources, strategy)

        return RouteDecision(
            question=question,
            intent=intent,
            confidence=self._confidence_for(intent),
            entiteis=entities,
            required_sources=required_sources,
            skill=skill,
            strategy=strategy,
            filters=filters,
            reasoning=reasoning,
        )

    def _select_strategy(self, intent: Intent, required_sources: list[DataSoruce]) -> RetrievalStrategy:
        if intent in {Intent.ARCHITECTURE, Intent.DEPENDENCY, Intent.DEPLOYMENT}:
            return RetrievalStrategy.HYBRID if len(required_sources) > 1 else RetrievalStrategy.VECTOR
        if intent == Intent.OWNERSHIP:
            return RetrievalStrategy.GRAPH
        if intent in {Intent.REVIEW_HISTORY, Intent.PR_ANALYSIS, Intent.COMMIT_HISTORY}:
            return RetrievalStrategy.SQL
        return RetrievalStrategy.HYBRID

    def _confidence_for(self, intent: Intent) -> float:
        return 0.85 if intent != Intent.MIXED else 0.55

    def _build_reasoning(self, intent: Intent, skill: Skill, sources: list[DataSoruce], strategy: RetrievalStrategy) -> str:
        return (
            f"Intent '{intent.value}' is routed to skill '{skill.value}' using sources "
            f"{', '.join(source.value for source in sources)} with strategy '{strategy.value}'."
        )