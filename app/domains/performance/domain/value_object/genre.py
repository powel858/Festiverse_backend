from enum import Enum


class Genre(str, Enum):
    THEATER = "AAAA"         # 연극
    MUSICAL = "AAAB"         # 뮤지컬
    CLASSICAL = "CCCA"       # 서양음악(클래식)
    KOREAN_MUSIC = "CCCB"    # 한국음악(국악)
    POPULAR_MUSIC = "CCCD"   # 대중음악
    DANCE = "BBBC"           # 무용
    POPULAR_DANCE = "BBBE"   # 대중무용
    CIRCUS_MAGIC = "EEEA"    # 서커스/마술
    COMPLEX = "EEEB"         # 복합
    KIDS = "KID"             # 아동
