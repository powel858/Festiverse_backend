from dataclasses import dataclass


@dataclass
class BlogPost:
    title: str
    link: str
    description: str
    bloggername: str
    postdate: str
