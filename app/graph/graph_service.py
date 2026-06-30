from app.graph.graph_repository import GraphRepository

class GraphService:

    def __init__(self):
        self.graph_repository = GraphRepository()

    def create_repository(
        self,
        repo_id: int,
        name: str
    ):
        self.graph_repository.create_repository_node(
            repo_id,
            name
        )

    def create_file(self, file_id, path, extension):
        self.graph_repository.create_file_node(file_id, path, extension)

    def connect_repository_to_file(self, repo_id, file_id):
        self.graph_repository.create_repository_file_relationship(repo_id, file_id)


from app.db.session import SessionLocal
service = GraphService()
db = SessionLocal()

from app.models.file import File

files = db.query(File).all()

for file in files:
    service.connect_repository_to_file(1, file.id)
    