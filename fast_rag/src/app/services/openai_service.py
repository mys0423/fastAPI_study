import os
import asyncio
from dotenv import load_dotenv
from fastapi import Depends
from openai import OpenAI

from app.schemas.llm_schema import ChatRequestDTO

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_client = OpenAI(
    api_key=OPENAI_API_KEY
)

class OpenAIService:

    async def chat(self, chat_request_dto: ChatRequestDTO) -> str:
        result = llm_client.responses.create(
            model="gpt-3.5-turbo",
            input=chat_request_dto.question
        )

        return result.output_text

    
    async def chat_stream(self, chat_request_dto: ChatRequestDTO):
        with llm_client.responses.stream(
            model="gpt-3.5-turbo",
            input=chat_request_dto.question
        ) as stream:
            for e in stream:
                if e.type == "response.output_text.delta":
                    yield e.delta
                    await asyncio.sleep(0.05)

def get_openai_service() -> OpenAIService:
    return OpenAIService()