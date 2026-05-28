"""Vercel function: POST /api/promote { slug } → move candidate to Directory.

Writes directly to data/artists.json and data/discoveries.json on main via
the GitHub Contents API. Requires GITHUB_PAT env var (fine-grained PAT with
Contents:write on this repo).
"""
from http.server import BaseHTTPRequestHandler
import base64
import json
import os
import urllib.error
import urllib.request
from datetime import date, timezone, datetime
from urllib.parse import urlparse

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
    except json.JSONDecodeError as e:
        # Surface enough of the raw body to debug. Often this is HTML from a
        # redirect, gzip we couldn't decode, or an empty response.
        preview = raw[:300].decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub {method} {url[:80]} -> HTTP {status}, non-JSON body "
            f"(len={len(raw)}): {preview}"
        )


RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"


def _get_file(path):
    # Step 1: Contents API for the sha (metadata is small even when the file isn't).
    meta = _gh_request("GET", f"{API_BASE}/contents/{path}?ref={BRANCH}")
    sha = meta["sha"]
    # Step 2: read the actual bytes. Contents API caps content at 1MB and returns
    # an empty `content` field above that, so we always go through raw.* for the
    # body. The repo is public, so no auth header is needed for raw.*.
    raw_url = f"{RAW_BASE}/{path}"
    headers = {"User-Agent": "uncharted-art-finder", "Accept-Encoding": "identity"}
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


def _promote(slug):
    discoveries, disc_sha = _get_file("data/discoveries.json")
    candidate = next((c for c in discoveries.get("candidates", []) if c.get("slug") == slug), None)
    if not candidate:
        return 404, {"ok": False, "error": f"slug '{slug}' not in discoveries"}

    artists, art_sha = _get_file("data/artists.json")
    if any(a.get("slug") == slug for a in artists):
        return 409, {"ok": False, "error": f"'{slug}' already in directory"}

    score = candidate.get("score") or {}
    url = candidate.get("url") or ""
    primary_host = urlparse(url).netloc if url else ""
    thumbs = candidate.get("thumbs") or ([candidate["image"]] if candidate.get("image") else [])

    new_entry = {
        "n": max((a.get("n", 0) for a in artists), default=0) + 1,
        "slug": slug,
        "name": candidate.get("name") or slug,
        "tier": score.get("suggested_tier") or 2,
        "kind": score.get("kind") or "Artist",
        "medium": score.get("medium") or "Mixed media",
        "tags": score.get("suggested_tags") or [],
        "summary": score.get("one_line_summary") or candidate.get("seed_description") or "",
        "fit": score.get("family_fit") or 3,
        "suitability": score.get("suitability") or "",
        "primaryUrl": url,
        "primaryHost": primary_host,
        "thumbs": thumbs,
        "addedAt": str(date.today()),
        "status": "active",
        "promoted_from": {
            "source_name": candidate.get("source_name"),
            "first_seen": candidate.get("first_seen"),
            "via": "dashboard",
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
    }
    artists.append(new_entry)
    name = candidate.get("name") or slug

    # Order matters: add to artists.json first (safe — duplicate-detect handles
    # any subsequent retry); then remove from discoveries.json.
    _put_file("data/artists.json", artists, art_sha,
              f"dashboard: promote {name} to directory")

    discoveries["candidates"] = [c for c in discoveries["candidates"] if c.get("slug") != slug]
    _put_file("data/discoveries.json", discoveries, disc_sha,
              f"dashboard: remove {name} from candidates (promoted)")

    return 200, {
        "ok": True,
        "slug": slug,
        "n": new_entry["n"],
        "name": name,
        "tier": new_entry["tier"],
    }


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
            status, result = _promote(slug)
            self._respond(status, result)
        except Exception as e:
            self._respond(500, {"ok": False, "error": f"{type(e).__name__}: {str(e)[:300]}"})

    def do_OPTIONS(self):
        # CORS preflight (same-origin in production, but useful for local dev)
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
