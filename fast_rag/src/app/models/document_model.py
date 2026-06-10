from datetime import datetime, timedelta, timezone
from sqlalchemy import BigInteger, DateTime, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.postgresql import Base
from app.enums.message_enum import MessageRole

KST = timezone(timedelta(hours=9))

class Document(Base):
  __tablename__="documents"

  id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
  document_name: Mapped[str] = mapped_column(Text, nullable=False)
  document_s3_key: Mapped[str] = mapped_column(Text, nullable=False)
  document_created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=lambda: datetime.now(KST)
  )
  member_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

