from pydantic import BaseModel
from datetime import datetime
from app.enums.member_enum import MemberProvider

# VO
class MemberVO(BaseModel):
    id: int
    member_email: str
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_picture: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider | None = None
    member_created_at: datetime | None = None

# DTO
class MemberCreateDTO(BaseModel):
    member_email: str
    member_password: str | None = None
    member_name: str | None = None
    member_age: int | None = None
    member_picture: str | None = "/members/default.jpg"
    member_provider: MemberProvider | None = None
    member_created_at: datetime | None = None

# 소셜용
class SocialMemberCreateDTO(BaseModel):
    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_picture: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider | None = None
    member_created_at: datetime | None = None

class MemberUpdateDTO(BaseModel):
    member_name: str | None = None
    member_age: int | None = None

class PasswordUpdateDTO(BaseModel):
    member_password: str

# 응답용
class MemberResponseDTO(BaseModel):
    id: int
    member_email: str
    member_name: str | None = None
    member_age: int | None = None
    member_picture: str | None = "/members/default.jpg"
    member_provider_id: str | None = None
    member_provider: MemberProvider | None = None
    member_created_at: datetime | None = None

    # ORM -> DTO
    class Config:
        from_attributes = True

# 토큰용
class MemberClaimsDTO(BaseModel):
    id: int
    member_email: str
    member_provider: MemberProvider | None = None

# 게시판용
class MemberSummaryDTO(BaseModel):
    member_email: str
    member_name: str | None = None
    member_picture: str | None = "/members/default.jpg"

    # ORM -> DTO
    class Config:
        from_attributes = True

