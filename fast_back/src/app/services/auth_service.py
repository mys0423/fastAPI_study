from fastapi import Depends, HTTPException, status
from app.services.member_service import get_member_service, MemberService
from redis.asyncio import Redis
from app.services.redis_service import get_redis_service, RedisService
from app.utils.security_util import verify_password
from app.utils.jwt_token_util import (
    parse_token, reissue_access_token, generate_access_token, generate_refresh_token
)
from app.schemas.auth_schema import LoginRequestDTO, SocialLoginRequestDTO, JwtTokenDTO
from app.schemas.member_schema import MemberClaimsDTO

class AuthService:
    def __init__(self, member_service, redis_service):
        self.member_service = member_service
        self.redis_service = redis_service

    # 로그인
    async def login(self, login_request_dto: LoginRequestDTO):

        # 1) 회원 조회
        member_in_db = await self.member_service.get_member_for_login(
            login_request_dto.member_email,
            login_request_dto.member_provider
        )

        # 2) 비밀번호 검증
        if not verify_password(login_request_dto.member_password, member_in_db.member_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="비밀번호 불일치")
        
        # 3) payload 제작
        claims = MemberClaimsDTO(
            id=member_in_db.id,
            member_email=member_in_db.member_email,
            member_provider=member_in_db.member_provider
        )

        # 4) 토큰 제작
        access_token = generate_access_token(claims)
        refresh_token = generate_refresh_token(claims)

        tokens = JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )

        # 5) redis refresh 등록
        await self.redis_service.save_refresh_token(member_in_db.id, refresh_token)
        return tokens

    # 소셜 로그인 
    async def social_login(self, social_member: SocialLoginRequestDTO):

        # 1) 회원 조회 및 회원 가입
        member_in_db = await self.member_service.social_login_or_create(social_member)
        
        # 2) payload 제작
        claims = MemberClaimsDTO(
            id=member_in_db.id,
            member_email=member_in_db.member_email,
            member_provider=member_in_db.member_provider
        )

        # 3) 토큰 제작
        access_token = generate_access_token(claims)
        refresh_token = generate_refresh_token(claims)

        tokens = JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )

        # 4) redis refresh 등록
        await self.redis_service.save_refresh_token(member_in_db.id, refresh_token)
        return tokens


    # 로그아웃
    # refresh token -> access token 재발급
    async def logout(self, member_id: int, jwt_token_dto: JwtTokenDTO) -> None: 
        # refresh token 삭제
        access_token = jwt_token_dto.access_token
        await self.redis_service.delete_refresh_token(member_id)

        # access token 블랙리스트에 추가
        await self.redis_service.save_blacklisted_token(access_token)














def get_auth_service(
        member_service: MemberService = Depends(get_member_service),
        redis_service: RedisService = Depends(get_redis_service)
):
    return AuthService(member_service, redis_service)