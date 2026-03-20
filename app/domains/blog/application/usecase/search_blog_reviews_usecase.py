from app.domains.blog.application.port.blog_search_port import BlogSearchPort
from app.domains.blog.application.port.performance_title_query_port import PerformanceTitleQueryPort
from app.domains.blog.application.response.blog_review_response import BlogReviewResponse


class SearchBlogReviewsUseCase:

    def __init__(
        self,
        blog_search_port: BlogSearchPort,
        title_query_port: PerformanceTitleQueryPort,
    ) -> None:
        self._blog_search = blog_search_port
        self._title_query = title_query_port

    async def execute(self, mt20id: str) -> list[BlogReviewResponse]:
        title = await self._title_query.get_title(mt20id)
        if not title:
            return []

        posts = await self._blog_search.search(query=title, display=3)

        return [
            BlogReviewResponse(
                title=post.title,
                link=post.link,
                description=post.description,
                bloggername=post.bloggername,
                postdate=post.postdate,
            )
            for post in posts
        ]
