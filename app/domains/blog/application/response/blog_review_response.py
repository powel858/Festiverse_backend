from pydantic import BaseModel


class BlogReviewResponse(BaseModel):
    title: str
    link: str
    description: str
    bloggername: str
    postdate: str
