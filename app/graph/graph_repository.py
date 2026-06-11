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
MERGE (r)-[:CONTAINS]->(f)
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
})
SET e.username= $username
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
MATCH(f:File {
file_id: $file_id
})
MERGE (e)-[:MODIFIED]->(f)
"""

        self.neo4j.execute_query(
            query,
            {
                "github_user_id": github_user_id,
                "file_id": file_id
            }
        )
    
    def create_function_node(self, file_id: int, function_name: str):
        query = """
MERGE(f:Function {
function_name: $function_name,
file_id: $file_id
})
"""

        try:
            result = self.neo4j.execute_query(
                query,
                {
                    "file_id": file_id,
                    "function_name": function_name
                }
            )

            print("Result of creating a node is : ",result)
        except Exception as exc:
            print(exc)


    def file_to_function_relation(self, file_id: int, function_name: str):
        query = """
MATCH(f:File {file_id: $file_id})
MATCH(fun:Function {function_name: $function_name, file_id: $file_id})
MERGE (f)-[:CONTAINS]->(fun)
""" 

        self.neo4j.execute_query(
            query,
            {
                "file_id": file_id,
                "function_name": function_name
            }
        )

    def create_function_call_relation(self, caller_name: str, callee_name: str, file_id : int):
        query = """
MATCH(caller:Function {
function_name: $caller_name,
file_id: $file_id
})
MATCH(callee:Function {
function_name: $callee_name,
file_id: $file_id
})
MERGE(caller)-[:CALLS]->(callee)
"""
        self.neo4j.execute_query(
            query,
            {
                "file_id": file_id,
                "caller_name": caller_name,
                "callee_name": callee_name
            }
        )

        print("Caller is calling the function and is saved in neo4j")

    def create_file_import_relationship(self, source_file_id: str, dest_file_id: str):

        print("Source file id: ",source_file_id)
        print("Dest file id",dest_file_id)
        query= """
MATCH(f1:File {file_id: $source_file_id})
MATCH(f2:File {file_id: $dest_file_id})
MERGE(f1)-[:IMPORTS]->(f2)
        """
        try:
            self.neo4j.execute_query(
                query,
                {
                    "source_file_id": source_file_id,
                    "dest_file_id": dest_file_id
                }
            )
        except Exception as exc:
            print("Exception occured: ",exc)

    def create_owns_relation(self, file_id: int, github_user_id: int):
        try:
            
            query = """
MATCH(e:Engineer {github_user_id: $github_user_id})
MATCH(f:File {file_id:$file_id})
MERGE (e)-[:OWNS]->(f)
"""
            print(type(github_user_id))
            print(type(file_id))

            print(github_user_id)
            print(file_id)
            

            result = self.neo4j.execute_query(
                query,
                {
                    "github_user_id": github_user_id,
                    "file_id": file_id
                }
            )

            print("OWNS CREATED", result)
        except Exception as e:
            print("ERROR:", e)


    def create_database_node(self, database_name: str):

        query = """
MERGE (d:Database {database_name: $database_name})
"""

        self.neo4j.execute_query(
            query,
            {
                "database_name": database_name
            }
        )

    def create_file_database_relation(self, file_id: int, database_name: str):
        query = """
MATCH(d:Database {database_name: $database_name})
MATCH(f:File {file_id: $file_id})
MERGE (f)-[:USES_DATABASE]->(d)
"""
        self.neo4j.execute_query(
            query,
            {
                "file_id": file_id,
                "database_name": database_name
            }
        )

    def create_api_node(self, path:str, method: str):
        query = """
MERGE(a:API {path: $path, method: $method})
"""

        self.neo4j.execute_query(query,{
            "path": path,
            "method": method
        })

    def create_api_funtion_relation(self, path: str, method: str, file_id: int, file_path: str):
        query = """
MATCH(a:API {path: $path, method: $method})
MATCH(f:File {file_id: $file_id, path: $file_path})
MERGE (a)-[:HANDLED_BY]->(f)
"""

        print("Before executing node")

        self.neo4j.execute_query(
            query,
            {
                "path": path,
                "method": method,
                "file_id": file_id,
                "file_path": file_path
            }
        )

        print("After executing relation", file_id, file_path)

    
    def create_class_node(self, class_name: str, file_id: int):
        query = """
MERGE(c:Class {class_name: $class_name, file_id: $file_id})
"""

        self.neo4j.execute_query(
            query,
            {
                "class_name": class_name,
                "file_id": file_id
            }
        )

    def file_class_relation(self, class_name: str, file_id: int):
        query = """
MATCH(f:File {file_id: $file_id})
MATCH(c:Class {class_name: $class_name, file_id: $file_id})
MERGE (f)-[:CONTAINS]->(c)
"""
        self.neo4j.execute_query(
            query,
            {
                "class_name": class_name,
                "file_id": file_id
            }
        )

    def create_service_node(self, service_name:str):
        query = """
MERGE (s:Service {service_name: $service_name})
"""

        self.neo4j.execute_query(
            query,
            {
                "service_name": service_name
            }
        )

    
    def create_service_file_relation(self, service_name: str, file_id: int):
        query = """
MATCH (s:Service {service_name: $service_name})
MATCH (f:File {file_id: $file_id})
MERGE (s)-[:CONTAINS]->(f)
"""
        self.neo4j.execute_query(
            query,
            {
                "service_name": service_name,
                "file_id": file_id
            }
        )
    
    def create_pr_node(self, title: str, pr_id: int, number: int, state: str):
        query = """
MERGE(p:PullRequest {
pr_id: $pr_id
})
SET p.title = $title,
p.number = $number,
p.state = $state
"""

        self.neo4j.execute_query(
            query,
            {
                "title":title,
                "pr_id": pr_id,
                "number": number,
                "state": state
            }
        )

    
    def create_engineer_pr_relation(self, pr_id: int, username: str):
        query = """
MATCH(e:Engineer {username: $username})
MATCH(p:PullRequest {pr_id: $pr_id})
MERGE(e)-[:CREATED]->(p)
"""

        self.neo4j.execute_query(
            query,
            {
                "pr_id": pr_id,
                "username": username
            }
        )