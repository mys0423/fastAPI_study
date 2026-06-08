from fastapi import Depends, HTTPException, status
from app.models.post_model import Post
from app.repositories.post_repository import get_post_repository, PostRepository
from app.schemas.post_schema import (
    PostCreateDTO, PostDetailResponseDTO, PostListResponseDTO, PostUpdateDTO
)

from sqlalchemy import select, update, insert, delete

class PostService:

    def __init__(self, repo: PostRepository):
        self.repo = repo

    # 게시글 작성
    async def write_post(self, member_id: int, post: PostCreateDTO) -> int:
        new_post_id = await self.repo.create_post(member_id, post);
        return new_post_id


    # 게시글 단일 조회
    async def read_post(self, post_id: int) -> PostDetailResponseDTO:
        found_post = await self.repo.find_post(post_id)

        if found_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )

        return PostDetailResponseDTO.model_validate(found_post) 
    

    # 게시글 전체 조회
    async def read_posts(self) -> list[PostListResponseDTO]:
        found_posts = await self.repo.find_posts()
        
        if found_posts is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )
        
        return [
            PostDetailResponseDTO.model_validate(found_post)
            for found_post in found_posts
        ]


    # 게시글 수정
    async def edit_post(self, post_id: int, post: PostUpdateDTO) -> None:
        is_edit = await self.repo.update_post(post_id, post)

        if not is_edit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글이 수정되지 않았습니다."
            )
        
    
    # 게시글 삭제
    async def remove_post(self, post_id: int):
        id_remove = await self.repo.delete_post(post_id)

        if not id_remove:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글이 존재하지 않습니다."
            )
        

def get_post_service(repo: PostRepository = Depends(get_post_repository)):
    return PostService(repo)

