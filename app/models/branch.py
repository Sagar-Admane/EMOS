from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import ForeignKey, String

class Branch(Base):
    __tablename__="branches"

    id: Mapped[int] = mapped_column(primary_key=True)

    repo_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    name: Mapped[str] = mapped_column(String(255))