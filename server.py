import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from jp_lesson import key_from_topic, read_lessons, try_check_json

HOST = "localhost"
PORT = 8000

# Directory paths anchored to this file's location
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TOPICS_FILE = BASE_DIR / "grammar_topics.txt"
PROMPT_FILE = BASE_DIR / "generate_lesson_prompt.md"


def get_completed_hashes() -> set[str]:
    """Reads existing topic hashes from lessons.json."""
    try:
        data = read_lessons()
        return set(data.keys()) if isinstance(data, dict) else set()
    except (json.JSONDecodeError, OSError):
        return set()


def get_topic_progress() -> tuple[str | None, int, int]:
    """Returns (next_topic, remaining_count, total_count)."""
    if not TOPICS_FILE.exists():
        return None, 0, 0

    completed = get_completed_hashes()
    missing: list[str] = []
    total = 0

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            topic = line.strip()
            if topic:
                total += 1
                if key_from_topic(topic) not in completed:
                    missing.append(topic)

    next_topic = missing[0] if missing else None
    return next_topic, len(missing), total

    completed = get_completed_hashes()
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            topic = line.strip()
            if topic and key_from_topic(topic) not in completed:
                return topic
    return None


class AppRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, file_path: Path) -> None:
        """Safely serves a static file with appropriate MIME type."""
        try:
            resolved = file_path.resolve()
            # Prevent path traversal outside the static folder
            if not resolved.is_relative_to(STATIC_DIR) or not resolved.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            mime_type, _ = mimetypes.guess_type(resolved)
            content_type = mime_type or "application/octet-stream"
            if content_type.startswith("text/") or content_type in (
                "application/javascript",
                "application/json",
            ):
                content_type += "; charset=utf-8"

            data = resolved.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except OSError:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_GET(self) -> None:
        # Static asset routing
        if self.path in ("/", "/index.html"):
            self._serve_file(STATIC_DIR / "index.html")
        elif self.path in ("/style.css", "/app.js"):
            self._serve_file(STATIC_DIR / self.path.lstrip("/"))
        # API routing
        elif self.path == "/api/topic":
            topic, remaining, total = get_topic_progress()
            self._send_json(
                {
                    "done": topic is None,
                    "topic": topic or "",
                    "remaining": remaining,
                    "total": total,
                }
            )
        elif self.path == "/api/system-prompt":
            content = (
                PROMPT_FILE.read_text(encoding="utf-8") if PROMPT_FILE.exists() else ""
            )
            self._send_json({"prompt": content})
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/submit":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))

            topic = payload.get("topic", "").strip()
            json_str = payload.get("json_str", "").strip()

            if not topic or not json_str:
                self._send_json(
                    {"success": False, "error": "Missing topic or JSON body."},
                    HTTPStatus.BAD_REQUEST,
                )
                return

            # Invoke custom validation logic
            try_check_json(lesson_json=json_str, grammar_topic=topic)
            self._send_json({"success": True})

        except Exception as err:
            # Handles KeyError, JSONDecodeError, or custom schema exceptions
            error_msg = f"{type(err).__name__}: {err}"
            self._send_json({"success": False, "error": error_msg})

    def log_message(self, format: str, *args) -> None:
        # Suppress routine GET/POST console logs to keep terminal quiet
        return


def main() -> None:
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, AppRequestHandler)
    print(f"Server listening at http://{HOST}:{PORT}/\nCtrl+C to quit")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()
