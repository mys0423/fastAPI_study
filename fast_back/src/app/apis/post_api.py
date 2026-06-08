from fastapi import APIRouter, Depends, Query
from app.schemas.common_schema import ApiResponseDTO
from app.schemas.post_schema import (
    PostCreateDTO, PostUpdateDTO, PostDetailResponseDTO, PostListResponseDTO
)
from app.services.post_service import PostService, get_post_service
from app.dependencies.auth_dependency import get_auth_context

router = APIRouter()

@router.post(
    "",
    response_model=ApiResponseDTO,
    summary="게시글 작성"
)
async def write_post(
    post: PostCreateDTO,
    post_service = Depends(get_post_service),
    auth_context = Depends(get_auth_context) # 보호된 라우트
):
    member_id = auth_context.member_claims.id
    new_post_id = await post_service.write_post(member_id, post)

    return ApiResponseDTO(
        success=True,
        message="게시글 작성 완료",
        data={
            new_post_id: new_post_id
        }
    )


@router.get(
    "/{id}",
    response_model=ApiResponseDTO,
    summary="게시글 조회"
)
async def read_post(
    id: int,
    post_service = Depends(get_post_service)
):
    found_post = await post_service.read_post(id)

    return ApiResponseDTO(
        success=True,
        message="게시글 조회 성공",
        data=found_post
    )


@router.get(
    "",
    response_model=ApiResponseDTO,
    summary="게시글 전체 조회"
)
async def read_post(
    post_service = Depends(get_post_service)
):
    found_posts = await post_service.read_posts()

    return ApiResponseDTO(
        success=True,
        message="게시글 조회 성공",
        data=found_posts
    )


@router.put(
    "/{id}",
    response_model=ApiResponseDTO,
    summary="게시글 수정"
)
async def register_member(
    id: int,
    post: PostUpdateDTO,
    post_service = Depends(get_post_service),
    auth_context = Depends(get_auth_context)
):
    await post_service.edit_post(id, post)

    return ApiResponseDTO(
        success=True,
        message="게시글 수정 완료"
    )



@router.delete(
    "/{id}",
    response_model=ApiResponseDTO,
    summary="게시글 삭제"
)
async def register_member(
    id: int,
    post_service = Depends(get_post_service),
    auth_context = Depends(get_auth_context)
):
    await post_service.remove_post(id)

    return ApiResponseDTO(
        success=True,
        message="게시글 삭제 완료"
    )

