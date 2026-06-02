from app.models.base import Base

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, String, BigInteger

class Contributor(Base):
    __tablename__ = "contributors"

    id: Mapped[int] = mapped_column(primary_key=True)

    repo_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.id")
    )

    github_user_id: Mapped[int] = mapped_column(BigInteger)

    username: Mapped[str] = mapped_column(String(255))

    contributions: Mapped[int] = mapped_column(default=0)