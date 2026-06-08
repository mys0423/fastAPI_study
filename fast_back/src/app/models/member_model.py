from app.infrastructure.oracle import Base

# ORM(sqlalchemy)
from sqlalchemy import String, Integer, BigInteger, DateTime, Sequence, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta, timezone

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from app.models.post_model import Post

KST = timezone(timedelta(hours=9)) # UTC+9

# 1개 테이블 == 1개 클래스
class Member(Base):
    __tablename__ = "TBL_MEMBER"

    id: Mapped[int] = mapped_column(BigInteger, Sequence("SEQ_MEMBER"), primary_key=True)
    # nullable=False: NOT NULL
    member_email: Mapped[str] = mapped_column(String(255), nullable=False)
    member_password: Mapped[str | None] = mapped_column(String(255))
    member_name: Mapped[str | None] = mapped_column(String(255))
    member_age: Mapped[int | None] = mapped_column(Integer)
    
    member_picture: Mapped[str | None] = mapped_column(String(255), default="/members/default.jpg")
    member_provider_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    member_provider: Mapped[str] = mapped_column(String(255))

    member_created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(KST))

    # 복합키
    __table_args__ = (
        UniqueConstraint("member_email", "member_provider", name="uq_member_email_member_provider"),
    )

    # 회원 1 : 게시글 N
    posts: Mapped[list["Post"]] = relationship(
       "Post",
       back_populates="member",
       cascade="all, delete-orphan"
    )
    