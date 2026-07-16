from app.graph.graph_repository import GraphRepository

from sqlalchemy.orm import Session

from app.models.repository import Repository
class GraphRepoIngestion:

    def __init__(self):
        self.graph_repo = GraphRepository()

    def ingest_repos(self, db: Session):
        repos = db.query(Repository).all()

        for repo in repos:
            self.graph_repo.create_repository_node(repo.id, repo.full_name)

