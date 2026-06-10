import io
import os
import uuid

from fastapi import Depends, HTTPException, status
from PIL import Image
from botocore.client import BaseClient

from app.schemas.file_schema import FileUploadResponseDTO
from app.repositories.s3_repository import S3Repository, get_s3_repository

class S3Service:
    def __init__(self, repo: S3Repository):
        self.repo = repo

    # 업로드
    async def upload_image_with_thumbnail(self, file, folder: str = "images"):
        original_filename = os.path.basename(file.filename)
        file_ext = original_filename.split(".")[-1]
        file_uuid = str(uuid.uuid4())

        saved_filename = f"{file_uuid}_{original_filename}"
        saved_thumbnail_filename = f"t_{file_uuid}_{original_filename}"

        original_key = f"{folder}/original/{saved_filename}"
        thumbnail_key = f"{folder}/thumbnail/{saved_thumbnail_filename}"

        # 원본 이미지 업로드
        await self.repo.upload_fileobj(file.file, original_key, file.content_type)

        # 초기화 
        file.file.seek(0)

        # 썸네일 제작
        thumb_buffer = self.make_thumbnail(file.file, file_ext)

        # 썸네일 업로드 
        await self.repo.upload_fileobj(thumb_buffer, thumbnail_key, file.content_type)

        return FileUploadResponseDTO(
            original_key=original_key,
            thumbnail_key=thumbnail_key
        )


    # 이미지 보기
    async def get_url(self, key):
        is_exists = await self.repo.exists(key)

        if not is_exists:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이미지가 존재하지 않습니다."
            )

        return self.repo.build_public_url(key)


    # 이미지 다운로드
    async def get_download_url(self, key):
        filename = os.path.basename(key)

        return await self.repo.generate_presigned_url(
            key, expires_in=3600, disposition=f"attachment; filename={filename}"
        )


    # 이미지 삭제 
    async def delete_file(self, key):
        await self.repo.delete_object(key)


    # 썸네일 제작 함수
    @staticmethod
    def make_thumbnail(fileobj, ext: str):
        format_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
        format = format_map.get(ext, "JPEG")

        image = Image.open(fileobj).convert("RGB")
        image.thumbnail((100, 100))

        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer


    # Rag용 file upload
    async def upload_file(self, file, folder: str) -> FileUploadResponseDTO:
        original_filename = os.path.basename(file.filename)
        file_ext = original_filename.split(".")[-1].lower()
        file_uuid = str(uuid.uuid4())

        save_filename = f"{file_uuid}_{original_filename}"
        key = f"{folder}/{save_filename}"

        await self.repo.upload_fileobj(
            file.file,
            key,
            file.content_type
        )

        return FileUploadResponseDTO(
            original_key=key,
            original_filename=original_filename,
            original_file_ext=file_ext,
            original_file_url=await self.get_url(key)
        )

    # rag output file upload
    async def upload_local_file(self, local_path: str, folder: str):
        original_filename = os.path.basename(local_path)
        file_ext = original_filename.split(".")[-1].lower()
        file_uuid = str(uuid.uuid4())
        save_filename = f"{file_uuid}_{original_filename}"
        key = f"{folder}/{save_filename}"
        content_type = f"image/{file_ext}" if file_ext in ["png", "jpg", "jpeg"] else "application/octet-stream"

        with open(local_path, "rb") as f:
            await self.repo.upload_fileobj(f, key, content_type)

        return FileUploadResponseDTO(
            original_key=key,
            original_filename=original_filename,
            original_file_ext=file_ext,
            original_file_url=await self.get_url(key)
        )


def get_s3_service(s3_repo: S3Repository = Depends(get_s3_repository)):
    return S3Service(s3_repo)