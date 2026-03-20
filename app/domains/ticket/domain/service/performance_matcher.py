import re
from dataclasses import dataclass


@dataclass
class MatchCandidate:
    title: str
    url: str


# 영어 불용어 (검색/매칭 시 노이즈가 되는 단어)
_STOPWORDS = frozenset({
    "the", "a", "an", "in", "on", "at", "to", "of", "for", "and", "or",
    "is", "it", "my", "no", "do", "be", "so", "up", "we", "he", "me",
    "by", "if", "as", "vs", "vol", "pt", "st", "nd", "rd", "th",
    "live", "tour", "concert",  # 공연 일반 용어도 제외
})


class PerformanceMatcher:
    """공연명과 검색 결과를 매칭하는 Domain Service (순수 Python)."""

    def __init__(self, threshold: float = 0.5) -> None:
        self._threshold = threshold

    def find_best_match(
        self, performance_name: str, candidates: list[MatchCandidate],
    ) -> MatchCandidate | None:
        """후보 목록에서 공연명과 가장 잘 매칭되는 결과를 반환한다."""
        keywords = self._extract_keywords(performance_name)
        if not keywords:
            return None

        year = self._extract_year(performance_name)
        region = self._extract_region(performance_name)

        best: MatchCandidate | None = None
        best_score = 0.0

        for candidate in candidates:
            # 연도가 있으면 필수 일치
            if year and year not in candidate.title:
                continue
            # 지역은 필수 일치이나, 검색 결과에 지역 없으면 통과
            if region and region not in candidate.title:
                # 검색 결과에 아무 지역도 없으면 pass
                if any(r in candidate.title for r in
                       ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "제주", "수원", "고양"]):
                    continue

            score = self._calc_keyword_score(keywords, candidate.title)
            if score >= self._threshold and score > best_score:
                best_score = score
                best = candidate

        return best

    @staticmethod
    def extract_search_query(name: str) -> str:
        """공연명에서 검색에 적합한 쿼리를 추출한다."""
        # 대괄호/소괄호 내용 제거 (지역, 영어 부제 등)
        cleaned = re.sub(r"\[[^\]]*\]", "", name)
        cleaned = re.sub(r"\([^)]*\)", "", cleaned)
        # 특수문자를 공백으로
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @staticmethod
    def _extract_keywords(name: str) -> list[str]:
        """공연명에서 핵심 키워드를 추출한다."""
        # 괄호와 괄호 안 내용 제거
        cleaned = re.sub(r"[(\[<（【《][^)\]>）】》]*[)\]>）】》]", "", name)
        # 특수문자 제거, 공백 분리
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)
        tokens = cleaned.split()
        keywords = []
        for t in tokens:
            # 1글자 토큰 제거
            if len(t) <= 1:
                continue
            # 영어 불용어 제거
            if t.lower() in _STOPWORDS:
                continue
            # 숫자만으로 된 토큰(연도 제외)은 제거
            if t.isdigit() and len(t) != 4:
                continue
            keywords.append(t)
        return keywords

    @staticmethod
    def _extract_year(name: str) -> str | None:
        """공연명에서 연도(4자리)를 추출한다."""
        match = re.search(r"(20\d{2})", name)
        return match.group(1) if match else None

    @staticmethod
    def _extract_region(name: str) -> str | None:
        """공연명에서 주요 지역명을 추출한다."""
        regions = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "제주", "수원", "고양"]
        for region in regions:
            if region in name:
                return region
        return None

    @staticmethod
    def _calc_keyword_score(keywords: list[str], title: str) -> float:
        """키워드가 제목에 포함된 비율을 계산한다 (대소문자 무시)."""
        if not keywords:
            return 0.0
        title_lower = title.lower()
        matched = sum(1 for kw in keywords if kw.lower() in title_lower)
        return matched / len(keywords)
