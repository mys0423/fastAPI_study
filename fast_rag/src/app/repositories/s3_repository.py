import os
from dotenv import load_dotenv
from botocore.client import BaseClient
from fastapi import Depends

from app.infrastructure.s3 import get_s3_client


load_dotenv()

AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")


class S3Repository:
    def __init__(self, s3_client: BaseClient):
        self.s3_client: BaseClient = s3_client
        self.bucket = AWS_S3_BUCKET

    # 업로드
    async def upload_fileobj(self, fileobj, key, content_type) -> None:
        await self.s3_client.upload_fileobj(
            fileobj,
            self.bucket,
            key,
            ExtraArgs={"ContentType": content_type}
        )

    # 이미지 여부 확인
    async def exists(self, key: str) -> bool:
        try:
            await self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
        
        except self.s3_client.exceptions.ClientError as e:
            return False


    # 이미지 조회
    def build_public_url(self, key: str) -> str:
        return f"https://{self.bucket}.s3.{AWS_REGION}.amazonaws.com/{key}"


    # 다운로드
    async def generate_presigned_url(self, key, expires_in=3600, disposition: str | None = None):
        params: dict = {"Bucket": self.bucket, "Key": key}
        if disposition:
            params["ResponseContentDisposition"] = disposition

        return await self.s3_client.generate_presigned_url(
            "get_object", 
            Params=params, 
            ExpiresIn=expires_in
        )

    # 삭제
    async def delete_object(self, key: str) -> None:
        await self.s3_client.delete_object(Bucket=self.bucket, Key=key)


def get_s3_repository(s3_client: BaseClient = Depends(get_s3_client)):
    return S3Repository(s3_client)
