import os
from dotenv import load_dotenv
from jose import jwt, JWTError
from app.schemas.member_schema import MemberClaimsDTO
from datetime import timedelta, datetime, timezone

# 환경변수 로드
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# 액세스 토큰 생성 함수
def generate_access_token(member_claims: MemberClaimsDTO) -> str:

    # .model_dump(): Class -> dict
    claims = member_claims.model_dump()

    # timedelta: 시간의 간격을 나타내는 객체
    # expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    expire = datetime.now(timezone.utc) + timedelta(days=1)

    access_token = jwt.encode({
        **claims,
        "exp": expire
    }, SECRET_KEY, algorithm=ALGORITHM)

    return access_token


def generate_refresh_token(member_claims: MemberClaimsDTO) -> str:

    # .model_dump(): Class -> dict
    claims = member_claims.model_dump()

    # timedelta: 시간의 간격을 나타내는 객체
    # expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    expire = datetime.now(timezone.utc) + timedelta(days=30)

    access_token = jwt.encode({
        **claims,
        "exp": expire
    }, SECRET_KEY, algorithm=ALGORITHM)

    return access_token


# 토큰 파싱 함수
def parse_token(token: str) -> MemberClaimsDTO:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    member_id = payload["id"]
    member_email = payload["member_email"]
    member_provider = payload["member_provider"]

    return MemberClaimsDTO(
        id=member_id,
        member_email=member_email,
        member_provider=member_provider
    )

# refresh_token -> access_token 재발급
def reissue_access_token(refresh_token: str) -> str:
    claims: MemberClaimsDTO = parse_token(refresh_token)
    new_access_token = generate_access_token(claims)
    
    return new_access_token