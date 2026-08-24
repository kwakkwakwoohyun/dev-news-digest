# Dev News Digest

## 프로젝트 개요

개발자를 위한 뉴스 요약 웹 대시보드. AI/LLM 뉴스, 빅테크·스타트업 엔지니어링 블로그, 웹/앱 개발 트렌드를 여러 소스에서 자동으로 모아 Claude API로 짧게 요약해서 매일 훑어볼 수 있게 하는 게 목적이다.

만드는 목적은 두 가지다.

1. 개인적으로 매일 쓸 도구가 필요하다 (빠르게 기술 트렌드 습득).
2. 이걸 만들면서 실전 AI 앱 개발(수집 파이프라인, LLM 요약, 풀스택 배포)을 익힌다.

먼저 개인용 MVP로 만들어서 직접 2~3주 써보고, 실제로 유용하다고 느끼는 부분을 확인한 뒤에 수익화 가능성(유료 다이제스트, 팀용 B2B 버전 등)을 검토한다. **지금 단계에서는 수익화 관련 기능(결제, 멀티유저, 마케팅 페이지)을 만들지 않는다.** 개인용 MVP가 완성되고 실사용 검증이 끝나기 전까지는 스코프를 넓히지 않는다.

## 기술 스택

- 프론트엔드: Next.js (App Router) + TypeScript
- 백엔드: FastAPI (Python)
- DB: SQLite (개발 단계). 나중에 필요해지면 PostgreSQL로 이전 검토.
- 수집: `httpx` (HN Algolia API, Reddit API, GitHub Trending), `feedparser` (RSS 블로그)
- 요약: Anthropic Python SDK (Claude API)
- 스케줄러: 처음엔 APScheduler로 FastAPI 프로세스 안에서 주기 실행. 필요시 별도 cron 스크립트로 분리.

프론트를 Next.js+TypeScript로 정한 이유: 나중에 다른 사용자에게 열어줄 가능성을 열어두기 위해서(인증/결제/SEO 붙이기 쉬움), 그리고 이 조합이 현재 가장 널리 쓰이는 스택이라 바이브코딩 시 AI가 생성하는 코드의 정확도가 높다.

## 아키텍처

```
dev-news-digest/
├── backend/
│   ├── main.py              # FastAPI 앱 진입점, /health, /news 등 엔드포인트
│   ├── models.py            # DB 모델 (NewsItem 등, SQLModel 사용) — 예정
│   ├── db.py                # DB 연결/세션 설정 — 예정
│   ├── collectors/          # 예정
│   │   ├── hn.py            # Hacker News (Algolia API)
│   │   ├── blogs_rss.py     # 빅테크/스타트업 엔지니어링 블로그 RSS
│   │   └── github_trending.py
│   ├── summarizer.py        # Claude API로 요약 + 카테고리 태그 생성 — 예정
│   ├── scheduler.py         # 수집 파이프라인 주기 실행 — 예정
│   ├── tests/                # pytest 테스트 (하네스)
│   │   └── test_health.py
│   ├── pyproject.toml        # ruff/mypy/pytest 설정
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/                 # Next.js 프로젝트 (App Router, TypeScript) — 예정
├── .github/workflows/ci.yml  # push/PR마다 lint+typecheck+test 자동 실행
└── .claude/
    ├── settings.json         # Claude Code hooks 설정
    └── hooks/lint-check.sh   # 파일 수정 후 자동 린트 스크립트
```

백엔드와 프론트는 완전히 분리된 구조다. 백엔드는 `/news?category=ai|blog|trend` 형태로 JSON을 반환하는 REST API만 제공하고, 프론트는 이를 fetch해서 카테고리별로 보여준다.

## 데이터 소스 (카테고리별)

- **AI/LLM**: Hacker News(키워드 필터), r/MachineLearning, r/LocalLLaMA, arXiv cs.AI/cs.CL, Anthropic/OpenAI/Google AI 블로그 RSS
- **빅테크/스타트업 블로그**: Netflix, Uber, Airbnb, Stripe, Vercel, Cloudflare 등 엔지니어링 블로그 RSS
- **웹/앱 트렌드**: GitHub Trending, dev.to 인기글, 주요 프레임워크(React/Next.js/Vite 등) 릴리즈 노트

각 수집기는 24시간 이내 신규 항목만 가져오고, 중복은 제목/URL 기준으로 제거한다.

## 요약 파이프라인

수집 → 24시간 필터링 → 중복 제거 → Claude API로 항목당 다음 형식 생성 → DB 저장:

