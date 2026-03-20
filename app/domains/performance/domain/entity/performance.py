from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Performance:
    mt20id: str
    prfnm: str                          # 공연명
    prfpdfrom: str = ""                  # 공연시작일 (YYYY.MM.DD)
    prfpdto: str = ""                    # 공연종료일
    fcltynm: str = ""                    # 공연시설명
    prfcast: str = ""                    # 출연진
    prfcrew: str = ""                    # 제작진
    prfruntime: str = ""                 # 런타임
    prfage: str = ""                     # 관람연령
    pcseguidance: str = ""               # 티켓가격
    poster: str = ""                     # 포스터 URL
    genrenm: str = ""                    # 장르명
    prfstate: str = ""                   # 공연상태
    openrun: str = ""                    # 오픈런 여부
    styurls: list[str] = field(default_factory=list)  # 소개이미지 URL 목록
    relates: list[dict[str, str]] = field(default_factory=list)  # 예매 링크 [{name, url}]
    dtguidance: str = ""                 # 공연시간
    area: str = ""                       # 지역
    mt10id: str = ""                     # 공연시설 ID
    festival: str = ""                   # 축제 여부 (Y/N)
    sty: str = ""                        # 줄거리
    updated_at: datetime | None = None   # 마지막 갱신 시각
