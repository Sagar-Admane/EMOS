from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import ForeignKey, Text, DateTime

from datetime import datetime

class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    code_file_id: Mapped[int] = mapped_column(ForeignKey("code_files.id"))

    code_chunk_index: Mapped[int] = mapped_column(nullable=True)

    chunk_text: Mapped[str] = mapped_column(Text)

    start_line: Mapped[int]

    end_line: Mapped[int]

    chunk_hashed: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)