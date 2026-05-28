"""Vercel function: POST /api/demote { slug } → move directory entry back to Candidates.

Reverse of promote. See api/promote.py for the GH Contents API pattern.
"""
from http.server import BaseHTTPRequestHandler
import base64
import json
import os
import urllib.error
import urllib.request
from datetime import date, timezone, datetime

REPO_OWNER = "johnny-neang"
REPO_NAME = "Uncharted-Art-Finder"
BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


def _gh_request(method, url, body=None):
    pat = os.environ.get("GITHUB_PAT")
    if not pat:
        raise RuntimeError("GITHUB_PAT env var not configured")
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "uncharted-art-finder",
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept-Encoding": "identity",
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


RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"


def _get_file(path):
    # Contents API gives us the sha; raw.* gives us the full body (no 1MB cap).
    meta = _gh_request("GET", f"{API_BASE}/contents/{path}?ref={BRANCH}")
    sha = meta["sha"]
    # Cache-bust raw.* with the sha we just got from the (uncached) Contents API.
    raw_url = f"{RAW_BASE}/{path}?_sha={sha}"
    headers = {
        "User-Agent": "uncharted-art-finder",
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    req = urllib.request.Request(raw_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"raw GET {path} -> HTTP {e.code}")
    if not raw:
        raise RuntimeError(f"raw GET {path} returned empty body")
    return json.loads(raw.decode("utf-8")), sha


def _put_file(path, data, sha, message):
    content_json = json.dumps(data, indent=2, ensure_ascii=False)
    body = {
        "message": message,
        "content": base64.b64encode(content_json.encode("utf-8")).decode("ascii"),
        "sha": sha,
        "branch": BRANCH,
    }
    return _gh_request("PUT", f"{API_BASE}/contents/{path}", body=body)


def _demote(slug):
    artists, art_sha = _get_file("data/artists.json")
    artist = next((a for a in artists if a.get("slug") == slug), None)
    if not artist:
        return 404, {"ok": False, "error": f"slug '{slug}' not in directory"}

    discoveries, disc_sha = _get_file("data/discoveries.json")
    if any(c.get("slug") == slug for c in discoveries.get("candidates", [])):
        return 409, {"ok": False, "error": f"'{slug}' already in candidates"}

    candidate = {
        "slug": slug,
        "name": artist.get("name") or slug,
        "url": artist.get("primaryUrl") or "",
        "source_name": "demoted from directory",
        "image": (artist.get("thumbs") or [None])[0],
        "thumbs": artist.get("thumbs") or [],
        "first_seen": str(date.today()),
        "status": "pending",
        "manual_override": "watch",
        "demoted_from_directory": {
            "n_original": artist.get("n"),
            "tier_original": artist.get("tier"),
            "via": "dashboard",
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
    }
    discoveries.setdefault("candidates", []).append(candidate)
    name = artist.get("name") or slug

    # Add to candidates first (safer ordering — if the second PUT fails, the
    # item exists in both lists, easy to reconcile vs being lost entirely).
    _put_file("data/discoveries.json", discoveries, disc_sha,
              f"dashboard: demote {name} back to candidates")

    artists = [a for a in artists if a.get("slug") != slug]
    _put_file("data/artists.json", artists, art_sha,
              f"dashboard: remove {name} from directory (demoted)")

    return 200, {"ok": True, "slug": slug, "name": name}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length_hdr = self.headers.get("Content-Length")
            length = int(length_hdr) if length_hdr and length_hdr.isdigit() else 0
            body_bytes = self.rfile.read(length) if length > 0 else b""
            if not body_bytes:
                self._respond(400, {
                    "ok": False,
                    "error": f"empty request body (Content-Length={length_hdr!r})",
                })
                return
            try:
                payload = json.loads(body_bytes)
            except json.JSONDecodeError as je:
                preview = body_bytes[:200].decode("utf-8", errors="replace")
                self._respond(400, {
                    "ok": False,
                    "error": f"body not JSON: {je}; raw (len={len(body_bytes)}): {preview!r}",
                })
                return
            slug = (payload.get("slug") or "").strip()
            if not slug:
                self._respond(400, {"ok": False, "error": "slug required"})
                return
            status, result = _demote(slug)
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
