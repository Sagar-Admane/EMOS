from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import ForeignKey, String, Text

class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)

    repo_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    path: Mapped[str] = mapped_column(Text)

    extension: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    size: Mapped[int | None] = mapped_column(
        nullable=True
    )

    last_modified_commit: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True
    )