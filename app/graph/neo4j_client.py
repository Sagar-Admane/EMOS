from app.core.config import settings
from neo4j import GraphDatabase


class Neo4JClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(
                settings.neo4j_username,
                settings.neo4j_password
            )
        )

    def execute_query(self, query: str, parameters: dict | None = None):
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    parameters or {}
                )

                return list(result)
        except Exception as exe:
            return list(exe)
        
    def close(self):
        self.driver.close()