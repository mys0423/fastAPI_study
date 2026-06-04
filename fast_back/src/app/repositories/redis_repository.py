from fastapi import Depends
from redis.asyncio import Redis
from app.infrastructure.redis import get_redis_db


class RedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    # key 유무 확인
    async def exists(self, key) -> bool:
        result = await self.redis_client.exists(key)
        return result > 0

    # 추가
    async def set(self, key: str, value: str, ex: int = 3600) -> None:
        await self.redis_client.set(key, value, ex=ex)

    # 조회
    async def get(self, key: str) -> str | None:
        return await self.redis_client.get(key)

    # 삭제
    async def delete(self, key) -> None:
        await self.redis_client.delete(key)


def get_redis_repository(redis: Redis = Depends(get_redis_db)):
    return RedisRepository(redis)