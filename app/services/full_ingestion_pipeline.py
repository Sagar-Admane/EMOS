"""
FullIngestionPipeline
=====================
Orchestrates the complete ingestion of a GitHub repository into:
  - PostgreSQL  (metadata, code content, chunks)
  - Qdrant      (per-repo vector collection)
  - Neo4j       (knowledge graph nodes + edges)

This runs as a FastAPI BackgroundTask so the HTTP request returns immediately
and the user can poll /github/repos/{repo_id}/status for progress.
"""

import traceback
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings

from app.models.connected_repo import ConnectedRepo
from app.models.file import File

# --- PostgreSQL ingestion services ---
from app.services.github_service import GithubService
from app.services.repository_ingestion_service import RepositoryIngestion
from app.services.commit_ingestion import CommitIngestionService
from app.services.branch_ingestion_service import BranchIngestionService
from app.services.contributor_ingestion_service import ContributorIngestionService
from app.services.file_ingestion_service import FileIngestionService
from app.services.commit_file_ingestion import CommitFileIngestion
from app.services.pull_request_ingestion_service import PullRequestIngestionService
from app.services.pull_request_review_service import PullRequestReviewService
from app.services.code_file_ingestion_service import CodeFileIngestionService
from app.services.code_chunk_ingestion import CodeChunkIngestion

# --- Qdrant ---
from app.services.qdrant_service import QdrantService
from app.services.embedding_ingestion_service import EmbeddingIngestionService

# --- Neo4j graph ingestion services ---
from app.services.graph_repo_ingestion import GraphRepoIngestion
from app.services.grapth_file_ingestion_service import GraphFileIngestionService
from app.services.graph_engineer_ingestion_service import GraphEngineerIngestionService
from app.services.function_graph_ingestion_service import FunctionGraphIngestionService
from app.services.call_graph_ingestion_service import CallGraphIngestionService
from app.services.import_graph_ingestion_service import ImportGraphIngestionServive
from app.services.graph_class_ingestion_service import GraphClassIngestionService
from app.services.graph_api_ingestion import GraphAPIIngestion
from app.services.graph_database_ingestion_service import GraphDatabaseIngestionService
from app.services.graph_service_ingestion_service import GraphServiceIngestionService
from app.services.graph_engineer_pr_relation import GraphPrEngineerRelation
from app.services.graph_review_relation import GraphReviewRelation


def _set_status(db: Session, repo_id: int, status: str, error: str = None):
    """Update ConnectedRepo status in a fresh DB session."""
    record = db.query(ConnectedRepo).filter(ConnectedRepo.repo_id == repo_id).first()
    if record:
        record.status = status
        record.error_message = error
        if status == "ready":
            record.indexed_at = datetime.utcnow()
        db.commit()


