from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Boolean,
    DateTime,
    BigInteger
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.models.base import Base


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    repo_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id")
    )

    github_pr_id: Mapped[int] = mapped_column(BigInteger)

    number: Mapped[int]

    title: Mapped[str] = mapped_column(Text)

    body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    state: Mapped[str] = mapped_column(
        String(50)
    )

    author: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    merged: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    merged_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )