import os
import asyncio
from dotenv import load_dotenv
from fastapi import Depends
from app.schemas.member_schema import MemberClaimsDTO
from app.schemas.llm_schema import ChatRequestDTO

from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from typing import AsyncGenerator

from app.repositories.message_repository import get_message_repository, MessageRepository
from app.schemas.message_schema import MessageCreateDTO, MessageResponseDTO
from app.enums.message_enum import MessageRole

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

class LangChainService:

    def __init__(self, repo: MessageRepository):
        self.repo = repo

    def build_history_messages(self, history: list[MessageResponseDTO]) -> list:
        messages = []
        for message in history:
            if message.message_role == MessageRole.USER:
                messages.append(("human", message.message_content))
            elif message.message_role == MessageRole.ASSISTANT:
                messages.append(("assistant", message.message_content))
        return messages


    async def chat(self, member_id: int, chat_request_dto: ChatRequestDTO) -> str:

        history = await self.repo.find_recent_messages_by_member_id(member_id)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            *self.build_history_messages(history), # 평탄화
            ("human", "{question}"),
        ])

        chain = prompt | llm
        result = await chain.ainvoke({
            "system_prompt": chat_request_dto.system_prompt,
            "question": chat_request_dto.question
        })

        new_user_message = MessageCreateDTO(
            message_content=chat_request_dto.question,
            message_role=MessageRole.USER.value,
            member_id=member_id
        )

        # 메세지 생성
        # User
        await self.repo.create_message(new_user_message)
        
        # AI
        new_ai_message = MessageCreateDTO(
            message_content = result.content,
            message_role=MessageRole.ASSISTANT.value,
            member_id=member_id,
        )
        await self.repo.create_message(new_ai_message)
        return result.content


    async def chat_stream(self, member_id: int, chat_request_dto: ChatRequestDTO) -> AsyncGenerator:
        history = await self.repo.find_recent_messages_by_member_id(member_id)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            *self.build_history_messages(history), # 평탄화
            ("human", "{question}"),
        ])

        chain = prompt | llm

        full_response = ""
        async for chunk in chain.astream({
            "system_prompt": chat_request_dto.system_prompt,
            "question": chat_request_dto.question
        }):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
                await asyncio.sleep(0.05)

        # User
        new_user_message = MessageCreateDTO(
            message_content=chat_request_dto.question,
            message_role=MessageRole.USER.value,
            member_id=member_id
        )
        await self.repo.create_message(new_user_message)

        # Ai
        new_ai_message = MessageCreateDTO(
            message_content=full_response,
            message_role=MessageRole.ASSISTANT.value,
            member_id=member_id
        )
        await self.repo.create_message(new_ai_message)


def get_langchain_service(
        repo: MessageRepository = Depends(get_message_repository)
) -> LangChainService:
    return LangChainService(repo)