def run_full_ingestion(repo_id: int, repo_full_name: str, qdrant_collection: str):
    """
    Entry point called as a FastAPI BackgroundTask.
    Opens its own DB session (separate from the request session).
    """
    db: Session = SessionLocal()

    try:
        print(f"[Pipeline] Starting full ingestion for {repo_full_name} (repo_id={repo_id})")
        _set_status(db, repo_id, "indexing")

        token = settings.github_token
        github_service = GithubService(token)

        # ── Phase A: PostgreSQL metadata ingestion ──────────────────────────────
        print("[Pipeline] Phase A — PostgreSQL metadata")

        print("[Pipeline]   A1: commits")
        try:
            CommitIngestionService(github_service).ingest_commits(db, repo_full_name, repo_id, limit=999999)
        except Exception as e:
            print(f"[Pipeline]   A1 commits warning: {e}")

        print("[Pipeline]   A2: branches")
        try:
            BranchIngestionService(github_service).ingest_branches(db, repo_full_name, repo_id)
        except Exception as e:
            print(f"[Pipeline]   A2 branches warning: {e}")

        print("[Pipeline]   A3: contributors")
        try:
            ContributorIngestionService(github_service).contributor_ingestion(db, repo_full_name, repo_id)
        except Exception as e:
            print(f"[Pipeline]   A3 contributors warning: {e}")

        print("[Pipeline]   A4: files tree")
        try:
            FileIngestionService(github_service).file_ingestion(db, repo_full_name, repo_id)
        except Exception as e:
            print(f"[Pipeline]   A4 files warning: {e}")

        print("[Pipeline]   A5: commit-file relations")
        try:
            CommitFileIngestion(github_service).commit_file_ingestion(db, repo_full_name, repo_id)
        except Exception as e:
            print(f"[Pipeline]   A5 commit-files warning: {e}")

        print("[Pipeline]   A6: pull requests")
        try:
            PullRequestIngestionService(github_service).ingest_pull_requests(db, repo_full_name, repo_id, limit=999999)
        except Exception as e:
            print(f"[Pipeline]   A6 PRs warning: {e}")

        print("[Pipeline]   A7: PR reviews")
        try:
            from app.models.repository import Repository as RepoModel
            repo_record = db.query(RepoModel).filter(RepoModel.id == repo_id).first()
            github_repo_id = repo_record.github_repo_id if repo_record else None
            if github_repo_id:
                PullRequestReviewService(github_service).ingest_reviews(db, repo_id, github_repo_id)
        except Exception as e:
            print(f"[Pipeline]   A7 PR reviews warning: {e}")

        # ── Phase B: Code content + chunking ───────────────────────────────────
        print("[Pipeline] Phase B — Code content + chunking")

        print("[Pipeline]   B1: fetch file contents from GitHub")
        try:
            CodeFileIngestionService(github_service).ingest(db, repo_id, limit=999999)
        except Exception as e:
            print(f"[Pipeline]   B1 code files warning: {e}")

        print("[Pipeline]   B2: chunk code files")
        try:
            CodeChunkIngestion(github_service).ingest(db, limit=999999, chunk_size=100)
        except Exception as e:
            print(f"[Pipeline]   B2 chunking warning: {e}")

        # ── Phase C: Qdrant vector embeddings ──────────────────────────────────
        print(f"[Pipeline] Phase C — Qdrant embeddings → collection '{qdrant_collection}'")

        try:
            qdrant_service = QdrantService()
            qdrant_service.create_collection(qdrant_collection)
            EmbeddingIngestionService().generate_embedding(
                db=db,
                repo_id=repo_id,
                collection_name=qdrant_collection
            )
        except Exception as e:
            print(f"[Pipeline]   C qdrant warning: {e}")

        # ── Phase D: Neo4j knowledge graph ─────────────────────────────────────
        print("[Pipeline] Phase D — Neo4j graph")

        print("[Pipeline]   D1: repo node")
        try:
            GraphRepoIngestion().ingest_repos(db)
        except Exception as e:
            print(f"[Pipeline]   D1 repo node warning: {e}")

        print("[Pipeline]   D2: file nodes")
        try:
            GraphFileIngestionService().ingest_files(db, repo_id)
        except Exception as e:
            print(f"[Pipeline]   D2 file nodes warning: {e}")

        print("[Pipeline]   D3: engineer nodes + MODIFIED/OWNS edges")
        try:
            GraphEngineerIngestionService().engineer_ingest(db, repo_id)
        except Exception as e:
            print(f"[Pipeline]   D3 engineers warning: {e}")

        # Per-file graph passes
        files = db.query(File).filter(File.repo_id == repo_id).all()

        function_svc = FunctionGraphIngestionService()
        call_svc = CallGraphIngestionService()
        import_svc = ImportGraphIngestionServive()
        class_svc = GraphClassIngestionService()
        api_svc = GraphAPIIngestion()
        db_svc = GraphDatabaseIngestionService()
        service_svc = GraphServiceIngestionService()

        for file in files:
            try:
                print(f"[Pipeline]   D4-D10: graph for file_id={file.id} path={file.path}")
                function_svc.ingest_file(db, file.id)
                call_svc.ingest_file(db, file.id)
                import_svc.ingest_imports(db, file.id)
                class_svc.ingest_files(db, file.id)
                api_svc.ingest_files(db, file.id)
                db_svc.ingest_files(db, file.id)
                service_svc.ingest_services(db, file.id)
            except Exception as e:
                print(f"[Pipeline]   per-file graph warning file_id={file.id}: {e}")

        print("[Pipeline]   D11: PR + Engineer nodes and CREATED edges")
        try:
            GraphPrEngineerRelation().ingest_files(db)
        except Exception as e:
            print(f"[Pipeline]   D11 PR-engineer warning: {e}")

        print("[Pipeline]   D12: REVIEWS edges")
        try:
            GraphReviewRelation().create_relation(db, pr_id=1)  # iterates all reviews internally
        except Exception as e:
            print(f"[Pipeline]   D12 reviews warning: {e}")

        # ── Done ───────────────────────────────────────────────────────────────
        _set_status(db, repo_id, "ready")
        print(f"[Pipeline] ✅ Ingestion complete for repo_id={repo_id}")

    except Exception as exc:
        error_msg = traceback.format_exc()
        print(f"[Pipeline] ❌ Fatal error: {error_msg}")
        _set_status(db, repo_id, "failed", error=str(exc))

    finally:
        db.close()
