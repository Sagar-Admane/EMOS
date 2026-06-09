from app.graph.neo4j_client import Neo4JClient

class GraphRepository:

    def __init__(self):
        self.neo4j = Neo4JClient()

    def create_repository_node(self, repo_id: int, name: str):
        query = """
MERGE (r:Repository {
    repo_id: $repo_id
})
SET r.name = $name
"""
        self.neo4j.execute_query(
            query,
            {
                "repo_id": repo_id,
                "name": name
            }
        )

    def create_file_node(self, file_id: int, path: str, extension: str):

        query = """
MERGE(f:File {
    file_id: $file_id
})

SET f.path = $path,
f.extension = $extension
"""
        
        self.neo4j.execute_query(
            query,
            {
                "file_id": file_id,
                "path": path,
                "extension": extension
            }
        )

    def create_repository_file_relationship(self, repo_id: int, file_id: int):
        query = """
MATCH(r:Repository {repo_id: $repo_id})
MATCH(f:File {file_id: $file_id})
CREATE (r)-[:CONTAINS]->(f)
"""
        
        self.neo4j.execute_query(
            query,
            {
                "repo_id": repo_id,
                "file_id": file_id
            }
        )

    def create_engineer_nodes(self, github_user_id: str, username: str):

        query = """
MERGE(e:Engineer {
github_user_id: $github_user_id
},
SET e.username= $username)
"""

        self.neo4j.execute_query(
            query,
            {
                "github_user_id": github_user_id,
                "username": username
            }
        )
    
    def create_modified_relations(self, github_user_id, file_id):
        query = """
MATCH(e:Engineer {
github_user_id: $github_user_id
})
MATCH(f:Fil {
file_id: $file_id
})
CREATE (e)-[:MODIFIED]->(f)
"""

        self.neo4j.execute_query(
            query,
            {
                "github_user_id": github_user_id,
                "file_id": file_id
            }
        )