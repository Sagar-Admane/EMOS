from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import ForeignKey, Text

class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    code_file_id: Mapped[int] = mapped_column(ForeignKey("code_files.id"))

    chunk_text: Mapped[str] = mapped_column(Text)

    start_line: Mapped[int]

    end_line: Mapped[int]