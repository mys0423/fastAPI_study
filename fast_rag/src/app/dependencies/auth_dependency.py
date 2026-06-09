from fastapi import Request, HTTPException, status, Depends
from app.schemas.member_schema import MemberClaimsDTO
from app.schemas.auth_schema import JwtTokenDTO, AuthContextDTO
from app.utils.jwt_token_util import parse_token
from app.services.redis_service import RedisService, get_redis_service
from jose import JWTError

async def get_auth_context(
        request: Request,
        redis_service: RedisService = Depends(get_redis_service)
) -> JwtTokenDTO:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="접근 권한 없음(access token)"
        )
    
    try:

        member_claims = parse_token(access_token)
        tokens = JwtTokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )

        return AuthContextDTO(
            member_claims=member_claims,
            tokens=tokens
        )


    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰"
        )
    
    return 


    