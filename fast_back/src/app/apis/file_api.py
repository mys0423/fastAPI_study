from fastapi import APIRouter, Depends, Query, UploadFile, File
from app.schemas.common_schema import ApiResponseDTO
from app.services.s3_service import S3Service, get_s3_service

router = APIRouter()

@router.post(
    "/upload",
    summary="파일 업로드",
    response_model=ApiResponseDTO
)
async def upload(
    file: UploadFile = File(...),
    s3_service: S3Service = Depends(get_s3_service)
):
    upload_response = await s3_service.upload_image_with_thumbnail(file)

    return ApiResponseDTO(
        success=True, 
        message="업로드 성공",
        data=upload_response
    )


@router.get(
    "/url",
    summary="파일 조회"
)
async def get_url(
    key: str = Query(..., description="S3 이미지 key"),
    s3_service: S3Service = Depends(get_s3_service)
):
    url = await s3_service.get_url(key)
    return url


@router.get(
    "/download",
    summary="파일 다운로드"
)
async def get_download_url(
    key: str = Query(..., description="S3 이미지 key"),
    s3_service: S3Service = Depends(get_s3_service)
):

    download_url = await s3_service.get_download_url(key)
    return download_url


@router.delete(
    "/delete",
    summary="파일 삭제"
)
async def delete_file(
    key: str = Query(..., description="S3 이미지 key"),
    s3_service: S3Service = Depends(get_s3_service)
):
    await s3_service.delete_file(key)

    return ApiResponseDTO(
        success=True,
        message="파일 삭제 성공"
    )