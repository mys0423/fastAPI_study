import asyncio
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimsDTO
from app.dependencies.auth_dependency import get_auth_context
from app.schemas.llm_schema import ChatRequestDTO
from app.services.openai_service import OpenAIService, get_openai_service

router = APIRouter()

@router.post(
    "/chat-bot",
    summary="llm 모델 응답",
    response_model=ApiResponseDTO
)
async def chat(
    chat_reqeust_dto: ChatRequestDTO,
    auth_context: MemberClaimsDTO = Depends(get_auth_context),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    response_data = await openai_service.chat(chat_reqeust_dto)
    
    return ApiResponseDTO(
        success=True,
        message="llm 응답 성공",
        data=response_data
    )


@router.post(
    "/chat-bot/stream",
    summary="llm 모델 stream 응답",
)
async def chat_stream(
    chat_reqeust_dto: ChatRequestDTO,
    auth_context: MemberClaimsDTO = Depends(get_auth_context),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    return StreamingResponse(
        openai_service.chat_stream(chat_reqeust_dto),
        media_type="text/plain"
    )