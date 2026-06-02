from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, BigInteger
from datetime import datetime

class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True)

    github_repo_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(
        String,
        unique=True
    )
    owner: Mapped[str] = mapped_column(String)

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    default_branch: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    visibility: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )