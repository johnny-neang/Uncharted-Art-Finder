"""Vercel function: POST /api/comment { slug, text } → save a freeform note.

Notes are stored per-slug in data/notes.json on main via the GitHub Contents
API, so they survive rebuilds and are shared across everyone viewing the
dashboard. The same slug keys both Directory artists and Candidates, so a note
follows an entry when it's promoted. Requires GITHUB_PAT (fine-grained PAT with
Contents:write on this repo) — the same token promote/demote already use.

An empty `text` clears the note for that slug. Kept in its own small file so a
save never has to rewrite the multi-MB discoveries.json.
"""
from http.server import BaseHTTPRequestHandler
import base64
import json
import os
import urllib.error
import urllib.request
from datetime import timezone, datetime

REPO_OWNER = "johnny-neang"
REPO_NAME = "Uncharted-Art-Finder"
BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
NOTES_PATH = "data/notes.json"
MAX_NOTE_CHARS = 4000


def _gh_request(method, url, body=None):
    pat = os.environ.get("GITHUB_PAT")
    if not pat:
        raise RuntimeError("GITHUB_PAT env var not configured")
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "uncharted-art-finder",
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept-Encoding": "identity",  # no gzip — urllib won't decompress
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub {method} {url[:80]} -> HTTP {e.code}: {body_text[:300]}")
    if not raw:
        raise RuntimeError(f"GitHub {method} {url[:80]} -> HTTP {status} but empty body")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        preview = raw[:300].decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub {method} {url[:80]} -> HTTP {status}, non-JSON body "
            f"(len={len(raw)}): {preview}"
        )


def _get_notes():
    """Return (notes_dict, sha). sha is None if the file doesn't exist yet —
    _put_file then creates it. Tolerates an empty/legacy-shaped file."""
    try:
        meta = _gh_request("GET", f"{API_BASE}/contents/{NOTES_PATH}?ref={BRANCH}")
    except RuntimeError as e:
        if "HTTP 404" in str(e):
            return {"by_slug": {}}, None
        raise
    sha = meta["sha"]
    blob = _gh_request("GET", f"{API_BASE}/git/blobs/{sha}")
    raw = base64.b64decode(blob["content"]).decode("utf-8")
    data = json.loads(raw) if raw.strip() else {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("by_slug", {})
    return data, sha


def _put_file(path, data, sha, message):
    content_json = json.dumps(data, indent=2, ensure_ascii=False)
    body = {
        "message": message,
        "content": base64.b64encode(content_json.encode("utf-8")).decode("ascii"),
        "branch": BRANCH,
    }
    if sha:  # omit on create (file doesn't exist yet)
        body["sha"] = sha
    return _gh_request("PUT", f"{API_BASE}/contents/{path}", body=body)


def _save_comment(slug, text, author):
    """Upsert (or clear) the note for `slug`. Retries once on a 409 sha
    conflict so back-to-back saves from the dashboard don't drop a write."""
    last_err = None
    for attempt in range(2):
        notes, sha = _get_notes()
        by_slug = notes.setdefault("by_slug", {})
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if text:
            entry = {"text": text, "updated_at": now}
            if author:
                entry["by"] = author
            by_slug[slug] = entry
            msg = f"dashboard: note on {slug}"
        else:
            by_slug.pop(slug, None)
            msg = f"dashboard: clear note on {slug}"
        try:
            _put_file(NOTES_PATH, notes, sha, msg)
            out = by_slug.get(slug, {})
            return 200, {
                "ok": True,
                "slug": slug,
                "text": out.get("text", ""),
                "updated_at": out.get("updated_at"),
            }
        except RuntimeError as e:
            last_err = e
            if "HTTP 409" in str(e) and attempt == 0:
                continue  # stale sha — re-fetch and retry once
            raise
    raise last_err


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length_hdr = self.headers.get("Content-Length")
            length = int(length_hdr) if length_hdr and length_hdr.isdigit() else 0
            body_bytes = self.rfile.read(length) if length > 0 else b""
            if not body_bytes:
                self._respond(400, {"ok": False, "error": "empty request body"})
                return
            try:
                payload = json.loads(body_bytes)
            except json.JSONDecodeError as je:
                preview = body_bytes[:200].decode("utf-8", errors="replace")
                self._respond(400, {"ok": False, "error": f"body not JSON: {je}; raw: {preview!r}"})
                return
            slug = (payload.get("slug") or "").strip()
            if not slug:
                self._respond(400, {"ok": False, "error": "slug required"})
                return
            text = (payload.get("text") or "").strip()[:MAX_NOTE_CHARS]
            author = (payload.get("by") or "").strip()[:80]
            status, result = _save_comment(slug, text, author)
            self._respond(status, result)
        except Exception as e:
            self._respond(500, {"ok": False, "error": f"{type(e).__name__}: {str(e)[:300]}"})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
