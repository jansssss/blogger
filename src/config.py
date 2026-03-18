from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    theme_name: str
    topics_path: Path
    template_path: Path
    prompt_path: Path
    preview_dir: Path
    payload_dir: Path
    anthropic_api_key: str | None
    anthropic_model: str
    blogger_blog_id: str | None
    blogger_access_token: str | None
    blogger_refresh_token: str | None
    google_client_id: str | None
    google_client_secret: str | None
    blogger_publish_mode: str


def _load_dotenv_file(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_config() -> AppConfig:
    project_root = Path(__file__).resolve().parent.parent
    _load_dotenv_file(project_root / ".env")

    return AppConfig(
        project_root=project_root,
        theme_name=os.getenv("BLOG_THEME_NAME", "건강한 100세를 위해"),
        topics_path=project_root / "data" / "topics.csv",
        template_path=project_root / "templates" / "article.html.j2",
        prompt_path=project_root / "prompts" / "health_article_prompt.txt",
        preview_dir=project_root / "output" / "previews",
        payload_dir=project_root / "output" / "payloads",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        anthropic_model=os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-6",
        blogger_blog_id=os.getenv("BLOGGER_BLOG_ID") or None,
        blogger_access_token=os.getenv("BLOGGER_ACCESS_TOKEN") or None,
        blogger_refresh_token=os.getenv("BLOGGER_REFRESH_TOKEN") or None,
        google_client_id=os.getenv("GOOGLE_CLIENT_ID") or None,
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET") or None,
        blogger_publish_mode=os.getenv("BLOGGER_PUBLISH_MODE", "draft"),
    )
