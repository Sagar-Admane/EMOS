# EMOS

EMOS is an AI-powered repository intelligence and analytics platform for GitHub repositories. It ingests repository data, builds graph-based relationships, generates embeddings, and exposes analytics and semantic search capabilities through a FastAPI backend and a React frontend.

## Overview

EMOS helps teams understand codebases by combining:

- GitHub repository ingestion
- Contributor and file-level analytics
- Commit and pull request analysis
- Graph-based dependency and relationship discovery
- Vector search and embeddings with Qdrant
- AI-assisted insights and prediction workflows

## Features

- Ingest repositories, branches, contributors, files, commits, and pull requests
- Analyze file ownership, hotspots, repository activity, and contribution trends
- Build and query a Neo4j knowledge graph of code relationships
- Store and search embeddings in Qdrant
- Expose analytics and semantic search through REST APIs
- Provide a modern React-based frontend for exploration

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Neo4j
- Qdrant
- Pydantic / Pydantic Settings
- Docker Compose

### Frontend
- React
- Vite
- React Router
- Lucide React

## Project Structure

- app/ - FastAPI application, routers, services, models, and prediction logic
- frontend/ - React frontend application
- alembic/ - Database migrations
- docker-compose.yml - Local infrastructure for PostgreSQL, Neo4j, and Qdrant
- requirements.txt - Python dependencies

## Prerequisites

Before running the project, make sure you have installed:

- Python 3.10 or newer
- Node.js 18 or newer
- Docker and Docker Compose
- Git

## Environment Variables

Create a .env file in the project root with the following values:

```env
DATABASE_URL=postgresql://sagar:sagar@localhost:5432/emos
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
```

> The default Docker Compose setup already exposes PostgreSQL and Neo4j using the credentials above.

## Running with Docker

Start the supporting services:

```bash
docker compose up -d
```

This will launch:

- PostgreSQL on port 5432
- Neo4j on ports 7474 and 7687
- Qdrant on ports 6333 and 6334

## Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API docs will be available at:

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Frontend Setup

Install frontend dependencies:

```bash
cd frontend
npm install
```

Start the local development server:

```bash
npm run dev
```

The frontend will typically run at:

- http://localhost:5173

## Initializing Data Services

Once the backend is running, you can initialize the vector store with:

```bash
curl http://localhost:8000/qdrant/init
```

You can also trigger repository ingestion endpoints depending on your workflow and GitHub token permissions.

## API Highlights

Some of the available API areas include:

- Repository summaries
- Contributor analytics
- File ownership and hotspot analytics
- Pull request review analysis
- Semantic search and embedding generation
- AI and prediction routers

## Development Notes

- The backend is organized around routers, services, repositories, and models under the app directory.
- The frontend is a separate React/Vite application and can be developed independently of the backend.
- Database migrations are managed using Alembic.

## License

This project is distributed as-is for development and evaluation purposes.
