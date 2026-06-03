from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import ForeignKey, String, Text

class CodeFile(Base):
    __tablename__ = "code_files"

    id: Mapped[int] = mapped_column(primary_key=True)

    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), unique=True)

    language: Mapped[str] = mapped_column(String(50), nullable=True)

    content: Mapped[str] = mapped_column(Text)