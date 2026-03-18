from __future__ import annotations

import argparse
from pathlib import Path

from src.blogger_client import BloggerClient
from src.config import load_config
from src.generate_post import ArticleGenerator
from src.render_html import HtmlRenderer
from src.topic_queue import TopicQueue


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="건강/바이오 Blogger 자동 글 생성기")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-topics", help="대기 중인 주제를 출력합니다.")
    subparsers.add_parser("list-blogs", help="현재 Blogger 인증으로 접근 가능한 블로그를 출력합니다.")

    preview_parser = subparsers.add_parser("preview", help="다음 주제 또는 특정 주제를 HTML로 미리보기 생성합니다.")
    preview_parser.add_argument("--topic-id", help="특정 주제 ID")

    publish_parser = subparsers.add_parser("publish", help="Blogger에 초안 또는 게시 상태로 업로드합니다.")
    publish_parser.add_argument("--topic-id", help="특정 주제 ID")
    publish_parser.add_argument("--mode", choices=["draft", "publish"], help="업로드 모드")

    return parser


def pick_topic(topic_queue: TopicQueue, topic_id: str | None):
    return topic_queue.get_by_id(topic_id) if topic_id else topic_queue.next_topic()


def save_preview(preview_dir: Path, article_slug: str, html: str) -> Path:
    preview_dir.mkdir(parents=True, exist_ok=True)
    output_path = preview_dir / f"{article_slug}.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config()
    topic_queue = TopicQueue(config.topics_path)
    client = BloggerClient(
        blog_id=config.blogger_blog_id,
        access_token=config.blogger_access_token,
        refresh_token=config.blogger_refresh_token,
        google_client_id=config.google_client_id,
        google_client_secret=config.google_client_secret,
        payload_dir=config.payload_dir,
    )

    if args.command == "list-topics":
        for topic in topic_queue.list_pending():
            print(f"{topic.id}\t{topic.priority}\t{topic.title_hint}")
        return

    if args.command == "list-blogs":
        blogs = client.list_blogs()
        for blog in blogs:
            print(f'{blog.get("id")}\t{blog.get("name")}\t{blog.get("url", "")}')
        return

    topic = pick_topic(topic_queue, getattr(args, "topic_id", None))
    generator = ArticleGenerator(
        theme_name=config.theme_name,
        prompt_path=config.prompt_path,
        anthropic_api_key=config.anthropic_api_key,
        anthropic_model=config.anthropic_model,
    )
    article = generator.build_article(topic)
    renderer = HtmlRenderer(config.template_path)
    html = renderer.render(article)

    if args.command == "preview":
        path = save_preview(config.preview_dir, article.slug, html)
        print(f"Preview created: {path}")
        return

    publish_mode = args.mode or config.blogger_publish_mode
    result = client.publish(article, html, publish_mode)
    topic_queue.update_status(topic.id, "drafted" if publish_mode == "draft" else "published")
    print(f"Uploaded: {result.status} post_id={result.post_id} url={result.url}")


if __name__ == "__main__":
    main()
