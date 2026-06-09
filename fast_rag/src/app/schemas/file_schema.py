from pydantic import BaseModel

class FileUploadResponseDTO(BaseModel):
    original_key: str
    thumbnail_key: str