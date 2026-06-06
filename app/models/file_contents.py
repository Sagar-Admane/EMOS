from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, DateTime, func

from datetime import datetime

class FileContent(Base):

    __tablename__="file_contents"

    id: Mapped[int] = mapped_column(primary_key=True)

    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id"),
        unique=True
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    content_hashed: Mapped[str] = mapped_column(
        String(64)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    file = relationship("File")