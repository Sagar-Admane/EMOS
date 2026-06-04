from fastapi import FastAPI
from app.core.config import settings
from app.services.github_service import GithubService
from app.db.session import SessionLocal

from app.services.repository_ingestion_service import RepositoryIngestion
from app.services.commit_ingestion import CommitIngestionService
from app.services.pull_request_ingestion_service import PullRequestIngestionService
from app.services.branch_ingestion_service import BranchIngestionService
from app.services.contributor_ingestion_service import ContributorIngestionService
from app.services.file_ingestion_service import FileIngestionService
from app.services.commit_file_ingestion import CommitFileIngestion
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService

from app.router.repository_summary import router as summary_router
from app.router.contributor_analytics import router as contributor_router
from app.router.file_analytics import router as hotspot_router
from app.router.repository_activity_analytics_router import router as repo_activity_router
from app.router.file_ownership_analytics import router as file_ownership_router
from app.router.code_file_ingest_router import router as code_file_ingest_router
from app.router.code_chunk_router import router as code_chunk_router
from app.router.generate_embedding_router import router as generate_embedding_router

app = FastAPI(
    title="EMOS",
    version="1.0"
)

db = SessionLocal()

@app.get("/")
def root():

    token = settings.github_token
    github_service = GithubService(token)
    # commit_service = CommitIngestionService(github_service)
    # count = commit_service.ingest_commits(db, "fastapi/fastapi", 1, 20)
    # service = RepositoryIngestion(github_service)
    # repo = service.ingest_repository(db, "fastapi/fastapi")

    # print(repo.id)
    # print(repo.full_name)

    service = PullRequestIngestionService(github_service)

    count = service.ingest_pull_requests(db, "fastapi/fastapi", 1, 50)

    return {
        "prs_ingested": count
    }

@app.get("/ingest-branch")
def branch_ingest():
    token = settings.github_token
    github_service = GithubService(token)
    service = BranchIngestionService(github_service)
    count = service.ingest_branches(db, "fastapi/fastapi", 1)
    return {
        "branches": count
    }

@app.get("/ingest-contributor")
def contributor_ingest():
    token = settings.github_token
    github_service = GithubService(token)
    service = ContributorIngestionService(github_service)
    count = service.contributor_ingestion(db, "fastapi/fastapi", 1)
    return count

@app.get("/ingest-file")
def file_ingest():
    token = settings.github_token
    github_service = GithubService(token)
    service = FileIngestionService(github_service)
    count = service.file_ingestion(db, "fastapi/fastapi", 1)
    return count

@app.get("/ingest-commitFile")
def commit_file_ingest():
    token = settings.github_token
    github_service = GithubService(token)
    service = CommitFileIngestion(github_service)
    relations = service.commit_file_ingestion(db, "fastapi/fastapi", 1)
    return relations


app.include_router(summary_router)
app.include_router(contributor_router)
app.include_router(hotspot_router)
app.include_router(repo_activity_router)
app.include_router(file_ownership_router)
app.include_router(code_file_ingest_router)
app.include_router(code_chunk_router)
app.include_router(generate_embedding_router)

@app.get("/qdrant/init")

def init_qdrant():

    service = QdrantService()

    service.create_collection()

    return {
        "message": "collection_recieved"
    }