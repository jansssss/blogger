# 건강한 100세를 위해

건강/바이오 단일 테마용 Blogger 자동 글 생성기입니다. 주제 목록(`data/topics.csv`)에서 아직 사용하지 않은 항목을 하나 고르고, 카드형 HTML 미리보기를 만든 뒤 Blogger 초안 또는 게시 상태로 전송할 수 있습니다.



## 기본 워크플로

1. `data/topics.csv`에 주제 60개를 넣습니다.
2. `python -m src.main preview`로 다음 글의 HTML을 확인합니다.
3. 문제가 없으면 `python -m src.main publish --topic-id hb-001`처럼 Blogger로 전송합니다.
4. 게시가 성공하면 해당 주제의 상태가 `published`로 바뀝니다.



기본 스케줄은 UTC `22:00`이며, 한국 시간 기준 오전 `07:00`입니다.

## 권장 운영 방식

- 초기에는 `BLOGGER_PUBLISH_MODE=draft`로 운영
- 장기 운영은 `BLOGGER_ACCESS_TOKEN` 단독보다 `BLOGGER_REFRESH_TOKEN + GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET` 조합 권장
- 건강/바이오 주제는 과장 표현과 치료 단정 표현을 피하도록 프롬프트 유지
- 실제 자동화는 로컬 검증 뒤 GitHub Actions로 옮기기
