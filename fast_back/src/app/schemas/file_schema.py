from pydantic import BaseModel

class FileUploadResponseDTO(BaseModel):
    original_key: str
    original_filename: str | None = None
    original_file_url: str | None = None
    original_file_ext: str | None = None
    thumbnail_key: str | None = None
    thumbnail_filename: str | None = None
    thumbnail_file_url: str | None = None
    thumbnail_file_ext: str | None = None