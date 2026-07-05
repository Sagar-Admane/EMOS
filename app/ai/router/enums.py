from enum import Enum

class Intent(str, Enum):
    REPOSITORY_SUMMARY = "repository_summary"
    ARCHITECTURE = "architecture"
    CODE_SEARCH = "code_search"
    OWNERSHIP = "ownership"
    PR_ANALYSIS = "pr_analysis"
    REVIEW_HISTORY = "review_history"
    COMMIT_HISTORY = "commit_history"
    DEPENDENCY = "dependency"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    METRICS = "metrics"
    DECISION_RECALL = "decision_recall"
    MIXED = "mixed"

class DataSoruce(str, Enum):
    POSTGRES = "postgres"
    NEO4J = "neo4j"
    QDRANT = "qdrant"

class Skill(str, Enum):
    REPOSITORY_SUMMARY = "repository_summary"
    ARCHITECTURE = "architecture"
    OWNERSHIP = "ownership"
    REVIEWER = "reviewer"
    DEPENDENCY = "dependency"
    DEPLOYMENT = "deployment"
    DECISION_RECALL = "decision_recall"

class RetrievalStrategy(str, Enum):
    SQL = "sql"
    GRAPH = "graph"
    VECTOR = "vector"
    HYBRID = "hybrid"