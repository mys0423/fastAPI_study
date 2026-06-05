from fastapi import Depends, HTTPException
from app.utils.security_util import get_password_hash
from app.repositories.member_repository import MemberRepository, get_member_repository
from app.schemas.member_schema import (
    MemberCreateDTO, SocialMemberCreateDTO, MemberUpdateDTO, MemberClaimsDTO, MemberResponseDTO
)

# 1. 트랜잭션 관리
# 2. 비즈니스 핵심 로직 설계
# 3. 예외 처리
class MemberService:
    def __init__(self, repo:MemberRepository = Depends(get_member_repository)):
        self.repo = repo

    # 이메일 중복확인
    async def check_duplicate_member(self, member_email: str, member_provider: str) -> None:
        result = await self.repo.exists_member(member_email, member_provider) 

        if result:
            raise HTTPException(
                status_code=409,
                detail="이미 존재하는 이메일입니다."
            )

    # 로컬 회원 가입
    async def join(self, member: MemberCreateDTO) -> MemberClaimsDTO:

        # 중복검사
        await self.check_duplicate_member(member.member_email, member.member_provider)

        # 비밀번호
        encrpyted_password = get_password_hash(member.member_password)
        member.member_password = encrpyted_password

        new_member = MemberCreateDTO(
            member_email=member.member_email,
            member_password=encrpyted_password,
            member_name=member.member_name,
            member_age=member.member_age,
            member_provider=member.member_provider
        )

        member_in_db = await self.repo.create_member(new_member)
        return member_in_db

    
    # 소셜 로그인과 회원가입
    async def social_login_or_create(self, social_member: SocialMemberCreateDTO):

        member_in_db = await self.repo.find_member_by_email_and_provider(
            social_member.member_email,
            social_member.member_provider
        )

        if not member_in_db:
            member_in_db = await self.repo.create_social_member(social_member)
            
        return member_in_db


    # 회원 정보 조회(id)
    async def get_member_by_id(self, id: int):
        found_member = await self.repo.find_member_by_id(id)

        if not found_member:
            raise HTTPException(
                status_code=404,
                detail="회원을 찾을 수 없습니다"
            )

        # ORM Member -> MemberResponseDTO
        return MemberResponseDTO.model_validate(found_member)


    # 회원 정보 조회(member_email, member_provider)
    async def get_member_for_login(self, member_email: str, member_provider: str):
        found_member = await self.repo.find_member_by_email_and_provider(member_email, member_provider)

        if not found_member:
            raise HTTPException(
                status_code=404,
                detail="회원을 찾을 수 없습니다"
            )

        # ORM Member -> MemberResponseDTO
        return found_member

    # 회원 정보 조회(member_email, member_provider)
    async def get_member_by_email_and_provider(self, member_email: str, member_provider: str):
        found_member = await self.repo.find_member_by_email_and_provider(member_email, member_provider)

        if not found_member:
            raise HTTPException(
                status_code=404,
                detail="회원을 찾을 수 없습니다"
            )

        # ORM Member -> MemberResponseDTO
        return MemberResponseDTO.model_validate(found_member)

    # 회원 전체 조회
    async def get_members(self):
        members = await self.repo.find_members()

        return [MemberResponseDTO.model_validate(member) for member in members]

    # 회원 정보 수정
    async def update_member(self, id: int, member: MemberUpdateDTO) -> None:
        updated_member = MemberUpdateDTO(
            member_name=member.member_name,
            member_age=member.member_age
        )

        is_updated = await self.repo.update_member(id, updated_member)
        if not is_updated:
            raise HTTPException(
                status_code=404,
                detail="회원이 존재하지 않습니다."
            )

    # 회원 비밀번호 변경
    async def update_password(self, id: int, member_password: str) -> None:
        encrypted_password = get_password_hash(member_password)
        is_updated = await self.repo.update_password(id, encrypted_password)

        if not is_updated:
            raise HTTPException(
                status_code=404,
                detail="회원이 존재하지 않습니다."
            )

    # 회원 이미지 수정S3




    # 회원 탈퇴
    async def withdraw(self, id: int):
        is_deleted = await self.repo.delete_member(id)
        
        if not is_deleted:
            raise HTTPException(
                status_code=404,
                detail="회원이 존재하지 않습니다."
            )

def get_member_service(repo: MemberRepository = Depends(get_member_repository)):
    return MemberService(repo)
