from .enums import *

INTENT_RULES = {
    Intent.ARCHITECTURE: {
        "sources": [
            DataSource.QDRANT,
            DataSource.NEO4J,
        ],
        "skill": Skill.ARCHITECTURE,
        "strategy": RetrievalStrategy.HYBRID,
    },
    Intent.CODE_SEARCH: {
        "sources": [DataSource.QDRANT],
        "skill": Skill.CODE_SEARCH,
        "strategy": RetrievalStrategy.VECTOR,
    },
    Intent.OWNERSHIP: {
        "sources": [
            DataSource.POSTGRES,
            DataSource.NEO4J,
        ],
        "skill": Skill.OWNERSHIP,
        "strategy": RetrievalStrategy.GRAPH,
    },
    Intent.REVIEW_HISTORY: {
        "sources": [DataSource.POSTGRES],
        "skill": Skill.REVIEWER,
        "strategy": RetrievalStrategy.SQL,
    },
    Intent.REPOSITORY_SUMMARY: {
        "sources": [
            DataSource.POSTGRES,
            DataSource.QDRANT,
        ],
        "skill": Skill.REPOSITORY_SUMMARY,
        "strategy": RetrievalStrategy.HYBRID,
    },
}

INTENT_RULEA = INTENT_RULES