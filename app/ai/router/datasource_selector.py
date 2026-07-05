from app.ai.router.enums import DataSource, Intent
from app.ai.router.rules import INTENT_RULES


class DataSourceSelector:

    def select(self, intent: Intent, question: str | None = None) -> list[DataSource]:
        if not isinstance(intent, Intent):
            intent = Intent(str(intent))

        config = INTENT_RULES.get(intent, {})
        sources = config.get("sources") or config.get("soruces") or config.get("source") or []

        if isinstance(sources, (str, DataSource)):
            sources = [sources]

        return [DataSource(source) for source in sources] if sources else [DataSource.POSTGRES]