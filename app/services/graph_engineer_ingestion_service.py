from app.graph.graph_repository import GraphRepository

from app.models.contributor import Contributor
from app.models.commit import Commit
from app.models.commitFile import CommitFile

from sqlalchemy.orm import Session

class GraphEngineerIngestionService:

    def __init__(self):
        self.graph_repository = GraphRepository()

    def engineer_ingest(self, db: Session, repo_id: int):
        contributors = db.query(Contributor).all()

        for contributor in contributors:
            self.graph_repository.create_engineer_nodes(contributor.github_user_id, contributor.username)

            commits = db.query(Commit).filter(Commit.repo_id == repo_id).all()

            for commit in commits:

                commit_files = db.query(CommitFile).filter(CommitFile.commit_id == commit.id).all()

                for commit_file in commit_files:
                    self.graph_repository.create_modified_relations(contributor.github_user_id, commit_file.file_id)
                    self.graph_repository.create_owns_relation(commit_file.file_id, contributor.github_user_id)
