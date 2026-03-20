from abc import ABC, abstractmethod

from app.domains.blog.domain.entity.blog_post import BlogPost


class BlogSearchPort(ABC):

    @abstractmethod
    async def search(self, query: str, display: int = 3) -> list[BlogPost]:
        ...
