from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class CommitFile(Base):
    __tablename__ = "commit_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    commit_id: Mapped[int] = mapped_column(
        ForeignKey("commits.id")
    )

    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id")
    )

    additions: Mapped[int]

    deletions: Mapped[int]