"""
Read-only Cypher query strings for the AI Neo4j retrieval layer.
All queries are matches scoped to a specific repository ID.
"""

FIND_PR_REVIEWERS = """
MATCH (e:Engineer)-[:REVIEWS]->(p:PullRequest {number: $pr_number})
RETURN e.username AS reviewer, p.title AS pr_title, p.state AS pr_state, p.number AS pr_number
"""

FIND_ALL_PR_REVIEWS_FOR_REPO = """
MATCH (e:Engineer)-[:REVIEWS]->(p:PullRequest)
RETURN e.username AS reviewer, p.title AS pr_title, p.number AS pr_number, p.state AS pr_state
ORDER BY p.number DESC
LIMIT $limit
"""

# ── Scoped to Repository ──────────────────────────────────────────

FIND_FILE_OWNERS = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (e:Engineer)-[:OWNS]->(f)
WHERE f.path CONTAINS $path_fragment
RETURN e.username AS owner, f.path AS file_path, f.extension AS extension
"""

FIND_MOST_ACTIVE_ENGINEERS_ON_FILE = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (e:Engineer)-[:MODIFIED]->(f)
WHERE f.path CONTAINS $path_fragment
RETURN e.username AS engineer, count(*) AS modifications, collect(f.path)[0..5] AS files
ORDER BY modifications DESC
LIMIT $limit
"""

FIND_ENGINEER_OWNED_FILES = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (e:Engineer {username: $username})-[:OWNS]->(f)
RETURN f.path AS file_path, f.extension AS extension
"""

FIND_ENGINEER_MODIFIED_FILES = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (e:Engineer {username: $username})-[:MODIFIED]->(f)
RETURN f.path AS file_path, f.extension AS extension
ORDER BY f.path
LIMIT $limit
"""

FIND_FILE_IMPORTS = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f1:File)
MATCH (f1)-[:IMPORTS]->(f2:File)
WHERE f1.path CONTAINS $path_fragment
RETURN f1.path AS source, f2.path AS dependency
LIMIT $limit
"""

FIND_REVERSE_IMPORTS = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f2:File)
MATCH (f1:File)-[:IMPORTS]->(f2)
WHERE f2.path CONTAINS $path_fragment
RETURN f1.path AS importer, f2.path AS dependency
LIMIT $limit
"""

FIND_DATABASE_USAGES = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (f)-[:USES_DATABASE]->(d:Database)
WHERE d.database_name CONTAINS $db_name
RETURN f.path AS file_path, d.database_name AS database
"""

FIND_ALL_DATABASE_USAGES = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (f)-[:USES_DATABASE]->(d:Database)
RETURN f.path AS file_path, d.database_name AS database
ORDER BY d.database_name
"""

FIND_SERVICE_FILES = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (s:Service)-[:CONTAINS]->(f)
WHERE s.service_name CONTAINS $service_name
RETURN s.service_name AS service, f.path AS file_path
"""

FIND_ALL_SERVICES = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (s:Service)-[:CONTAINS]->(f)
RETURN s.service_name AS service, collect(f.path)[0..10] AS files, count(f) AS file_count
ORDER BY file_count DESC
"""

FIND_FUNCTION_CALLS = """
MATCH (caller:Function)-[:CALLS]->(callee:Function)
WHERE caller.file_id = $file_id
RETURN caller.function_name AS caller, callee.function_name AS callee
LIMIT $limit
"""

FIND_API_ENDPOINTS = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (a:API)-[:HANDLED_BY]->(f)
RETURN a.path AS endpoint, a.method AS method, f.path AS handler_file
ORDER BY a.path
LIMIT $limit
"""

FIND_ENGINEER_PR_ACTIVITY = """
MATCH (e:Engineer {username: $username})-[r]->(p:PullRequest)
RETURN e.username AS engineer, type(r) AS relationship, p.title AS pr_title, p.number AS pr_number
ORDER BY p.number DESC
LIMIT $limit
"""

FIND_ALL_ENGINEERS = """
MATCH (r:Repository {repo_id: $repo_id})-[:CONTAINS]->(f:File)
MATCH (e:Engineer)-[:OWNS|MODIFIED]->(f)
RETURN DISTINCT e.username AS username
ORDER BY e.username
"""
