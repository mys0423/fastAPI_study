from datetime import datetime, timedelta, timezone
from sqlalchemy import BigInteger, DateTime, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.postgresql import Base
from app.enums.message_enum import MessageRole

KST = timezone(timedelta(hours=9))

class Message(Base):
  __tablename__ = "messages"

  # Identity(): 자동증가 - GENERATED AS IDENTITY 표준 SQL 권장 방식
  id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
  message_role: Mapped[str] = mapped_column(String(20), nullable=False)
  message_content: Mapped[str] = mapped_column(Text, nullable=False)
  message_created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=lambda: datetime.now(KST)
  )

  # FK
  member_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)