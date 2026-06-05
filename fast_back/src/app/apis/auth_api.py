import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import RedirectResponse
from app.services.auth_service import get_auth_service, AuthService
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.member_schema import MemberClaimsDTO
from app.schemas.auth_schema import LoginRequestDTO, SocialLoginRequestDTO, JwtTokenDTO, AuthContextDTO
from app.enums.member_enum import MemberProvider
from app.dependencies.auth_dependency import get_tokens

# 소셜 로그인용 import
import httpx
from urllib.parse import urlencode

load_dotenv()

GOOGLE_AUTH_URL = os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_USERINFO_URL = os.getenv("GOOGLE_USERINFO_URL")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONT_END_URL = os.getenv("FRONT_END_URL")

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


@router.post(
    "/logout",
    response_model=ApiResponseDTO,
    summary="로그아웃"
)
async def logout(
    response:Response,
    auth_context: AuthContextDTO  = Depends(get_tokens),
    auth_servcie: AuthService = Depends(get_auth_service)
):
    
    print("auth_context", auth_context)

    tokens: JwtTokenDTO = auth_context.tokens
    member_claims = auth_context.member_claims

    # 로그아웃처리
    await auth_servcie.logout(member_claims.id, tokens)

    # 쿠키 삭제
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return ApiResponseDTO(
        success=True,
        message="로그아웃 성공"
    )


# 소셜 로그인(Google)
@router.get(
    "/login/google",
    summary="구글 로그인"
)
async def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }

    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


# 소셜 로그인(Google Callback)  
@router.get(
    "/login/google/callback",
    summary="구글 로그인"
)
async def google_login_callback(
    code: str,
    response: Response,
    auth_service = Depends(get_auth_service)
):

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data= {
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )

        token_data = token_res.json()
        google_access_token = token_data.get("access_token")

        # user info 조회
        async with httpx.AsyncClient() as client:
            user_res = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {google_access_token}"}
            )
            
        user_info = user_res.json()

        social_member = SocialLoginRequestDTO(
            member_email=user_info["email"],
            member_name=user_info["name"],
            member_picture=user_info["picture"],
            member_provider=MemberProvider.GOOGLE.value,
            member_provider_id=user_info["sub"]
        )
        tokens = await auth_service.social_login(social_member)

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