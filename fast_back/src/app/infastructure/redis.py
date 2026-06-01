# redis stack
# 설정의 책임 분리(Separation of Concerns)
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import redis.asyncio as redis # 서버연결 비동기

# .env 설정 
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# 클라이언트 설정
redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )

# 기존에 사용했던 startup, shutdown 방법보다
# lifespan 새로운 권장방식
@asynccontextmanager
async def start_redis_client(app: FastAPI):
    try:
        # Redis 연결
        app.state.redis = redis_client

        try:
            await app.state.redis.ping()
            
        except Exception as e:
            print("Redis connection failed:", e)
        yield  # 여기서 FastAPI 라우터 실행
    finally:
        await app.state.redis.close()


# 꺼내쓰는 DB DI 팩토리 메서드
def get_redis_db(request: Request):
    return request.app.state.redis