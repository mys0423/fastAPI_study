from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infrastructure.postgresql import engine, Base

from app.infrastructure.redis import init_redis_client
from app.security.cors import setup_cors
from app.security.security_headers import setup_security

import app.models
from app.apis import openai_api, langchain_api

@asynccontextmanager
async def lifespan(app: FastAPI):
  
    async with init_redis_client(app):
        print("Redis 실행 완료!")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("POSTGRESQL 연결 성공!")
        
        yield
    

# Swagger
# http://localhost:8000/docs
app = FastAPI(
    lifespan=lifespan,
    title="fast API Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

setup_cors(app)
setup_security(app)

app.include_router(openai_api.router, prefix="/llms", tags=["llms"])
app.include_router(langchain_api.router, prefix="/langchains", tags=["langchains"])