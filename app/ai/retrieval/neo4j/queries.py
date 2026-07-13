"""
Read-only Cypher query strings for the AI Neo4j retrieval layer.

All queries are MATCH-only (never MERGE, CREATE, or SET).
Parameters are passed separately to prevent injection.
"""

# ------------------------------------------------------------------ #
# PR Reviewer Queries
# ------------------------------------------------------------------ #

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

# ------------------------------------------------------------------ #
# Ownership Queries
# ------------------------------------------------------------------ #

FIND_FILE_OWNERS = """
MATCH (e:Engineer)-[:OWNS]->(f:File)
WHERE f.path CONTAINS $path_fragment
RETURN e.username AS owner, f.path AS file_path, f.extension AS extension
"""

FIND_MOST_ACTIVE_ENGINEERS_ON_FILE = """
MATCH (e:Engineer)-[:MODIFIED]->(f:File)
WHERE f.path CONTAINS $path_fragment
RETURN e.username AS engineer, count(*) AS modifications, collect(f.path)[0..5] AS files
ORDER BY modifications DESC
LIMIT $limit
"""

FIND_ENGINEER_OWNED_FILES = """
MATCH (e:Engineer {username: $username})-[:OWNS]->(f:File)
RETURN f.path AS file_path, f.extension AS extension
"""

FIND_ENGINEER_MODIFIED_FILES = """
MATCH (e:Engineer {username: $username})-[:MODIFIED]->(f:File)
RETURN f.path AS file_path, f.extension AS extension
ORDER BY f.path
LIMIT $limit
"""

# ------------------------------------------------------------------ #
# Dependency / Architecture Queries
# ------------------------------------------------------------------ #

FIND_FILE_IMPORTS = """
MATCH (f1:File)-[:IMPORTS]->(f2:File)
WHERE f1.path CONTAINS $path_fragment
RETURN f1.path AS source, f2.path AS dependency
LIMIT $limit
"""

FIND_REVERSE_IMPORTS = """
MATCH (f1:File)-[:IMPORTS]->(f2:File)
WHERE f2.path CONTAINS $path_fragment
RETURN f1.path AS importer, f2.path AS dependency
LIMIT $limit
"""

FIND_DATABASE_USAGES = """
MATCH (f:File)-[:USES_DATABASE]->(d:Database)
WHERE d.database_name CONTAINS $db_name
RETURN f.path AS file_path, d.database_name AS database
"""

FIND_ALL_DATABASE_USAGES = """
MATCH (f:File)-[:USES_DATABASE]->(d:Database)
RETURN f.path AS file_path, d.database_name AS database
ORDER BY d.database_name
"""

FIND_SERVICE_FILES = """
MATCH (s:Service)-[:CONTAINS]->(f:File)
WHERE s.service_name CONTAINS $service_name
RETURN s.service_name AS service, f.path AS file_path
"""

FIND_ALL_SERVICES = """
MATCH (s:Service)-[:CONTAINS]->(f:File)
RETURN s.service_name AS service, collect(f.path)[0..10] AS files, count(f) AS file_count
ORDER BY file_count DESC
"""

# ------------------------------------------------------------------ #
# Architecture / Function Call Graph
# ------------------------------------------------------------------ #

FIND_FUNCTION_CALLS = """
MATCH (caller:Function)-[:CALLS]->(callee:Function)
WHERE caller.file_id = $file_id
RETURN caller.function_name AS caller, callee.function_name AS callee
LIMIT $limit
"""

FIND_API_ENDPOINTS = """
MATCH (a:API)-[:HANDLED_BY]->(f:File)
RETURN a.path AS endpoint, a.method AS method, f.path AS handler_file
ORDER BY a.path
LIMIT $limit
"""

# ------------------------------------------------------------------ #
# Engineer Overview
# ------------------------------------------------------------------ #

FIND_ENGINEER_PR_ACTIVITY = """
MATCH (e:Engineer {username: $username})-[r]->(p:PullRequest)
RETURN e.username AS engineer, type(r) AS relationship, p.title AS pr_title, p.number AS pr_number
ORDER BY p.number DESC
LIMIT $limit
"""

FIND_ALL_ENGINEERS = """
MATCH (e:Engineer)
RETURN e.username AS username, e.github_user_id AS github_user_id
ORDER BY e.username
"""
