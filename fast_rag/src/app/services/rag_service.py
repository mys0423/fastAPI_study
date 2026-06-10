import os
import glob
import shutil
import tempfile
from pathlib import Path
from fastapi import Depends
from lightrag import QueryParam
from app.infrastructure.rag_anything import RAGAnything, get_rag_engine
from app.repositories.document_repository import DocumentRepository, get_document_repository
from app.schemas.document_schema import DocumentCreateDTO, DocumentResponseDTO
from app.services.s3_service import S3Service, get_s3_service 

class RagService:
  def __init__(
    self, 
    document_repo: DocumentRepository,
    s3_service: S3Service,
    rag_engine: RAGAnything
  ):
    self.document_repo = document_repo
    self.s3_service = s3_service
    self.rag_engine = rag_engine
  
  async def ingest_document(self, file, member_id: int) -> DocumentResponseDTO:
    content = await file.read()

    await file.seek(0)
    s3_result = await self.s3_service.upload_file(file, "documents")
    print("s3_result", s3_result)

def get_rag_service(
  document_repo: DocumentRepository = Depends(get_document_repository),
  s3_service: S3Service = Depends(get_s3_service),
  rag_engine: RAGAnything = Depends(get_rag_engine)
):
  return RagService(document_repo, s3_service, rag_engine)