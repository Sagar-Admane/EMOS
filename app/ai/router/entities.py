import re

from app.ai.router.schemas import Entity
from app.ai.router.utils import extract_author, extract_file, extract_repository


class EntityExtractor:

    def extract(self, question: str):
        entities: list[Entity] = []
        question_text = (question or "").strip()

        if not question_text:
            return entities

        repository = extract_repository(question_text)
        if repository:
            entities.append(Entity(typing="repository", value=repository))

        file_path = extract_file(question_text)
        if file_path:
            entities.append(Entity(typing="file", value=file_path))

        author = extract_author(question_text)
        if author:
            entities.append(Entity(typing="author", value=author))

        return entities