from app.models.base import Base

from sqlalchemy.orm import mapped_column, Mapped

from sqlalchemy import BigInteger, Text, ForeignKey, Integer, DateTime, String


class PullRequestReview(Base):
    __tablename__ = "pull_request_reviews"

    id : Mapped[int] = mapped_column(primary_key=True)

    pull_request_id = mapped_column(
        ForeignKey("pull_requests.id")
    )

    reviewer_username = mapped_column(
        String(255)
    )

    state = mapped_column(
        String(50)
    )

    submitted_at = mapped_column(
        DateTime
    )