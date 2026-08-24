"""backend/main.py의 /health 엔드포인트에 대한 테스트.

이 테스트가 '하네스'의 핵심 역할을 한다: 코드가 바뀔 때마다
서버가 정상적으로 뜨고 기본 엔드포인트가 응답하는지 자동으로 검증해서,
사람이 매번 수동으로 확인하지 않아도 실수를 잡아낼 수 있게 해준다.
"""

from fastapi.testclient import TestClient  # FastAPI 앱을 실제 서버 없이 테스트하는 클라이언트

from main import app  # 우리가 만든 FastAPI 앱 인스턴스 import

client = TestClient(app)  # 테스트용 클라이언트 생성


def test_health_check_returns_ok() -> None:
    """GET /health 요청이 200과 {'status': 'ok'}를 반환하는지 확인한다."""
    response = client.get("/health")  # /health 엔드포인트 호출
    assert response.status_code == 200  # HTTP 상태 코드가 200(성공)인지 확인
    assert response.json() == {"status": "ok"}  # 응답 본문이 예상값과 일치하는지 확인
