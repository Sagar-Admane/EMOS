from app.graph.graph_repository import GraphRepository
from sqlalchemy.orm import Session
from app.models.pull_request import PullRequest
from app.services.github_service import GithubService
from app.core.config import settings

class GraphPrEngineerRelation:
    def __init__(self):
        self.graph_repo = GraphRepository()
    

    def ingest_files(self, db: Session):
        token = settings.github_token
        github_service = GithubService(token)
        prs = db.query(PullRequest).all()

        for pr in prs:
            user_id = github_service.get_user(pr.author).id
            self.graph_repo.create_engineer_nodes(user_id, pr.author)
            self.graph_repo.create_pr_node(pr.title, pr.id, pr.github_pr_id, pr.state)

            self.graph_repo.create_engineer_pr_relation(pr.id, pr.author)

