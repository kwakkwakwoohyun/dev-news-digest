"""FastAPI 앱 진입점.

지금은 하네스(테스트/린트/CI)가 제대로 동작하는지 확인하기 위한
최소 스켈레톤이다. 실제 /news 엔드포인트와 수집 파이프라인은
로드맵 1단계에서 이어서 구현한다.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI  # FastAPI 웹 프레임워크의 핵심 클래스

from db import create_db_and_tables
from models import NewsItem  # noqa: F401  # SQLModel 메타데이터에 테이블을 등록하기 위한 import


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    create_db_and_tables()
    yield


# FastAPI 앱 인스턴스 생성. title/description은 자동 생성되는 /docs 페이지에 표시된다.
app = FastAPI(
    title="Dev News Digest API",
    description="AI/LLM, 빅테크 블로그, 웹 트렌드 뉴스를 요약해서 제공하는 API",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """서버가 살아있는지 확인하는 헬스체크 엔드포인트.

    CI와 하네스 테스트(test_health.py)가 이 엔드포인트를 호출해서
    서버가 정상 기동되는지 자동으로 검증한다.
    """
    return {"status": "ok"}  # 단순히 상태만 반환
