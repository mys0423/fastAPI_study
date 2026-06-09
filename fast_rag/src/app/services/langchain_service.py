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

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

class LangChainService:
    async def chat(self, chat_request_dto: ChatRequestDTO) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{question}"),
        ])

        chain = prompt | llm
        result = await chain.ainvoke({
            "system_prompt": chat_request_dto.system_prompt,
            "question": chat_request_dto.question
        })

        return result.content


    async def chat_stream(self, chat_request_dto: ChatRequestDTO) -> AsyncGenerator:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{question}"),
        ])

        chain = prompt | llm
        async for chunk in chain.astream({
            "system_prompt": chat_request_dto.system_prompt,
            "question": chat_request_dto.question
        }):
            if chunk.content:
                yield chunk.content
                await asyncio.sleep(0.05)


def get_langchain_service() -> LangChainService:
    return LangChainService()

