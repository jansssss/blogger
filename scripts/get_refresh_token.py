"""
Google OAuth refresh token 재발급 스크립트.

사용법:
    python scripts/get_refresh_token.py

사전 조건:
    - .env 파일에 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET 설정
    - Google Cloud Console에서 승인된 리디렉션 URI에 http://localhost:8080 추가
"""
from __future__ import annotations

import json
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse, request

# .env 로드
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            k, v = _line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8080"
SCOPE = "https://www.googleapis.com/auth/blogger"

if not CLIENT_ID or not CLIENT_SECRET:
    sys.exit("오류: GOOGLE_CLIENT_ID 또는 GOOGLE_CLIENT_SECRET이 설정되지 않았습니다.")

# 1단계: 인증 URL 생성 및 브라우저 열기
auth_url = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    + parse.urlencode(
        {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",  # 항상 refresh_token 반환하도록 강제
        }
    )
)

print(f"\n브라우저에서 아래 URL을 열어 Google 계정으로 로그인하세요:\n\n{auth_url}\n")
webbrowser.open(auth_url)

# 2단계: 로컬 서버로 code 수신
received_code: str | None = None


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        global received_code
        qs = parse.urlparse(self.path).query
        params = parse.parse_qs(qs)
        if "code" in params:
            received_code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write("<h2>인증 완료! 터미널로 돌아가세요.</h2>".encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("code 파라미터를 찾을 수 없습니다.".encode("utf-8"))

    def log_message(self, *_):  # 서버 로그 억제
        pass


print("로그인 후 자동으로 code를 수신합니다... (Ctrl+C로 취소)")
server = HTTPServer(("localhost", 8080), _Handler)
server.handle_request()

if not received_code:
    sys.exit("인증 코드를 받지 못했습니다.")

# 3단계: code → token 교환
body = parse.urlencode(
    {
        "code": received_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
).encode("utf-8")

req = request.Request(
    "https://oauth2.googleapis.com/token",
    data=body,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST",
)
with request.urlopen(req, timeout=30) as resp:
    token_data = json.loads(resp.read().decode("utf-8"))

refresh_token = token_data.get("refresh_token")
if not refresh_token:
    print("\n응답:", json.dumps(token_data, indent=2))
    sys.exit("refresh_token이 응답에 없습니다. prompt=consent가 작동했는지 확인하세요.")

print("\n" + "=" * 60)
print("새 BLOGGER_REFRESH_TOKEN:")
print(refresh_token)
print("=" * 60)
print("\nGitHub 저장소 → Settings → Secrets → BLOGGER_REFRESH_TOKEN 을 위 값으로 업데이트하세요.")
