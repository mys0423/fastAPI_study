from datetime import datetime
from pydantic import BaseModel
from app.enums.message_enum import MessageRole

class MessageCreateDTO(BaseModel):
    member_id: int
    message_content: str
    message_role: MessageRole
    
class MessageResponseDTO(BaseModel):
    id: int
    message_content: str
    message_role: MessageRole
    message_created_at: datetime
    member_id: int
    
    class Config:
        from_attributes = True