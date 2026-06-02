from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from app.models.base import Base

class Commit(Base):
    __tablename__ = "commits"

    id: Mapped[int] = mapped_column(primary_key=True)

    repo_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id")
    )

    sha: Mapped[str] = mapped_column(
        String(40),
        unique=True
    )

    message: Mapped[str] = mapped_column(Text)

    author_name: Mapped[str] = mapped_column(
        String(255)
    )

    author_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    parent_sha: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True
    )

    commit_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    github_commit_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )