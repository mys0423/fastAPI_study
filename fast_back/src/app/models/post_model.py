from app.infrastructure.oracle import Base

# ORM(sqlalchemy)
from sqlalchemy import String, Integer, BigInteger, DateTime, Sequence, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta, timezone

from typing import TYPE_CHECKING

KST = timezone(timedelta(hours=9)) # UTC+9

if TYPE_CHECKING:
  from app.models.member_model import Member

class Post(Base):
  __tablename__="TBL_POST"

  id: Mapped[int] = mapped_column(BigInteger, Sequence("SEQ_POST"), primary_key=True)
  post_title: Mapped[str] = mapped_column(String(255), nullable=False)
  post_content: Mapped[str] = mapped_column(String(255), nullable=False)
  post_created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(KST))
  post_updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(KST))

  # 외래키(FK) 설정
  member_id: Mapped[int] = mapped_column(ForeignKey("TBL_MEMBER.id"), nullable=False)

  member: Mapped["Member"] = relationship(
    "Member",
    back_populates="posts"
  )
