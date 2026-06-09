import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

POSTGRESQL_DATABASE_URL = os.getenv("POSTGRESQL_DATABASE_URL")

# 1. 비동기 전용 DB엔진 생성
engine = create_async_engine(
  POSTGRESQL_DATABASE_URL,
  echo=True
)

# 2. 비동기 세션 생성기
AsyncSessionLocal = async_sessionmaker(
  bind=engine,
  class_=AsyncSession,
  expire_on_commit=False #필수
)

# 2.0 베이스 클래스를 반드시 상속받아서
# Model의 테이블을 생성해야한다.
class Base(DeclarativeBase):
  pass

# 3. 비동기 서버 의존성 주입 함수
async def get_postgrsql_db():
  async with AsyncSessionLocal() as db:
    try:
      yield db
    
    finally:
      await db.close()