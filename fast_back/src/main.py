from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infrastructure.oracle import engine, Base
from app.infrastructure.redis import start_redis_client
from app.security.cors import setup_cors
from app.security.security_headers import setup_security
from app.apis import member_api, auth_api, file_api

import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Oracle DB 연결 성공!")

    async with start_redis_client(app):
        print("Redis DB 연결 성공!")

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

app.include_router(member_api.router, prefix="/members", tags=["members"])
app.include_router(auth_api.router, prefix="/auth", tags=["/auth"])
app.include_router(file_api.router, prefix="/auth", tags=["/files"])
