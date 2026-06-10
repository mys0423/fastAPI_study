from fastapi import Depends
from app.infrastructure.postgresql import get_postgrsql_db
from sqlalchemy import select, update, delete, insert, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.document_schema import DocumentCreateDTO, DocumentResponseDTO
from app.models.document_model import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 문서 추가
    async def create_document(self, document: DocumentCreateDTO) -> DocumentResponseDTO:
        new_document = {
            "document_name": document.document_name,
            "document_s3_key": document.document_s3_key,
            "member_id": document.member_id
        }

        query = (
            insert(Document)
            .values(**new_document)
            .returning(Document)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return DocumentResponseDTO.model_validate(result.scalar_one())


    # 문서 삭제
    async def delete_document(self, document_id: int) -> bool:
        query = (
            delete(Document)
            .where(Document.id == document_id)
        )    

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    
    # rag anything용 쿼리(local -> s3 주소로 변경쿼리)
    async def replace_image_path_in_all_chunks(self, local_path: str, s3_url: str) -> None:
        # lightrag_vdb_chunks
        await self.db.execute(
            text(
                "update lightrag_vdb_chunks set content = REPLACE(content, :local_path, :s3_url)", 
                {
                    "local_path": local_path, 
                    "s3_url": s3_url
                }
            )
        )

       # lightrag_doc_chunks
        await self.db.execute(
            text(
                "update lightrag_doc_chunks set content = REPLACE(content, :local_path, :s3_url)", 
                {
                    "local_path": local_path, 
                    "s3_url": s3_url
                }
            )
        )

        await self.db.commit()

def get_document_repository(db: AsyncSession = Depends(get_postgrsql_db)):
    return DocumentRepository(db)