- `summary`: 1~2줄 요약
- `why_it_matters`: 왜 중요한지 한 줄 코멘트
- `category`: ai | blog | trend
- `tags`: 관련 스택/키워드

## 에이전트 하네스 (테스트/린트/훅/CI)

AI 코딩 에이전트(Claude Code)가 코드를 짤 때 사람이 매번 리뷰하지 않아도 실수를 스스로 잡아낼 수 있도록, 아래 안전장치를 프로젝트 초기부터 갖춰뒀다. 이걸 "에이전트 하네스"라고 부른다.

- **자동 테스트** (`backend/tests/`): pytest로 기능이 깨졌는지 검증. 지금은 `/health` 엔드포인트 테스트 1개만 있고, 새 기능을 만들 때마다 테스트를 같이 추가한다.
- **린트/타입체크** (`backend/pyproject.toml`): ruff(스타일/버그 패턴), mypy(타입 오류)를 로컬에서 `ruff check .` / `mypy .`로 직접 돌릴 수 있다.
- **Claude Code Hooks — PreToolUse (`.claude/hooks/require_comments.py`)**: Claude Code가 Edit/Write로 코드를 쓰기 *직전에* 새로 쓰이는 코드에 주석이 하나도 없으면 실행 자체를 막는다(`permissionDecision: deny`). Claude는 그 이유를 보고 주석을 추가해서 다시 시도한다. `.py`/`.ts`/`.tsx`/`.js`/`.jsx` 파일이 대상이고, 3줄 미만의 사소한 변경은 검사하지 않는다(스크립트 상단 `MIN_LINES_TO_CHECK`로 조절 가능).
- **Claude Code Hooks — PostToolUse (`.claude/hooks/lint-check.sh`)**: Edit/Write 직후 자동으로 `ruff check`를 실행해서 스타일 오류를 즉시 알려준다.
- **CI** (`.github/workflows/ci.yml`): GitHub에 push/PR할 때마다 ruff → mypy → pytest를 자동으로 돌려서, 로컬에서 놓친 문제를 병합 전에 잡아낸다. (GitHub 원격 저장소를 만들고 push해야 실제로 동작함)

새 기능(수집기, 요약 파이프라인 등)을 추가할 때는 해당 코드에 대한 테스트도 함께 작성하는 걸 원칙으로 한다.

## 개발 로드맵 (MVP 단계)

0. **0단계 (완료)**: 에이전트 하네스 구축 — backend 스켈레톤(`/health`), pytest, ruff/mypy 설정, CI, Claude Code hooks.
1. **1단계**: DB 스키마 + HN 수집기 하나만 연결 + `/news` 엔드포인트가 JSON 반환. 프론트는 최소한으로(리스트만 출력). 수집기/엔드포인트마다 테스트도 같이 작성.
2. **2단계**: Claude 요약 파이프라인 연결 (원문 → summary + why_it_matters + tag).
3. **3단계**: RSS 블로그 수집기, GitHub Trending 수집기 추가 (소스 다양화).
4. **4단계**: 대시보드 UI 다듬기(카테고리 필터, 정렬), APScheduler로 자동 주기 갱신.
5. **5단계 (검증 후)**: 2~3주 직접 사용 후 아쉬운 점 정리 → 수익화 방향(이메일/Slack 다이제스트 유료화, 팀용 B2B 등) 검토.

현재는 1단계부터 시작한다.

## 코딩 컨벤션

- 백엔드: 함수/변수는 snake_case, 타입 힌트 필수, Pydantic/SQLModel로 스키마 명시.
- 프론트엔드: 컴포넌트는 PascalCase, 가능한 한 서버 컴포넌트 우선 사용(App Router 기본), 클라이언트 컴포넌트는 필요한 곳에만.
- 환경변수(`ANTHROPIC_API_KEY` 등)는 `.env`로 관리하고 절대 커밋하지 않는다. `.env.example`만 커밋.
- 커밋은 기능 단위로 작게 나눈다.
- 이 프로젝트는 학습 목적도 겸하므로, 코드 작성 시 각 줄/블록에 무엇을 왜 하는지 설명하는 주석을 달아준다.
- 새 기능을 추가하면 그에 대한 pytest 테스트도 같이 작성한다 (하네스 유지).

## 실행 명령어

```
# backend 최초 세팅
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# 서버 실행
uvicorn main:app --reload

# 하네스 실행 (커밋 전 직접 돌려보기)
ruff check .
mypy .
pytest

# frontend (스캐폴딩 후 사용 예정)
cd frontend && npm run dev
```