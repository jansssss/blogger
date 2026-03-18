from __future__ import annotations

import html
from pathlib import Path
from string import Template

from src.generate_post import Article


class HtmlRenderer:
    def __init__(self, template_path: Path) -> None:
        self.template = Template(template_path.read_text(encoding="utf-8"))

    def render(self, article: Article) -> str:
        _font = "'Apple SD Gothic Neo', 'Malgun Gothic', 'Segoe UI', sans-serif"
        summary_items = "\n".join(
            f'<li style="font-family: {_font}; font-size: 15px; color: #2a3a5c; line-height: 1.7; margin-bottom: 8px; word-break: keep-all;">{html.escape(item)}</li>'
            for item in article.summary_points
        )

        section_parts = []
        for section in article.sections:
            paragraphs_html = "".join(
                f'<p style="font-family: {_font}; font-size: 16px; color: #3a4a62; margin: 0 0 14px; line-height: 1.9; word-break: keep-all;">{html.escape(paragraph)}</p>'
                for paragraph in section.paragraphs
            )
            insight_html = ""
            if section.expert_insight:
                insight_html = (
                    f'<div style="background: #f0f4ff; border-left: 4px solid #3268ff; border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 4px 0 20px;">'
                    f'<div style="font-family: {_font}; font-size: 12px; font-weight: 700; color: #3268ff; margin-bottom: 6px; letter-spacing: 0.04em;">전문가 인사이트</div>'
                    f'<p style="font-family: {_font}; font-size: 15px; color: #2a3a5c; margin: 0; line-height: 1.75; word-break: keep-all;">{html.escape(section.expert_insight)}</p>'
                    f'</div>'
                )
            section_parts.append(
                f"<section>"
                f'<h2 style="font-family: {_font}; font-size: 22px; font-weight: 800; color: #1c2741; margin: 40px 0 14px; padding-bottom: 8px; border-bottom: 2px solid #eef2f7; letter-spacing: -0.02em; line-height: 1.4; word-break: keep-all;">{html.escape(section.heading)}</h2>'
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
                f'<li style="font-family: {_font}; font-size: 13px; color: #7a8699; line-height: 1.6;">{html.escape(src)}</li>'
                for src in article.sources
            )
            sources_section = (
                f'<div style="margin-top: 28px; padding: 16px 18px; border-radius: 10px; background: #f8f9fb; border: 1px solid #e1e5eb;">'
                f'<div style="font-family: {_font}; font-size: 13px; font-weight: 700; color: #7a8699; margin-bottom: 8px;">참고 자료</div>'
                f'<ul style="margin: 0; padding-left: 16px;">{source_items}</ul>'
                f'</div>'
            )
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
        )
