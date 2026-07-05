from app.ai.router.enums import DataSoruce, Intent
from app.ai.router.rules import INTENT_RULES


class DataSourceSelector:

    def select(self, intent: Intent, question: str | None = None) -> list[DataSoruce]:
        if not isinstance(intent, Intent):
            intent = Intent(str(intent))

        config = INTENT_RULES.get(intent, {})
        sources = config.get("sources") or config.get("soruces") or config.get("source") or []

        if isinstance(sources, (str, DataSoruce)):
            sources = [sources]

        return [DataSoruce(source) for source in sources] if sources else [DataSoruce.POSTGRES]