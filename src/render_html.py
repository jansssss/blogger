from __future__ import annotations

import html
from pathlib import Path
from string import Template

from src.generate_post import Article


class HtmlRenderer:
    def __init__(self, template_path: Path) -> None:
        self.template = Template(template_path.read_text(encoding="utf-8"))

    def render(self, article: Article) -> str:
        summary_items = "\n".join(
            f"<li>{html.escape(item)}</li>"
            for item in article.summary_points
        )
        section_items = "\n".join(
            (
                "<section>"
                f"<h2>{html.escape(section.heading)}</h2>"
                + "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in section.paragraphs)
                + "</section>"
            )
            for section in article.sections
        )
        tip_items = "\n".join(f'<span class="hb-chip">{html.escape(item)}</span>' for item in article.action_tips)
        tag_items = "\n".join(f'<span class="hb-chip">{html.escape(tag)}</span>' for tag in article.tags)
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
