from fastapi import APIRouter, Depends, Response
from app.services.auth_service import get_auth_service, AuthService
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimsDTO
from app.schemas.auth_schema import LoginRequestDTO, SocialLoginRequestDTO, JwtTokenDTO
from app.enums.member_enum import MemberProvider


router = APIRouter()

@router.post(
    "/login",
    summary="로컬 로그인",
    response_model=ApiResponseDTO
)
async def login(
    login_member: LoginRequestDTO,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    
    login_member.member_provider = MemberProvider.LOCAL.value
    tokens = await auth_service.login(login_member)
    
    # cookie -> token
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30
    )

    return ApiResponseDTO(
        success=True,
        message="로그인 성공",
    )