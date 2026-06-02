import os
from dotenv import load_dotenv
# 비동기 전용 엔진과 세션 메이커
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

ORACLE_DATABASE_URL = os.getenv("ORACLE_DATABASE_URL")

# 1. 비동기 전용 DB 엔진 생성
engine = create_async_engine(
    ORACLE_DATABASE_URL, 
    echo=True,
)

# 2. 비동기 세션 생성기 (expire_on_commit=False는 비동기에서 필수 설정)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 2.0 베이스 클래스는 반드시 1번만 생성
# Model들은 이 Base를 상속받아 테이블을 생성 
class Base(DeclarativeBase):
    pass

# 3. FastAPI용 비동기 의존성 주입(Dependency) 함수
# DB서버를 극한까지 성능을 올리기 위해 비동기 서버를 많이 구현(실무)
# 생성형 DI
async def get_oracle_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()