from fastapi import Depends
from app.infrastructure.postgresql import get_postgrsql_db
from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message_model import Message
from app.schemas.message_schema import MessageCreateDTO, MessageResponseDTO


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 추가
    async def create_message(self, message_create_dto: MessageCreateDTO) -> MessageResponseDTO:
        query = (
            insert(Message)
            .values(
                member_id=message_create_dto.member_id,
                message_content=message_create_dto.message_content,
                message_role=message_create_dto.message_role
            )
            .returning(Message)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return MessageResponseDTO.model_validate(result.scalar_one())


    # 전체 대화 목록(member_id)
    async def find_messages_by_member_id(self, member_id: int) -> list[MessageResponseDTO]:
        query = (
            select(Message)
            .where(Message.member_id == member_id)
            .order_by(Message.message_created_at.asc())
        )

        result = await self.db.execute(query)
        return [MessageResponseDTO.model_validate(messsage) for messsage in result.scalars().all()]


    # 최근 대화 목록(member_id)
    async def find_recent_messages_by_member_id(self, member_id: int, limit: int = 10) -> list[MessageResponseDTO]:
        query = (
            select(Message)
            .where(Message.member_id == member_id)
            .order_by(Message.message_created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [MessageResponseDTO.model_validate(messsage) for messsage in result.scalars().all()]
    

    # 대화 내용 수정
    async def update_message(self, message_id: int, message_content: str) -> MessageResponseDTO:
        query = (
            update(Message)
            .where(Message.id == message_id)
            .values(message_content=message_content)
            .returning(Message)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        message = result.scalar_one_or_none()
        return MessageResponseDTO.model_validate(message) if message else None


    # 대화 삭제
    async def delete_message(self, message_id: int) -> bool:
        query = (
            delete(Message)
            .where(Message.id == message_id)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0


    # 대화 삭제(탈퇴 시)
    async def delete_message_by_member_id(self, member_id: int) -> bool:
        query = (
            delete(Message)
            .where(Message.member_id == member_id)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0



def get_message_repository(db: AsyncSession = Depends(get_postgrsql_db)) -> MessageRepository:
    return MessageRepository(db)