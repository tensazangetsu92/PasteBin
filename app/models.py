import datetime
from .database import Base
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TextUrlOrm(Base):
    __tablename__ = "text_urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    blob_url: Mapped[str] = mapped_column(String, nullable=False)
    short_key: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    # created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # expires_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)

    # author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # author: Mapped["UserOrm"] = relationship("UserOrm", back_populates="text_urls")


# class UserOrm(Base):
#     __tablename__ = 'users'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     username: Mapped[str] = mapped_column(String, unique=True, index=True)
#     email: Mapped[str] = mapped_column(String, unique=True, index=True)
#     password_hash: Mapped[str] = mapped_column(String)
#     created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
#
#     texts: Mapped[list["TextOrm"]] = relationship("TextOrm", back_populates="author")
#
#     def __repr__(self):
#         return f"<User(id={self.id}, username={self.username}, email={self.email})>"

