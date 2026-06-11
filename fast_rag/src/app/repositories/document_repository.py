from fastapi import Depends
from app.infrastructure.postgresql import get_postgrsql_db
from sqlalchemy import insert, delete
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
    
    
def get_document_repository(db: AsyncSession = Depends(get_postgrsql_db)):
    return DocumentRepository(db)