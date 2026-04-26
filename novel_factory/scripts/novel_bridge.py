import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from init_book_project import build_project, safe_book_id


ROOT = Path(__file__).resolve().parents[2]
FACTORY_DIR = ROOT / "novel_factory"
PROJECTS_DIR = ROOT / "novel_projects"


def json_bytes(data, status=200):
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    return status, "application/json; charset=utf-8", body


def text_bytes(text, status=200):
    return status, "text/plain; charset=utf-8", text.encode("utf-8")


def read_body(handler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


def safe_child(base: Path, relative: str) -> Path:
    target = (base / relative).resolve()
    base_resolved = base.resolve()
    if target != base_resolved and base_resolved not in target.parents:
        raise ValueError("path escapes base directory")
    return target


def list_files(base: Path):
    if not base.exists():
        return []
    return [
        str(path.relative_to(base)).replace("\\", "/")
        for path in base.rglob("*")
        if path.is_file()
    ]


class NovelBridgeHandler(BaseHTTPRequestHandler):
    server_version = "NovelBridge/0.1"

    def _authorized(self):
        token = getattr(self.server, "token", None)
        if not token:
            return True
        auth = self.headers.get("Authorization", "")
        header_token = self.headers.get("X-Novel-Token", "")
        return header_token == token or auth == f"Bearer {token}"

    def _send(self, response):
        status, content_type, body = response
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, message, status=400):
        self._send(json_bytes({"error": message}, status))

    def do_GET(self):
        if not self._authorized():
            self._error("unauthorized", 401)
            return
        try:
            parsed = urlparse(self.path)
            parts = [unquote(p) for p in parsed.path.strip("/").split("/") if p]
            query = parse_qs(parsed.query)

            if parsed.path == "/health":
                self._send(json_bytes({"status": "ok", "root": str(ROOT)}))
                return

            if parts == ["api", "prompts"]:
                self._send(json_bytes({"prompts": list_files(FACTORY_DIR / "prompts")}))
                return

            if len(parts) == 3 and parts[:2] == ["api", "prompts"]:
                name = parts[2]
                path = safe_child(FACTORY_DIR / "prompts", name)
                if path.suffix != ".md" or not path.exists():
                    self._error("prompt not found", 404)
                    return
                self._send(json_bytes({"name": name, "content": path.read_text(encoding="utf-8")}))
                return

            if parts == ["api", "schemas"]:
                self._send(json_bytes({"schemas": list_files(FACTORY_DIR / "schemas")}))
                return

            if len(parts) == 3 and parts[:2] == ["api", "schemas"]:
                name = parts[2]
                path = safe_child(FACTORY_DIR / "schemas", name)
                if path.suffix != ".json" or not path.exists():
                    self._error("schema not found", 404)
                    return
                self._send(json_bytes({"name": name, "schema": json.loads(path.read_text(encoding="utf-8"))}))
                return

            if len(parts) == 4 and parts[:2] == ["api", "books"] and parts[3] == "manifest":
                book_id = parts[2]
                base = safe_child(PROJECTS_DIR, book_id)
                self._send(json_bytes({"book_id": book_id, "files": list_files(base)}))
                return

            if len(parts) == 4 and parts[:2] == ["api", "books"] and parts[3] == "read":
                book_id = parts[2]
                rel = query.get("path", [""])[0]
                base = safe_child(PROJECTS_DIR, book_id)
                path = safe_child(base, rel)
                if not path.exists() or not path.is_file():
                    self._error("file not found", 404)
                    return
                content = path.read_text(encoding="utf-8")
                if path.suffix == ".json":
                    self._send(json_bytes({"path": rel, "content": json.loads(content)}))
                else:
                    self._send(json_bytes({"path": rel, "content": content}))
                return

            self._error("not found", 404)
        except Exception as exc:
            self._error(str(exc), 500)

    def do_POST(self):
        if not self._authorized():
            self._error("unauthorized", 401)
            return
        try:
            parsed = urlparse(self.path)
            parts = [unquote(p) for p in parsed.path.strip("/").split("/") if p]
            body = read_body(self)

            if parts == ["api", "books", "init"]:
                title = body.get("title", "").strip()
                if not title:
                    self._error("title is required", 400)
                    return
                chapter_count = int(body.get("chapter_count") or 20)
                book_id = body.get("book_id") or safe_book_id(title)
                project_dir = build_project(ROOT, title, book_id, chapter_count)
                self._send(json_bytes({"book_id": book_id, "project_dir": str(project_dir)}))
                return

            if len(parts) == 4 and parts[:2] == ["api", "books"] and parts[3] == "write":
                book_id = parts[2]
                rel = body.get("path", "")
                if not rel:
                    self._error("path is required", 400)
                    return
                base = safe_child(PROJECTS_DIR, book_id)
                path = safe_child(base, rel)
                path.parent.mkdir(parents=True, exist_ok=True)
                content = body.get("content", "")
                if path.suffix == ".json" and not isinstance(content, str):
                    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
                elif path.suffix == ".json" and isinstance(content, str):
                    json.loads(content)
                    path.write_text(content, encoding="utf-8")
                else:
                    if not isinstance(content, str):
                        content = json.dumps(content, ensure_ascii=False, indent=2)
                    path.write_text(content, encoding="utf-8")
                self._send(json_bytes({"book_id": book_id, "path": rel, "saved": True}))
                return

            self._error("not found", 404)
        except Exception as exc:
            self._error(str(exc), 500)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


def main():
    parser = argparse.ArgumentParser(description="Serve novel_factory files to n8n through a small HTTP bridge.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Keep localhost unless you know what you are doing.")
    parser.add_argument("--port", type=int, default=8765, help="Bind port.")
    parser.add_argument("--token", default=None, help="Optional token required as X-Novel-Token or Bearer token.")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), NovelBridgeHandler)
    server.token = args.token
    print(f"Novel bridge listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
