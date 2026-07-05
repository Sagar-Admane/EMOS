import re
from typing import Any


def normalize_question(question: str) -> str:
    return (question or "").strip().lower()


def extract_repository(question: str) -> str | None:
    patterns = [
        r"\brepo(?:sitory)?\s+([a-zA-Z0-9._/-]+)",
        r"\bin\s+repo(?:sitory)?\s+([a-zA-Z0-9._/-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_file(question: str) -> str | None:
    patterns = [
        r"\bfile\s+([a-zA-Z0-9._/-]+)",
        r"\b([a-zA-Z0-9._/-]+\.py|[a-zA-Z0-9._/-]+\.js|[a-zA-Z0-9._/-]+\.ts)",
    ]
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_author(question: str) -> str | None:
    match = re.search(r"\bby\s+([A-Za-z0-9._-]+)", question, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def infer_filters(question: str) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    repository = extract_repository(question)
    if repository:
        filters["repository"] = repository

    file_path = extract_file(question)
    if file_path:
        filters["file"] = file_path

    author = extract_author(question)
    if author:
        filters["author"] = author

    return filters