from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.infrastructure.oracle import get_oracle_db
# DTO, VO, Query, DB session

from sqlalchemy import select, update, insert, delete
from app.models.member_model import Member
from app.schemas.member_schema import (
    MemberCreateDTO, SocialMemberCreateDTO, MemberUpdateDTO, MemberClaimsDTO
)
from app.queries.member_query import (
    EXISTS_MEMBER_QUERY, CREATE_MEMBER_QUERY, 
    FIND_MEMBER_BY_EMAIL_AND_PROVIDER_QUERY, FIND_MEMBER_BY_ID_QUERY,
    FIND_MEMBERS_QUERY, UPDATE_MEMBER_QUERY, DELETE_MEMBER_QUERY
)

class MemberRepository:

    # 생성자 주입
    def __init__(self, db: AsyncSession):
        self.db = db

    # 이메일 중복 검사
    async def exists_member(self, member_email: str, member_provider: str) -> bool:
        # 1) query 직접 작성
        # result = await self.db.execute(EXISTS_MEMBER_QUERY, {
        #     "member_email": member_email,
        #     "member_provider": member_provider
        # })

        # count = result.scalar_one()
        # return count > 0
    
        # 2) ORM Core
        query = select(Member).where(
            Member.member_email == member_email,
            Member.member_provider == member_provider
        )

        result = await self.db.execute(query)
        found_member = result.scalar_one_or_none()
        return found_member is not None

    # 회원가입
    async def create_member(self, member: MemberCreateDTO) -> MemberClaimsDTO:
        # 1) Query 직접 작성
        new_member = {
            "member_email": member.member_email,
            "member_password": member.member_password,
            "member_name": member.member_name,
            "member_age": member.member_age,
            "member_picture": member.member_picture,
            "member_provider": member.member_provider
        }

        # await self.db.execute(CREATE_MEMBER_QUERY, new_member)
        # await self.db.commit()

        # result = await self.db.execute(FIND_MEMBER_BY_EMAIL_AND_PROVIDER_QUERY, {
        #     "member_email": member.member_email,
        #     "member_provider": member.member_provider
        # })
        
        # # 한 행 데이터
        # found_member = result.fetchone()
        # member_claim = MemberClaimsDTO(
        #     id = found_member.id,
        #     member_email=found_member.member_email,
        #     member_provider=found_member.member_provider
        # )

        # print("member_claim", member_claim)
        # return member_claim

        # 2) Core 방식
        query = (
            insert(Member)
            .values(**new_member)
            .returning(
                Member.id,
                Member.member_email,
                Member.member_provider
            )
        )

        result = await self.db.execute(query)
        await self.db.commit()

        id, member_email, member_provider = result.first()
        member_claim = MemberClaimsDTO(
            id = id,
            member_email=member_email,
            member_provider=member_provider
        )
        return member_claim
    

    # 소셜 회원가입
    async def create_social_member(self, member: SocialMemberCreateDTO) -> MemberClaimsDTO:
        new_member = {
            "member_email": member.member_email,
            "member_name": member.member_name,
            "member_age": member.member_age,
            "member_picture": member.member_picture,
            "member_provider": member.member_provider
        }

        query = (
            insert(Member)
            .values(**new_member)
            .returning(
                Member.id,
                Member.member_email,
                Member.member_provider
            )
        )

        result = await self.db.execute(query)
        await self.db.commit()

        id, member_email, member_provider = result.first()
        member_claim = MemberClaimsDTO(
            id = id,
            member_email=member_email,
            member_provider=member_provider
        )
        return member_claim

    
    # 회원 정보 전체 조회(관리자)
    async def find_members(self):
      # 1) 직접 작성
      # result = await self.db.execute(FIND_MEMBERS_QUERY)
      # members = result.mappings().all()
      # return members

      # 2) Core 방식
      query = select(Member)
      result = await self.db.execute(query)
      members = result.scalars().all()
      return members
    
    # 회원 정보 조회(id)
    async def find_member_by_id(self, id: int) -> Member | None:
        # 1) 직접 작성
        # result = await self.db.execute(FIND_MEMBER_BY_ID_QUERY, {
        #     "id": id
        # })

        # # mappings: Member -> Dict key-value 매핑
        # found_member = result.mappings().one_or_none()
        # return found_member

        # 2) Core 방식
        query = select(Member).where(Member.id == id)
        result = await self.db.execute(query, {
            "id": id
        })

        found_member = result.scalar_one_or_none()
        return found_member

    # 회원 정보 조회(email, provider)
    async def find_member_by_email_and_provider(self, member_email: str, member_provider: str) -> Member | None:
        # 1) 직접 작성
        result = await self.db.execute(FIND_MEMBER_BY_EMAIL_AND_PROVIDER_QUERY, {
          "member_email": member_email,
          "member_provider": member_provider  
        })

        # # mappings: Member -> Dict key-value 매핑
        # found_member = result.mappings().one_or_none()
        # return found_member

        # 2) Core 방식
        query = select(Member).where(
            Member.member_email == member_email,
            Member.member_provider == member_provider
        )
        result = await self.db.execute(query, {
            "member_email": member_email,
            "member_provider": member_provider
        })

        found_member = result.scalar_one_or_none()
        return found_member
    

    # 회원 정보 수정
    async def update_member(self, id: int, member: MemberUpdateDTO) -> bool:
        # 1) 직접 작성
        # result = self.db.execute(UPDATE_MEMBER_QUERY, {
        #     "id": id,
        #     "member_name": Member.member_name,
        #     "member_age": Member.member_age,
        #     "member_password": Member.member_password
        # })

        # await self.db.commit()
        # return result.rowcount() > 0

        # 2) Core
        new_data = {
            "id": id,
            "member_name": Member.member_name,
            "member_age": Member.member_age,
            "member_password": Member.member_password
        }
        query = (
            update(Member)
            .where(Member.id == id)
            .values(**new_data)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount() > 0


    # 회원 탈퇴
    async def delete_member(self, id: int):
        # result = await self.db.execute(DELETE_MEMBER_QUERY, {
        #     "id": id
        # })
        # await self.db.commit()
        # return result.rowcount() > 0

        query = (
            delete(Member)
            .where(Member.id == id)
        )

        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount() > 0
    # 회원 썸네일 변경(S3)

# 주입 팩토리 메서드
def get_member_repository(db: AsyncSession = Depends(get_oracle_db)):
    return MemberRepository(db)