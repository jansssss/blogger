from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib import error, parse, request

from src.generate_post import Article


@dataclass
class BloggerResult:
    post_id: str
    url: str
    status: str


class BloggerClient:
    def __init__(
        self,
        blog_id: str | None,
        access_token: str | None,
        refresh_token: str | None,
        google_client_id: str | None,
        google_client_secret: str | None,
        payload_dir: Path,
    ) -> None:
        self.blog_id = blog_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        self.payload_dir = payload_dir

    def publish(self, article: Article, html: str, mode: str) -> BloggerResult:
        if not self.blog_id:
            raise ValueError("BLOGGER_BLOG_ID must be configured.")
        token = self._get_token()
        if not token:
            raise ValueError(
                "Provide BLOGGER_ACCESS_TOKEN for testing or BLOGGER_REFRESH_TOKEN + GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET for automation."
            )

        self.payload_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "kind": "blogger#post",
            "title": article.title,
            "content": html,
            "labels": article.tags,
        }
        payload_path = self.payload_dir / f"{article.topic_id}.json"
        payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        params = {"isDraft": "true" if mode == "draft" else "false"}
        url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/?{parse.urlencode(params)}"
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        data = self._open_json(http_request)
        return BloggerResult(
            post_id=data["id"],
            url=data.get("url", ""),
            status="draft" if params["isDraft"] == "true" else "published",
        )

    def list_blogs(self) -> list[dict]:
        token = self._get_token()
        if not token:
            raise ValueError(
                "Provide BLOGGER_ACCESS_TOKEN for testing or BLOGGER_REFRESH_TOKEN + GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET for automation."
            )
        http_request = request.Request(
            "https://www.googleapis.com/blogger/v3/users/self/blogs",
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        data = self._open_json(http_request)
        return data.get("items", [])

    def _refresh_access_token(self) -> str | None:
        if not self.refresh_token or not self.google_client_id or not self.google_client_secret:
            return None
        body = parse.urlencode(
            {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
            }
        ).encode("utf-8")
        http_request = request.Request(
            "https://oauth2.googleapis.com/token",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        data = self._open_json(http_request)
        return data["access_token"]

    def _get_token(self) -> str | None:
        return self.access_token or self._refresh_access_token()

    @staticmethod
    def _open_json(http_request: request.Request) -> dict:
        try:
            with request.urlopen(http_request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {body}") from exc
