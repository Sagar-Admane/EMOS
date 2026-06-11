from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, DateTime, BigInteger

from datetime import datetime


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(primary_key=True)

    repo_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id")
    )

    github_deployment_id: Mapped[int] = mapped_column(
        BigInteger
    )

    environment: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    creator_username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )