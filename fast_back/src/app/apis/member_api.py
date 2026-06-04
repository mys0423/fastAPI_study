from fastapi import APIRouter, Depends, Query
from app.schemas.member_schema import MemberCreateDTO, MemberUpdateDTO, MemberClaimsDTO, PasswordUpdateDTO
from app.schemas.common_schema import ApiResponseDTO
from app.enums.member_enum import MemberProvider
from app.services.member_service import get_member_service, MemberService

router = APIRouter()

# 회원 가입 api
# swagger
@router.post(
    "/join",
    summary="로컬 회원가입",
    response_model=ApiResponseDTO,
    responses={
        409: {
            "description": "중복된 이메일(또는 아이디)로 회원가입 시도",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "이미 존재하는 이메일(아이디)입니다."
                    }
                }
            }
        }
    }
)
async def join(
    member: MemberCreateDTO,
    member_service: MemberService = Depends(get_member_service),
):
    member.member_provider = MemberProvider.LOCAL.value
    member_claim = await member_service.join(member)

    return ApiResponseDTO(
        success=True,
        message="회원가입 성공",
        data=member_claim
    )

# 회원 단일 조회(id)
@router.get(
    "/{id}",
    response_model=ApiResponseDTO,
    summary="회원 정보 조회(id)"
)
async def get_member_by_id(
    id: int,
    member_service: MemberService = Depends(get_member_service)
):
    found_member = await member_service.get_member_by_id(id)
    return ApiResponseDTO(
        success=True,
        message="회원 조회 성공",
        data=found_member
    )

# 회원 단일 조회(member_email, member_provider)
#Query(...): 필수 값
@router.get(
    "/",
    summary="회원 정보 조회(member_email, member_provider)",
    response_model=ApiResponseDTO
)
async def get_member_by_email_and_provider(
    member_email: str = Query(...),
    member_provider: str = Query(...),
    member_service: MemberService = Depends(get_member_service)
):
    found_member = await member_service.get_member_by_email_and_provider(member_email, member_provider)
    return ApiResponseDTO(
        success=True,
        message="회원 조회 성공",
        data=found_member
    )

# 회원 전체 조회
@router.get(
    "",
    summary="회원 전체 조회",
    response_model=ApiResponseDTO
)
async def get_members(
    member_service: MemberService = Depends(get_member_service)
):
    found_members = await member_service.get_members()
    return ApiResponseDTO(
        success=True,
        message="회원 전체 조회 성공",
        data=found_members
    )

# 회원 정보 수정
@router.put(
    "/{id}",
    summary="회원 정보 수정",
    response_model=ApiResponseDTO
)
async def update_member(
    id: int,
    member: MemberUpdateDTO,
    member_service: MemberService = Depends(get_member_service)
):
    await member_service.update_member(id, member)
    return ApiResponseDTO(
        success=True,
        message="회원 정보 수정 완료"
    )

# 회원 비밀번호 수정
@router.put(
    "/password/{id}",
    summary="회원 비밀번호 수정",
    response_model=ApiResponseDTO
)
async def update_password(
    id: int,
    new_password: str,
    member_service: MemberService = Depends(get_member_service)
):
    await member_service.update_password(id, new_password)
    return ApiResponseDTO(
        success=True,
        message="비밀번호 변경 성공"
    )

# 회원 정보 탈퇴
@router.delete(
    "/{id}",
    summary="회원 정보 탈퇴",
    response_model=ApiResponseDTO
)
async def withdraw(
    id: int,
    member_service: MemberService = Depends(get_member_service)
):
    await member_service.withdraw(id)
    return ApiResponseDTO(
        success=True,
        message="회원 탈퇴 성공"
    )

# 토큰 -> 회원 정보 조회 (TODO: JWT Security 의존성 추가 필요)
