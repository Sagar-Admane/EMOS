from .enums import *

INTENT_RULES = {
    Intent.ARCHITECTURE: {
        "sources": [
            DataSoruce.QDRANT,
            DataSoruce.NEO4J,
        ],
        "skill": Skill.ARCHITECTURE,
        "strategy": RetrievalStrategy.HYBRID,
    },
    Intent.OWNERSHIP: {
        "sources": [
            DataSoruce.POSTGRES,
            DataSoruce.NEO4J,
        ],
        "skill": Skill.OWNERSHIP,
        "strategy": RetrievalStrategy.GRAPH,
    },
    Intent.REVIEW_HISTORY: {
        "sources": [DataSoruce.POSTGRES],
        "skill": Skill.REVIEWER,
        "strategy": RetrievalStrategy.SQL,
    },
    Intent.REPOSITORY_SUMMARY: {
        "sources": [DataSoruce.QDRANT],
        "skill": Skill.REPOSITORY_SUMMARY,
        "strategy": RetrievalStrategy.VECTOR,
    },
}

INTENT_RULEA = INTENT_RULES