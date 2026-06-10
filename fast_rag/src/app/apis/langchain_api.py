import asyncio
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimsDTO
from app.dependencies.auth_dependency import get_auth_context
from app.schemas.llm_schema import ChatRequestDTO
from app.services.langchain_service import LangChainService, get_langchain_service

router = APIRouter()

@router.post(
    "/chat-bot",
    summary="llm 모델 응답",
    response_model=ApiResponseDTO
)
async def chat(
    chat_reqeust_dto: ChatRequestDTO,
    auth_context: MemberClaimsDTO = Depends(get_auth_context),
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    member_id = auth_context.member_claims.id 
    result = await langchain_service.chat(member_id, chat_reqeust_dto)
    return ApiResponseDTO(
        success=True,
        message="응답 성공",
        data=result
    )


@router.post(
    "/chat-bot/stream",
    summary="llm 모델 stream 응답",
)
async def chat_stream(
    chat_reqeust_dto: ChatRequestDTO,
    auth_context: MemberClaimsDTO = Depends(get_auth_context),
    langchain_service: LangChainService = Depends(get_langchain_service)
):
    
    member_id = auth_context.member_claims.id 
    return StreamingResponse(
        langchain_service.chat_stream(member_id, chat_reqeust_dto),
        media_type="text/plain"
    )