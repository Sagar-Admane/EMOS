from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from datetime import datetime


class ConnectedRepo(Base):
    __tablename__ = "connected_repos"

    id: Mapped[int] = mapped_column(primary_key=True)

    repo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("repositories.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Status: pending | indexing | ready | failed
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False
    )

    qdrant_collection: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    connected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
