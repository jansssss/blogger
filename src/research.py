from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError

from src.topic_queue import Topic


class OpenAIResearcher:
    API_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model

    def research(self, topic: Topic) -> str:
        query = f"{topic.title_hint} ({topic.angle}) - {', '.join(topic.keywords)}"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "당신은 대한민국 건강·의학 리서처입니다. "
                        "요청 주제에 대해 실제 통계 수치와 연구 결과를 기관명·연도 출처와 함께 한국어로 정리합니다. "
                        "불확실하거나 검증되지 않은 내용은 포함하지 않습니다."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"다음 건강 주제에 관한 최신 통계·연구·임상 수치를 수집해주세요.\n"
                        f"주제: {query}\n\n"
                        "요구사항:\n"
                        "- 구체적인 수치(%, mmHg, kg, 배율 등) 포함\n"
                        "- 출처 기관명과 발표 연도 반드시 포함\n"
                        "- 국내(질병관리청, 건강보험심사평가원, 국민건강영양조사 등) 및 "
                        "해외(WHO, AHA, NEJM 등) 자료 모두 수집\n"
                        "- 핵심 수치 위주로 간결하게 정리 (500자 내외)"
                    ),
                },
            ],
            "max_completion_tokens": 1000,
        }
        raw_body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.API_URL,
            data=raw_body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except HTTPError as e:
            body = e.read().decode("utf-8")
            raise RuntimeError(f"OpenAI HTTP {e.code}: {body}") from e
