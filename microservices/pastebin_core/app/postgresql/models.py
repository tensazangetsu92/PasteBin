from datetime import datetime
from microservices.pastebin_core.app.postgresql.database import Base
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class TextUrlOrm(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    blob_url: Mapped[str] = mapped_column(String, nullable=False)
    short_key: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    # author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # author: Mapped["UserOrm"] = relationship("UserOrm", back_populates="text_urls")
