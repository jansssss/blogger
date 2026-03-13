from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import re
import unicodedata
from urllib import request

from src.topic_queue import Topic


@dataclass
class ArticleSection:
    heading: str
    paragraphs: list[str]


@dataclass
class Article:
    topic_id: str
    theme: str
    title: str
    subtitle: str
    summary_points: list[str]
    sections: list[ArticleSection]
    action_tips: list[str]
    tags: list[str]
    disclaimer: str
    published_label: str
    updated_label: str

    @property
    def slug(self) -> str:
        normalized = unicodedata.normalize("NFKD", self.title).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
        return f"{self.topic_id}-{slug}" if slug else self.topic_id

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["sections"] = [asdict(section) for section in self.sections]
        return payload


class ArticleGenerator:
    def __init__(self, theme_name: str, prompt_path: Path, openai_api_key: str | None, openai_model: str) -> None:
        self.theme_name = theme_name
        self.prompt_text = prompt_path.read_text(encoding="utf-8")
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model

    def build_article(self, topic: Topic) -> Article:
        if self.openai_api_key:
            try:
                return self._build_with_openai(topic)
            except Exception:
                return self._build_with_template(topic)
        return self._build_with_template(topic)

    def _build_with_template(self, topic: Topic) -> Article:
        now = datetime.now()
        title = topic.title_hint
        subtitle = (
            f"{topic.angle} 이라는 관점에서 {topic.target_reader}이 이해하기 쉽게 정리한 "
            f"'{self.theme_name}' 시리즈 글입니다."
        )
        summary_points = [
            f"{topic.title_hint}은 단일 성분보다 식사, 활동, 수면 같은 전체 습관과 함께 봐야 합니다.",
            f"{topic.target_reader}에게 중요한 관점은 '{topic.angle}'이며, 생활 맥락에서 접근해야 지속하기 쉽습니다.",
            f"핵심 키워드인 {', '.join(topic.keywords)}는 서로 연결되어 작동하므로 한 가지만 강조하면 균형을 잃기 쉽습니다.",
            "건강 정보는 개인 상태와 복용 약, 기존 질환에 따라 해석이 달라질 수 있습니다.",
            "실천은 작은 변화부터 시작하고, 증상이나 질환이 있다면 전문가 상담을 우선해야 합니다.",
        ]
        sections = [
            ArticleSection(
                heading=f"{title}를 왜 지금 챙겨야 할까",
                paragraphs=[
                    f"{topic.angle}라는 질문은 단순한 유행 정보가 아니라 중장기 건강 관리와 직접 연결됩니다. "
                    f"{topic.target_reader}에게는 현재 불편이 없더라도 미리 생활 패턴을 조정하는 접근이 중요합니다.",
                    f"특히 {', '.join(topic.keywords[:2])} 같은 요소는 서로 분리된 이슈가 아니라 몸의 회복력과 일상 기능에 함께 영향을 줄 수 있습니다.",
                ],
            ),
            ArticleSection(
                heading="생활 속에서 이해해야 할 핵심 포인트",
                paragraphs=[
                    f"이 주제를 볼 때는 {topic.must_include} 같은 조건을 염두에 두고 정보의 강도보다 지속 가능성을 먼저 따져야 합니다.",
                    "건강 관리에서 가장 흔한 실수는 한 가지 식품이나 보충제에 지나치게 기대는 것입니다. 실제로는 식사 균형, 활동량, 수면, 스트레스 관리가 함께 맞물려야 결과를 해석하기 쉽습니다.",
                ],
            ),
            ArticleSection(
                heading="무리하지 않고 실천하는 방법",
                paragraphs=[
                    f"{topic.target_reader}이라면 당장 복잡한 계획보다 하루 한 가지 습관부터 고정하는 편이 낫습니다. 예를 들어 일정한 취침 시간, 규칙적인 걷기, 단백질과 식이섬유를 고려한 식사 구성이 출발점이 될 수 있습니다.",
                    "실천 도중 몸 상태가 평소와 다르게 느껴지거나 기존 질환 관리와 충돌하는 부분이 있다면 스스로 결론을 내리기보다 전문가와 상의하는 편이 안전합니다.",
                ],
            ),
            ArticleSection(
                heading="마무리",
                paragraphs=[
                    f"{title}은 특별한 비법보다 기본 습관을 얼마나 오래 유지하느냐에 가까운 주제입니다. 단기간 효과보다 장기적인 생활 리듬을 만드는 데 초점을 두는 것이 더 현실적입니다.",
                ],
            ),
        ]
        action_tips = [
            "하루 1개 습관부터 시작하기",
            "주 1회 실천 기록 남기기",
            "과장 광고 문구는 한 번 더 의심하기",
            "기존 질환이 있으면 상담 후 적용하기",
        ]
        disclaimer = (
            "이 글은 일반적인 건강 정보 제공을 위한 콘텐츠입니다. 개인의 질환, 복용 약, 검사 결과에 따라 "
            "적용 방법이 달라질 수 있으므로 치료나 복용 결정은 의료 전문가와 상담해 판단해야 합니다."
        )
        published_label = f"{now.year}년 {now.month}월"
        updated_label = f"{now.year}년 {now.month}월 {now.day}일"
        return Article(
            topic_id=topic.id,
            theme=self.theme_name,
            title=title,
            subtitle=subtitle,
            summary_points=summary_points,
            sections=sections,
            action_tips=action_tips,
            tags=[self.theme_name, *topic.keywords],
            disclaimer=disclaimer,
            published_label=published_label,
            updated_label=updated_label,
        )

    def _build_with_openai(self, topic: Topic) -> Article:
        schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "health_blog_article",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "subtitle": {"type": "string"},
                        "summary_points": {"type": "array", "items": {"type": "string"}, "minItems": 5, "maxItems": 5},
                        "sections": {
                            "type": "array",
                            "minItems": 4,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "heading": {"type": "string"},
                                    "paragraphs": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
                                },
                                "required": ["heading", "paragraphs"],
                                "additionalProperties": False,
                            },
                        },
                        "action_tips": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 6},
                        "tags": {"type": "array", "items": {"type": "string"}, "minItems": 3},
                        "disclaimer": {"type": "string"},
                    },
                    "required": ["title", "subtitle", "summary_points", "sections", "action_tips", "tags", "disclaimer"],
                    "additionalProperties": False,
                },
            },
        }
        instructions = (
            f"{self.prompt_text}\n\n"
            f"주제: {topic.title_hint}\n"
            f"관점: {topic.angle}\n"
            f"대상 독자: {topic.target_reader}\n"
            f"핵심 키워드: {', '.join(topic.keywords)}\n"
            f"반드시 반영할 요소: {topic.must_include}"
        )
        payload = requests_post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": self.openai_model,
                "input": instructions,
                "text": {"format": schema},
            },
        )
        content_text = self._extract_output_text(payload)
        data = json.loads(content_text)
        now = datetime.now()
        return Article(
            topic_id=topic.id,
            theme=self.theme_name,
            title=data["title"],
            subtitle=data["subtitle"],
            summary_points=data["summary_points"],
            sections=[ArticleSection(**section) for section in data["sections"]],
            action_tips=data["action_tips"],
            tags=data["tags"],
            disclaimer=data["disclaimer"],
            published_label=f"{now.year}년 {now.month}월",
            updated_label=f"{now.year}년 {now.month}월 {now.day}일",
        )

    @staticmethod
    def _extract_output_text(payload: dict) -> str:
        if "output_text" in payload:
            return payload["output_text"]
        for item in payload.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if text:
                    return text
        raise ValueError("No output text found in OpenAI response payload.")


def requests_post(url: str, headers: dict[str, str], payload: dict) -> dict:
    raw_body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(url, data=raw_body, headers=headers, method="POST")
    with request.urlopen(http_request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))
