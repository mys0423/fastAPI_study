from pydantic import BaseModel
from app.enums.member_enum import MemberProvider
from app.schemas.member_schema import MemberClaimsDTO

# DTO
class JwtTokenDTO(BaseModel):
  access_token: str | None = None
  refresh_token: str | None = None

class LoginRequestDTO(BaseModel):
  member_email: str  
  member_password: str  
  member_provider: MemberProvider | None = None

class SocialLoginRequestDTO(BaseModel):
  member_email: str  
  member_name: str | None = None  
  member_age: str | None = None  
  member_picture: str | None = None  
  member_provider_id: str | None = None  
  member_provider: MemberProvider | None = None

class AuthContextDTO(BaseModel):
  tokens: JwtTokenDTO
  member_claims: MemberClaimsDTO