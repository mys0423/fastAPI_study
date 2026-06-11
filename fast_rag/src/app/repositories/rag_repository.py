from fastapi import Depends
from app.infrastructure.postgresql import get_postgrsql_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class RagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # rag anything용 쿼리(local -> s3 주소로 변경쿼리)
    async def replace_image_path_in_all_chunks(self, local_path: str, s3_url: str) -> None:
        # lightrag_vdb_chunks
        await self.db.execute(
            text("update lightrag_vdb_chunks set content = REPLACE(content, :local_path, :s3_url)"),
            {
                "local_path": local_path, 
                "s3_url": s3_url
            }
        )

       # lightrag_doc_chunks
        await self.db.execute(
            text("update lightrag_doc_chunks set content = REPLACE(content, :local_path, :s3_url)"),
            {
                "local_path": local_path, 
                "s3_url": s3_url
            }
        )

        await self.db.commit()

def get_rag_repository(db: AsyncSession = Depends(get_postgrsql_db)):
    return RagRepository(db)