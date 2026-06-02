from fastapi import APIRouter, Depends
from app.repositories.member_repository import get_member_repository
from app.schemas.member_schema import MemberCreateDTO, MemberUpdateDTO, MemberClaimsDTO
from app.schemas.common_schema import ApiResponseDTO
from app.enums.member_enum import MemberProvider

# router가 하나의 EndPoint가 됨
router = APIRouter()

# /members/*

@router.post(
    "/join",
    summary="로컬 회원가입"
)
def join():
    pass

@router.post(
    "/test",
    summary="레포지토리 테스트"
    
)
async def test(
    id: int,
    member_repository = Depends(get_member_repository)
):
    await member_repository.find_member_by_id(id)

