from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.services.rag_service import RagService, get_rag_service
from app.dependencies.auth_dependency import get_auth_context
from app.schemas.auth_schema import AuthContextDTO
from app.schemas.common_schema import ApiResponseDTO
router = APIRouter()

# pdf 업로드 -> S3 저장 -> rag anything 전처리 -> postgrsql 저장
@router.post(
  "/upload-pdf",
  summary="pdf upload, rag processing"
)
async def upload_pdf(
  file: UploadFile = File(...),
  auth_context: AuthContextDTO = Depends(get_auth_context),
  rag_service: RagService = Depends(get_rag_service)
):
  member_id = auth_context.member_claims.id

  if not file.filename.lower().endwsith(".pdf") or file.content_type != "application/pdf":
    return ApiResponseDTO(
      success=False,
      message="pdf 파일만 업로드 가능합니다."
    )

  await rag_service.ingest_document(file, member_id)


# pdf 업로드 파일 질문

