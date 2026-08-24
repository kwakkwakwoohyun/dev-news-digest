"""DB 모델 정의.

수집기가 가져온 뉴스 항목과 Claude 요약 결과를 저장하는 NewsItem 테이블.
"""

from datetime import datetime

from sqlmodel import Field, SQLModel


class NewsItem(SQLModel, table=True):
    """수집된 뉴스 항목 하나를 나타내는 테이블.

    summary/why_it_matters/tags는 요약 파이프라인(summarizer.py)이
    채우기 전까지는 비어 있을 수 있다.
    """

    id: int | None = Field(default=None, primary_key=True)
    title: str
    url: str = Field(unique=True, index=True)
    source: str  # 예: "hn", "github_trending", "netflix_blog"
    category: str  # ai | blog | trend
    published_at: datetime
    collected_at: datetime = Field(default_factory=datetime.utcnow)

    summary: str | None = None
    why_it_matters: str | None = None
    tags: str | None = None  # 쉼표로 구분된 키워드 문자열
