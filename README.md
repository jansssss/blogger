# 건강한 100세를 위해

건강/바이오 단일 테마용 Blogger 자동 글 생성기입니다. 주제 목록(`data/topics.csv`)에서 아직 사용하지 않은 항목을 하나 고르고, 카드형 HTML 미리보기를 만든 뒤 Blogger 초안 또는 게시 상태로 전송할 수 있습니다.

## 구성

- `data/topics.csv`: 글 주제 큐
- `prompts/health_article_prompt.txt`: 글 구조와 톤 가이드
- `src/topic_queue.py`: 다음 주제 선택과 상태 갱신
- `src/generate_post.py`: 글 데이터 생성
- `src/render_html.py`: Blogger용 HTML 렌더링
- `src/blogger_client.py`: Blogger REST API 업로드
- `src/main.py`: CLI 진입점

## 빠른 시작

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m src.main list-topics
python -m src.main preview
```

미리보기 결과는 `output/previews/` 아래에 저장됩니다.

## 환경 변수

`.env`에 아래 값을 넣습니다.

- `BLOG_THEME_NAME`: 기본 테마 이름
- `OPENAI_API_KEY`: 선택. 없으면 템플릿 기반으로 글 생성
- `OPENAI_MODEL`: 선택. 기본값 `gpt-5-mini`
- `BLOGGER_BLOG_ID`: Blogger 블로그 ID
- `BLOGGER_ACCESS_TOKEN`: 선택. 단기 테스트용 액세스 토큰
- `BLOGGER_REFRESH_TOKEN`: 장기 자동화를 위한 리프레시 토큰
- `GOOGLE_CLIENT_ID`: OAuth 클라이언트 ID
- `GOOGLE_CLIENT_SECRET`: OAuth 클라이언트 시크릿
- `BLOGGER_PUBLISH_MODE`: `draft` 또는 `publish`

## 기본 워크플로

1. `data/topics.csv`에 주제 60개를 넣습니다.
2. `python -m src.main preview`로 다음 글의 HTML을 확인합니다.
3. 문제가 없으면 `python -m src.main publish --topic-id hb-001`처럼 Blogger로 전송합니다.
4. 게시가 성공하면 해당 주제의 상태가 `published`로 바뀝니다.

## GitHub Actions

`.github/workflows/daily-blogger-post.yml`이 포함되어 있습니다. 저장소 Secrets에 아래 값을 넣으면 매일 자동으로 동작시킬 수 있습니다.

- `BLOG_THEME_NAME`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `BLOGGER_BLOG_ID`
- `BLOGGER_ACCESS_TOKEN`
- `BLOGGER_REFRESH_TOKEN`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `BLOGGER_PUBLISH_MODE`

기본 스케줄은 UTC `22:00`이며, 한국 시간 기준 오전 `07:00`입니다.

## 권장 운영 방식

- 초기에는 `BLOGGER_PUBLISH_MODE=draft`로 운영
- 장기 운영은 `BLOGGER_ACCESS_TOKEN` 단독보다 `BLOGGER_REFRESH_TOKEN + GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET` 조합 권장
- 건강/바이오 주제는 과장 표현과 치료 단정 표현을 피하도록 프롬프트 유지
- 실제 자동화는 로컬 검증 뒤 GitHub Actions로 옮기기
