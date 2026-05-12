from __future__ import annotations

import html
from pathlib import Path
from string import Template

from src.generate_post import Article

_FONT = "'Apple SD Gothic Neo', 'Malgun Gothic', 'Segoe UI', sans-serif"

# 쿠팡 파트너스 제휴 상품 정의
_AFFILIATE_PRODUCTS = [
    {"id": "protein-supplement", "rank": 1, "emoji": "💊", "name": "단백질 보충제", "desc": "근감소 예방·근육 유지를 돕는 고흡수 단백질.", "url": "https://link.coupang.com/a/eaqvqF", "keywords": ["단백질", "근육", "근감소", "근력운동", "근육합성", "근육회복", "근감소증"]},
    {"id": "omega3", "rank": 2, "emoji": "🐟", "name": "오메가3", "desc": "혈관·뇌 건강을 지키는 EPA/DHA 오메가3.", "url": "https://link.coupang.com/a/eaqxGL", "keywords": ["혈관건강", "혈압", "심혈관", "뇌건강", "혈액순환"]},
    {"id": "joint-supplement", "rank": 3, "emoji": "🦵", "name": "관절 영양제", "desc": "무릎·연골 보호를 위한 글루코사민·콜라겐.", "url": "https://link.coupang.com/a/eaqKPo", "keywords": ["무릎통증", "관절", "무릎보호", "관절보호", "스트레칭", "유연성"]},
    {"id": "vitamin-d-calcium", "rank": 4, "emoji": "☀️", "name": "비타민D + 칼슘", "desc": "뼈 건강과 낙상 예방을 위한 비타민D·칼슘 복합.", "url": "https://link.coupang.com/a/eaqLVY", "keywords": ["낙상예방", "균형감각", "면역력", "뼈", "골밀도"]},
    {"id": "magnesium-sleep", "rank": 5, "emoji": "🌙", "name": "마그네슘 · 수면 영양제", "desc": "수면의 질 개선과 스트레스 완화에 도움.", "url": "https://link.coupang.com/a/eaqNVU", "keywords": ["수면", "수면 개선", "피로 회복", "스트레스", "수면질"]},
    {"id": "lutein", "rank": 6, "emoji": "👁️", "name": "루테인 · 지아잔틴", "desc": "모니터 장시간 사용으로 지친 눈을 보호하는 눈 건강 영양제. 루테인·지아잔틴이 황반 색소를 보충해 눈 피로와 안구건조를 완화.", "url": "https://link.coupang.com/a/eeXERJ", "keywords": ["눈 피로", "안구건조증", "눈 통증", "눈 건강", "블루라이트"]},
    {"id": "vitamin-b", "rank": 7, "emoji": "💊", "name": "비타민B 복합제", "desc": "B1·B6·B12가 신경·에너지 대사를 지원. 손목·팔꿈치 신경통 완화에 B6가 직접적으로 효과.", "url": "https://link.coupang.com/a/eeXWVI", "keywords": ["피로 회복", "신경통", "에너지", "만성 피로"]},
    {"id": "vitamin-c", "rank": 8, "emoji": "🍊", "name": "비타민C", "desc": "항산화·면역력 강화로 누적 피로를 빠르게 회복. 콜라겐 합성도 도와 관절·피부 건강에도 기여.", "url": "https://link.coupang.com/a/eeXYUk", "keywords": ["피로 회복", "면역력", "항산화", "만성 피로"]},
    {"id": "collagen-peptide", "rank": 9, "emoji": "🦴", "name": "콜라겐 펩타이드", "desc": "힘줄·연골의 원료가 되는 저분자 콜라겐. 손목·팔꿈치 통증 완화와 관절 유연성 유지에 도움.", "url": "https://link.coupang.com/a/eeXJxm", "keywords": ["스트레칭", "관절", "연골", "유연성"]},
    {"id": "coenzyme-q10", "rank": 10, "emoji": "⚡", "name": "코엔자임Q10", "desc": "세포 미토콘드리아에서 에너지를 만드는 핵심 성분. 만성 피로·체력 저하를 느끼는 직장인에게 추천.", "url": "https://link.coupang.com/a/eeXKhZ", "keywords": ["피로 회복", "만성 피로", "에너지", "심혈관", "항산화"]},
    {"id": "milk-thistle", "rank": 11, "emoji": "🌿", "name": "밀크씨슬 (간 건강)", "desc": "실리마린 성분이 간세포를 보호하고 해독 기능을 높여 회식·음주 후 피로 회복에 효과적.", "url": "https://link.coupang.com/a/eeXK7d", "keywords": ["피로 회복", "간건강", "만성 피로", "해독"]},
    {"id": "iron-supplement", "rank": 12, "emoji": "🩸", "name": "철분 영양제", "desc": "철분 부족으로 생기는 빈혈성 피로를 해소. 특히 여성의 만성 피로 원인 1위인 철 결핍에 효과적.", "url": "https://link.coupang.com/a/eeXLTg", "keywords": ["피로 회복", "만성 피로", "빈혈", "여성 건강"]},
]

_COUPANG_DISCLOSURE = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."


def _pick_products(tags: list[str]) -> list[dict]:
    """태그 키워드와 가장 많이 겹치는 상품 최대 2개 반환. 매칭 0이면 rank 1·2 기본."""
    scored = []
    for p in _AFFILIATE_PRODUCTS:
        score = sum(1 for k in p["keywords"] for t in tags if k == t or t in k or k in t)
        scored.append((score, p["rank"], p))
    scored.sort(key=lambda x: (-x[0], x[1]))
    top = [x[2] for x in scored[:2] if x[0] > 0]
    return top if top else _AFFILIATE_PRODUCTS[:2]


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
            f'margin-bottom:12px; letter-spacing:0.04em;">추천 제품</div>'
            # 이모지 + 상품명
            f'<div style="font-family:{_FONT}; font-size:16px; font-weight:800; color:#1c2741; '
            f'margin-bottom:6px; line-height:1.4; word-break:keep-all;">{p["emoji"]} {html.escape(p["name"])}</div>'
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
        f'letter-spacing:0.12em; margin-bottom:6px;">HEALTH PRODUCT</div>'
        # 섹션 제목
        f'<div style="font-family:{_FONT}; font-size:18px; font-weight:800; color:#1c2741; '
        f'margin-bottom:18px; letter-spacing:-0.02em; line-height:1.4;">이 글과 함께 챙기면 좋은 것</div>'
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
