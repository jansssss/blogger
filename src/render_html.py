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
            f'<li style="font-family: {_font}; font-size: 15px; color: #2a3a5c; line-height: 1.6; word-break: keep-all;">{html.escape(item)}</li>'
            for item in article.summary_points
        )
        section_items = "\n".join(
            (
                "<section>"
                f'<h2 style="font-family: {_font}; font-size: 22px; font-weight: 800; color: #1c2741; margin: 36px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #eef2f7; letter-spacing: -0.02em; line-height: 1.4; word-break: keep-all;">{html.escape(section.heading)}</h2>'
                + "".join(f'<p style="font-family: {_font}; font-size: 16px; color: #3a4a62; margin: 0 0 14px; line-height: 1.85; word-break: keep-all;">{html.escape(paragraph)}</p>' for paragraph in section.paragraphs)
                + "</section>"
            )
            for section in article.sections
        )
        tip_items = "\n".join(f'<span style="display: inline-block; padding: 6px 14px; border-radius: 999px; background: #fff; border: 1.5px solid #ffcfc9; color: #cc3a28; font-size: 13px; font-weight: 600; line-height: 1;">{html.escape(item)}</span>' for item in article.action_tips)
        tag_items = "\n".join(f'<span style="display: inline-block; padding: 6px 14px; border-radius: 999px; background: #fff; border: 1.5px solid #bdd0ff; color: #2652cc; font-size: 13px; font-weight: 600; line-height: 1;">{html.escape(tag)}</span>' for tag in article.tags)
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
        )
