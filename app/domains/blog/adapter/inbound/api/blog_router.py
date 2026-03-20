from fastapi import APIRouter, Depends

from app.domains.blog.adapter.outbound.external.naver_blog_adapter import NaverBlogAdapter
from app.domains.blog.adapter.outbound.persistence.performance_title_query import PerformanceTitleQuery
from app.domains.blog.application.response.blog_review_response import BlogReviewResponse
from app.domains.blog.application.usecase.search_blog_reviews_usecase import SearchBlogReviewsUseCase
from app.infrastructure.config.settings import settings
from app.infrastructure.database.session import async_session_factory
from app.infrastructure.external.http_client import get_http_client

router = APIRouter(prefix="/api", tags=["blogs"])


async def _get_usecase():
    client = await get_http_client()
    blog_adapter = NaverBlogAdapter(client, settings.NAVER_CLIENT_ID, settings.NAVER_CLIENT_SECRET)
    async with async_session_factory() as session:
        title_query = PerformanceTitleQuery(session)
        yield SearchBlogReviewsUseCase(blog_adapter, title_query)


@router.get("/performances/{mt20id}/blogs", response_model=list[BlogReviewResponse])
async def get_blog_reviews(
    mt20id: str,
    usecase: SearchBlogReviewsUseCase = Depends(_get_usecase),
) -> list[BlogReviewResponse]:
    return await usecase.execute(mt20id)
