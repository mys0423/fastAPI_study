import os
from fastapi import Depends, HTTPException, status
from dotenv import load_dotenv
from redis.asyncio import Redis
from app.repositories.redis_repository import RedisRepository, get_redis_repository

load_dotenv()

REFRESH_TOKEN_PREFIX = os.getenv("REFRESH_TOKEN_PREFIX")
TOKEN_BLACKLIST_PREFIX = os.getenv("TOKEN_BLACKLIST_PREFIX")

class RedisService:
    def __init__(self, repo):
        self.repo = repo 

    # Redis Stack에 리프레쉬을 저장
    async def save_refresh_token(self, member_id: int, refresh_token: str) -> None:
        try:
            key = f"{REFRESH_TOKEN_PREFIX}{member_id}"
            ex = 60 * 60 * 24 * 30 #30일
            
            await self.repo.set(key, refresh_token, ex=ex)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 유요하지 않거나 만료되었습니다."
            )

    # 저장된 리프레쉬가 유효한지
    async def validate_refresh_token(self, member_id, refresh_token: str) -> bool:
        key = f"{REFRESH_TOKEN_PREFIX}{member_id}"
        is_validated = await self.repo.exists(key)

        if not is_validated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 유요하지 않거나 만료되었습니다."
            )

        return is_validated


    # Redis Stack에 등록된 토큰 삭제
    async def delete_refresh_token(self, member_id: int) -> None:
        key = f"{REFRESH_TOKEN_PREFIX}{member_id}"
        await self.repo.delete(key)

    # Redis Stack에 블랙리스트에 토큰 등록
    async def save_blacklisted_token(self, access_token: str) -> None:
        try:
            key = f"{TOKEN_BLACKLIST_PREFIX}{access_token}"
            ex = 60 * 60 * 24 #1days

            await self.repo.set(key, "blacklisted", ex=ex)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 유효하지 않거나 만료되었습니다."
            )

    # 블랙리스트 토큰인지 검증
    async def is_blacklisted_token(self, access_token: str) -> bool:
        key = f"{TOKEN_BLACKLIST_PREFIX}{access_token}"

        return await self.repo.exists(key)

def get_redis_service(redis: Redis = Depends(get_redis_repository)):
    return RedisService(redis)