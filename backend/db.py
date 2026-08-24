"""DB 연결/세션 설정.

개발 단계에서는 SQLite 파일 하나로 충분하다.
"""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./dev_news_digest.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """모델에 정의된 테이블이 없으면 생성한다."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용 세션 제너레이터."""
    with Session(engine) as session:
        yield session
