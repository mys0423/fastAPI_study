from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.infrastructure.oracle import get_oracle_db

from sqlalchemy import select, update, insert, delete, func
from sqlalchemy.orm import joinedload
from app.models.post_model import Post
from app.schemas.post_schema import (
  PostCreateDTO, PostDetailResponseDTO, PostListResponseDTO, PostUpdateDTO
)

class PostRepository:

  def __init__(self, db: AsyncSession):
    self.db = db

  # 게시글 작성
  async def create_post(self, member_id, post: PostCreateDTO):

    new_post = {
      "post_title": post.post_title,
      "post_content": post.post_content,
      "member_id": member_id
    }

    query = (
      insert(Post)
      .values(**new_post)
      .returning(Post.id)
    )

    result = await self.db.execute(query)
    await self.db.commit()

    new_post_id = result.scalar_one()
    return new_post_id

  # 게시글 전체 조회
  async def find_posts(self) -> list[PostListResponseDTO]:
    query = select(Post).options(joinedload(Post.member))
    result = await self.db.execute(query)
    return result.scalars().all()
  
  # 게시글 1개 조회
  async def find_post(self, post_id: int) -> PostDetailResponseDTO:
    query = (
      select(Post)
      .options(joinedload(Post.member))
      .where(Post.id == post_id)
    )

    result = await self.db.execute(query)
    return result.scalar_one_or_none()
  
  # 게시글 수정
  async def update_post(self, post_id: int, post: PostUpdateDTO) -> bool:
    
    update_data = post.model_dump(exclude_unset=True)
    update_data["post_updated_at"] = func.now()

    query = (
      update(Post)
      .where(Post.id == post_id)
      .values(**update_data)
    )

    result = await self.db.execute(query)
    await self.db.commit()
    return result.rowcount > 0
  
  # 게시글 삭제
  async def delete_post(self, post_id):
    query = (
      delete(Post)
      .where(Post.id == post_id)
    )

    result = await self.db.execute(query)
    await self.db.commit()
    return result.rowcount > 0
  
def get_post_repository(db: AsyncSession = Depends(get_oracle_db)):
  return PostRepository(db)