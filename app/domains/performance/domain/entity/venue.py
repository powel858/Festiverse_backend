from dataclasses import dataclass


@dataclass
class Venue:
    mt10id: str                          # 공연시설 ID
    fcltynm: str = ""                    # 공연시설명
    mt13cnt: int = 0                     # 공연장 수
    fcltychartr: str = ""                # 시설특성
    opende: str = ""                     # 개관연도
    seatscale: int = 0                   # 객석수
    telno: str = ""                      # 전화번호
    relateurl: str = ""                  # 홈페이지
    adres: str = ""                      # 주소
    la: float = 0.0                      # 위도
    lo: float = 0.0                      # 경도
    parkinglot: str = ""                 # 주차시설
    restaurant: str = ""                 # 레스토랑
    cafe: str = ""                       # 카페
    store: str = ""                      # 편의점
    nolibang: str = ""                   # 놀이방
    suyu: str = ""                       # 수유실
    disability: str = ""                 # 장애시설
