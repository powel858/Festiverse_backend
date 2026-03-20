from enum import Enum


class PerformanceState(str, Enum):
    UPCOMING = "01"      # 공연예정
    RUNNING = "02"       # 공연중
    COMPLETED = "03"     # 공연완료
