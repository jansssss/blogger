from __future__ import annotations

import html
from pathlib import Path
from string import Template

from src.generate_post import Article

_FONT = "'Apple SD Gothic Neo', 'Malgun Gothic', 'Segoe UI', sans-serif"

# 쿠팡 파트너스 제휴 상품 정의
_AFFILIATE_PRODUCTS = [
    {
        "name": "단백질 보충제",
        "desc": "근감소 예방·근육 유지를 돕는 고흡수 단백질",
        "url": "https://link.coupang.com/a/eaqvqF",
        "keywords": {"단백질", "근육", "근감소", "아미노산", "근력운동", "근육합성", "근육회복", "근육식단", "근력", "근감소증"},
    },
    {
        "name": "오메가3",
        "desc": "혈관·뇌 건강을 지키는 EPA/DHA 오메가3",
        "url": "https://link.coupang.com/a/eaqxGL",
        "keywords": {"혈관건강", "혈압", "심혈관", "뇌건강", "신경가소성", "혈액순환", "탄력성"},
    },
    {
        "name": "관절 영양제",
        "desc": "무릎·연골 보호를 위한 글루코사민·콜라겐",
        "url": "https://link.coupang.com/a/eaqKPo",
        "keywords": {"무릎통증", "관절", "무릎보호", "저충격운동", "관절보호", "스트레칭", "유연성"},
    },
    {
        "name": "비타민D + 칼슘",
        "desc": "뼈 건강과 낙상 예방을 위한 비타민D·칼슘 복합",
        "url": "https://link.coupang.com/a/eaqLVY",
        "keywords": {"낙상예방", "균형감각", "면역력", "뼈", "골밀도", "노년운동", "고령근육"},
    },
    {
        "name": "마그네슘 · 수면 영양제",
        "desc": "수면의 질 개선과 스트레스 완화에 도움",
        "url": "https://link.coupang.com/a/eaqNVU",
        "keywords": {"수면질", "숙면", "우울증", "정신건강", "스트레스", "마그네슘"},
    },
]

_COUPANG_DISCLOSURE = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."


