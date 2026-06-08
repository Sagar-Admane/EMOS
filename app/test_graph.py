from .graph.graph_service import GraphService

graph = GraphService()

graph.create_repository(
    repo_id=1,
    name="EMOS"
)

graph.create_file(
    file_id=1,
    path="app/main.py",
    extension="py"
)

graph.connect_repository_to_file(
    repo_id=1,
    file_id=1
)