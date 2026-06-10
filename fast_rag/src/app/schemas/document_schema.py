from datetime import datetime
from pydantic import BaseModel

class DocumentCreateDTO(BaseModel):
  document_name: str
  document_s3_key: str
  member_id: int

class DocumentResponseDTO(BaseModel):
  id: int
  document_name: str
  document_s3_key: str
  document_created_at: datetime
  member_id: int

  class Config:
        from_attributes = True