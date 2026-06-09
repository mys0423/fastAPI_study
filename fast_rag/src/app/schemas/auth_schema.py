from pydantic import BaseModel
from app.schemas.member_schema import MemberClaimsDTO

# DTO
class JwtTokenDTO(BaseModel):
  access_token: str | None = None
  refresh_token: str | None = None

class AuthContextDTO(BaseModel):
  tokens: JwtTokenDTO
  member_claims: MemberClaimsDTO