def _pick_products(tags: list[str]) -> list[dict]:
    """태그 키워드와 가장 많이 겹치는 상품 최대 2개 반환."""
    tag_set = set(tags)
    scored = [
        (product, len(tag_set & product["keywords"]))
        for product in _AFFILIATE_PRODUCTS
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    # 매칭 0이라도 최소 1개는 노출 (단백질이 기본)
    top = [p for p, score in scored[:2] if score > 0]
    if not top:
        top = [_AFFILIATE_PRODUCTS[0]]
    return top


def _build_cta_section(tags: list[str]) -> str:
    products = _pick_products(tags)
    cards = []
    for p in products:
        cards.append(
            # 카드 전체는 div — a 태그로 감싸면 Blogger가 텍스트 색상을 링크 색으로 덮어씀
            f'<div style="background:#ffffff; border:2px solid #dde6ff; border-radius:16px; '
            f'padding:20px 20px 18px; flex:1; min-width:260px; box-sizing:border-box;">'
            # 배지
            f'<div style="display:inline-block; background:#ebf0ff; color:#3268ff; font-family:{_FONT}; '
            f'font-size:11px; font-weight:700; padding:3px 10px; border-radius:99px; '
            f'margin-bottom:12px; letter-spacing:0.04em;">추천 영양제</div>'
            # 상품명
            f'<div style="font-family:{_FONT}; font-size:16px; font-weight:800; color:#1c2741; '
            f'margin-bottom:6px; line-height:1.4; word-break:keep-all;">{html.escape(p["name"])}</div>'
            # 설명
            f'<div style="font-family:{_FONT}; font-size:13px; color:#5a6a85; line-height:1.65; '
            f'word-break:keep-all; margin-bottom:18px;">{html.escape(p["desc"])}</div>'
            # CTA 버튼 (a 태그는 버튼에만)
            f'<a href="{p["url"]}" target="_blank" rel="noopener sponsored" '
            f'style="display:block; text-align:center; background:#ff5c42; color:#ffffff !important; '
            f'font-family:{_FONT}; font-size:14px; font-weight:700; padding:13px 0; '
            f'border-radius:10px; text-decoration:none !important; letter-spacing:0.01em;">쿠팡에서 구매하기 →</a>'
            f'</div>'
        )
    cards_html = "\n".join(cards)
    return (
        # 외부 래퍼 — 연한 그라데이션 배경으로 섹션 구분
        f'<div style="margin-top:48px; padding:24px 22px 20px; '
        f'background:linear-gradient(135deg,#f0f4ff 0%,#fff5f3 100%); border-radius:20px;">'
        # 상단 레이블
        f'<div style="font-family:{_FONT}; font-size:11px; font-weight:700; color:#3268ff; '
        f'letter-spacing:0.12em; margin-bottom:6px;">HEALTH SUPPLEMENT</div>'
        # 섹션 제목
        f'<div style="font-family:{_FONT}; font-size:18px; font-weight:800; color:#1c2741; '
        f'margin-bottom:18px; letter-spacing:-0.02em; line-height:1.4;">이 글과 함께 챙기면 좋은 영양제</div>'
        # 카드 그리드
        f'<div style="display:flex; flex-wrap:wrap; gap:14px;">'
        f'{cards_html}'
        f'</div>'
        # 쿠팡 파트너스 고지
        f'<p style="font-family:{_FONT}; font-size:11px; color:#aab3c6; margin:16px 0 0; '
        f'line-height:1.6; padding-top:14px; border-top:1px solid rgba(50,104,255,0.1);">'
        f'※ {html.escape(_COUPANG_DISCLOSURE)}</p>'
        f'</div>'
    )


class HtmlRenderer:
    def __init__(self, template_path: Path) -> None:
        self.template = Template(template_path.read_text(encoding="utf-8"))

    def render(self, article: Article) -> str:
        summary_items = "\n".join(
            f'<li style="font-family: {_FONT}; font-size: 15px; color: #2a3a5c; line-height: 1.7; margin-bottom: 8px; word-break: keep-all;">{html.escape(item)}</li>'
            for item in article.summary_points
        )

        section_parts = []
        for section in article.sections:
            paragraphs_html = "".join(
                f'<p style="font-family: {_FONT}; font-size: 16px; color: #3a4a62; margin: 0 0 14px; line-height: 1.9; word-break: keep-all;">{html.escape(paragraph)}</p>'
                for paragraph in section.paragraphs
            )
            insight_html = ""
            if section.expert_insight:
                insight_html = (
                    f'<div style="background: #f0f4ff; border-left: 4px solid #3268ff; border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 4px 0 20px;">'
                    f'<div style="font-family: {_FONT}; font-size: 12px; font-weight: 700; color: #3268ff; margin-bottom: 6px; letter-spacing: 0.04em;">전문가 인사이트</div>'
                    f'<p style="font-family: {_FONT}; font-size: 15px; color: #2a3a5c; margin: 0; line-height: 1.75; word-break: keep-all;">{html.escape(section.expert_insight)}</p>'
                    f'</div>'
                )
            section_parts.append(
                f"<section>"
                f'<h2 style="font-family: {_FONT}; font-size: 22px; font-weight: 800; color: #1c2741; margin: 40px 0 14px; padding-bottom: 8px; border-bottom: 2px solid #eef2f7; letter-spacing: -0.02em; line-height: 1.4; word-break: keep-all;">{html.escape(section.heading)}</h2>'
                + paragraphs_html
                + insight_html
                + "</section>"
            )
        section_items = "\n".join(section_parts)

        tip_items = "\n".join(
            f'<span style="display: inline-block; padding: 6px 14px; border-radius: 999px; background: #fff; border: 1.5px solid #ffcfc9; color: #cc3a28; font-size: 13px; font-weight: 600; line-height: 1.5; margin-bottom: 4px;">{html.escape(item)}</span>'
            for item in article.action_tips
        )
        tag_items = "\n".join(
            f'<span style="display: inline-block; padding: 6px 14px; border-radius: 999px; background: #fff; border: 1.5px solid #bdd0ff; color: #2652cc; font-size: 13px; font-weight: 600; line-height: 1;">{html.escape(tag)}</span>'
            for tag in article.tags
        )
        sources_section = ""
        if article.sources:
            source_items = "\n".join(
                f'<li style="font-family: {_FONT}; font-size: 13px; color: #7a8699; line-height: 1.6;">{html.escape(src)}</li>'
                for src in article.sources
            )
            sources_section = (
                f'<div style="margin-top: 28px; padding: 16px 18px; border-radius: 10px; background: #f8f9fb; border: 1px solid #e1e5eb;">'
                f'<div style="font-family: {_FONT}; font-size: 13px; font-weight: 700; color: #7a8699; margin-bottom: 8px;">참고 자료</div>'
                f'<ul style="margin: 0; padding-left: 16px;">{source_items}</ul>'
                f'</div>'
            )
        cta_section = _build_cta_section(article.tags)
        return self.template.safe_substitute(
            title=html.escape(article.title),
            subtitle=html.escape(article.subtitle),
            theme=html.escape(article.theme),
            published_label=html.escape(article.published_label),
            updated_label=html.escape(article.updated_label),
            summary_items=summary_items,
            section_items=section_items,
            tip_items=tip_items,
            tag_items=tag_items,
            disclaimer=html.escape(article.disclaimer),
            sources_section=sources_section,
            cta_section=cta_section,
        )
