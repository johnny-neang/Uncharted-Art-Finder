"""Shared helpers: HTTP, image processing, slug, paths."""
from __future__ import annotations

import base64
import json
import logging
import re
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
DIGESTS = DATA / "digests"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

logger = logging.getLogger("uchart")


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
        datefmt="%H:%M:%S",
    )


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def get(url: str, timeout: int = 20, **kw) -> requests.Response | None:
    """GET a URL with sensible defaults; return None on any failure."""
    try:
        host = urlparse(url).netloc
        headers = {**HEADERS, "Referer": f"https://{host}/"}
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, **kw)
        if r.status_code != 200:
            logger.info("[%d] %s", r.status_code, url[:90])
            return None
        return r
    except Exception as e:
        logger.info("[err] %s: %s", url[:80], e)
        return None


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception as e:
        logger.warning("Failed to load %s: %s", path, e)
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def detect_mime(content: bytes) -> str | None:
    if content[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if content[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if content[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return None


def process_image(content: bytes, target_w: int = 480, quality: int = 80) -> tuple[bytes, str] | None:
    """Validate, resize, recompress to JPEG. Returns (bytes, mime) or None."""
    if len(content) < 5000:
        return None
    if detect_mime(content) is None:
        return None
    try:
        from PIL import Image  # lazy import
        img = Image.open(BytesIO(content))
        if img.width < 300 or img.height < 200:
            return None
        ratio = img.width / img.height
        if ratio > 4 or ratio < 0.25:
            return None
        if img.width > target_w:
            new_h = int(img.height * (target_w / img.width))
            img = img.resize((target_w, new_h), Image.LANCZOS)
        if img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            mask = img.split()[-1] if img.mode in ("RGBA", "LA") else None
            bg.paste(img, mask=mask)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        buf = BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True)
        return buf.getvalue(), "image/jpeg"
    except Exception as e:
        logger.info("[PIL] %s", e)
        return None


def to_data_uri(content: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(content).decode('ascii')}"


def fetch_image(url: str, target_w: int = 480) -> tuple[str, int] | None:
    """Fetch + process an image. Returns (data_uri, kb) or None."""
    r = get(url)
    if not r:
        return None
    out = process_image(r.content, target_w=target_w)
    if not out:
        return None
    raw, mime = out
    return to_data_uri(raw, mime), len(raw) // 1024


SKIP_PATTERNS = [
    "logo", "favicon", "icon", "avatar", "profile-pic",
    "loading", "spinner", "placeholder", "blank", "spacer",
    "social", "twitter", "facebook", "instagram-icon", "youtube",
    "wp-emoji", "gravatar", "_thumb_", "thumb-",
    "header.", "footer.", "nav-", "menu-",
]


def looks_like_artwork(url: str) -> bool:
    low = url.lower()
    return not any(p in low for p in SKIP_PATTERNS)


def extract_image_candidates(html: str, base_url: str, max_count: int = 12) -> list[str]:
    """Pull <img>, og:image, srcset URLs from a page. Filter out likely chrome."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    out: list[str] = []
    seen: set[str] = set()

    def add(u: str) -> None:
        full = urljoin(base_url, u)
        if full in seen or not looks_like_artwork(full):
            return
        seen.add(full)
        out.append(full)

    for prop, attr in (("og:image", "property"), ("twitter:image", "name")):
        m = soup.find("meta", {attr: prop})
        if m and m.get("content"):
            add(m["content"])

    for img in soup.find_all("img"):
        src = (img.get("src") or img.get("data-src") or img.get("data-image")
               or img.get("data-lazy-src") or img.get("data-original"))
        if src and not src.startswith("data:"):
            add(src)
        srcset = img.get("srcset") or img.get("data-srcset")
        if srcset:
            largest_url, largest_w = None, 0
            for entry in srcset.split(","):
                parts = entry.strip().split()
                if len(parts) >= 2 and parts[1].endswith("w"):
                    try:
                        w = int(parts[1][:-1])
                        if w > largest_w:
                            largest_w, largest_url = w, parts[0]
                    except ValueError:
                        pass
            if largest_url:
                add(largest_url)

    for src in soup.find_all("source"):
        srcset = src.get("srcset") or src.get("data-srcset")
        if srcset:
            first = srcset.split(",")[0].strip().split()[0]
            add(first)

    return out[:max_count]


def polite_delay(seconds: float = 0.5) -> None:
    time.sleep(seconds)


def extract_og_meta(html: str, base_url: str) -> dict:
    """Pull Open Graph + basic meta tags from a page. Returns dict with keys:
    og_title, og_description, og_image, og_site_name, og_url, html_title.

    Works without auth on Instagram, Facebook, and standard sites — these
    platforms serve OG meta to crawlers even when the rest of the page is
    behind a login wall. Used by the seed-by-URL ingest flow.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    def meta(prop: str, attr: str = "property") -> str | None:
        m = soup.find("meta", {attr: prop})
        if m and m.get("content"):
            return m["content"].strip()
        return None

    out = {
        "og_title": meta("og:title"),
        "og_description": meta("og:description") or meta("description", "name"),
        "og_image": meta("og:image"),
        "og_site_name": meta("og:site_name"),
        "og_url": meta("og:url"),
        "html_title": (soup.title.string.strip() if soup.title and soup.title.string else None),
    }
    if out["og_image"]:
        out["og_image"] = urljoin(base_url, out["og_image"])
    return out


# --- Optional Playwright (headless browser) support ---
#
# Some sources render their content client-side and return a near-empty JS shell
# to plain requests. Mark them `requires_js: true` in data/sources.json (or
# data/manual_seeds.json) to opt into a headless chromium fetch via Playwright.
#
# Playwright is fully optional: if not installed, `rendered_session()` yields
# None and the caller logs a `[skip-js]` line and continues. Install with:
#     .venv/bin/pip install -r requirements-rendered.txt
#     .venv/bin/playwright install chromium

def playwright_available() -> bool:
    """True if `playwright` is importable. Chromium binary presence is
    checked only on first launch (in rendered_session)."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        return False


class RenderedResponse:
    """Minimal shape mimicking requests.Response for the subset we use
    elsewhere — `.text`, `.content`, `.status_code`, `.url`. Keeps the
    BeautifulSoup-based parsers in discover/ingest unchanged."""
    __slots__ = ("text", "content", "status_code", "url")

    def __init__(self, text: str, url: str, status_code: int = 200):
        self.text = text
        self.content = text.encode("utf-8", errors="replace")
        self.status_code = status_code
        self.url = url


_ANTI_BOT_MARKERS = (
    "cf-browser-verification",
    "checking your browser",
    "attention required! | cloudflare",
    "just a moment",
    "captcha",
    "access denied",
    "request blocked",
    "automated traffic",
    "blocked by perimeterx",
)


def _looks_like_block_page(html: str) -> bool:
    """Detect anti-bot interstitials. Only flags small bodies to avoid
    false positives on real pages that mention these phrases in passing."""
    if len(html) >= 50_000:
        return False
    low = html.lower()
    return any(m in low for m in _ANTI_BOT_MARKERS)


class RenderedFetcher:
    """Holds a chromium browser context open for the lifetime of a pipeline
    step. One context, one page per fetch, page closed after each call."""

    def __init__(self, pw, browser, context):
        self._pw = pw
        self._browser = browser
        self._context = context

    def fetch(
        self,
        url: str,
        timeout_ms: int = 30000,
        wait_until: str = "load",
        min_bytes: int = 1500,
        settle_ms: int = 2500,
    ) -> RenderedResponse | None:
        """Render `url` and return the post-JS DOM.

        Defaults are tuned for SPA-heavy art-org sites:
          wait_until="load" — networkidle is too strict; many sites keep
            long-polling/analytics connections open and never go idle.
          settle_ms=2500 — empirically catches React/Vue hydration on
            sites where the load event fires before the framework renders.
          min_bytes=1500 — JS shells are typically <1500 bytes; rendered
            content is 20KB+. Filters out cases where settle wasn't enough.
        """
        page = self._context.new_page()
        try:
            page.goto(url, timeout=timeout_ms, wait_until=wait_until)
            page.wait_for_timeout(settle_ms)
            html = page.content()
        except Exception as e:
            logger.info("[render-err] %s: %s", url[:80], str(e)[:120])
            return None
        finally:
            page.close()

        if len(html) < min_bytes:
            logger.info("[render-thin] %s: %d bytes", url[:80], len(html))
            return None
        if _looks_like_block_page(html):
            logger.info("[render-block] %s: anti-bot interstitial detected", url[:80])
            return None
        return RenderedResponse(html, url)


def rendered_session(headless: bool = True):
    """Context manager yielding a RenderedFetcher or None if Playwright is
    unavailable. Never raises — graceful degradation is the contract.

    Usage:
        with rendered_session() as rf:
            if rf is None:
                continue  # caller decides how to handle
            resp = rf.fetch(url)
    """
    from contextlib import contextmanager

    @contextmanager
    def _impl():
        if not playwright_available():
            logger.warning(
                "[playwright] not installed — requires_js sources will be skipped. "
                "Install: .venv/bin/pip install -r requirements-rendered.txt && "
                ".venv/bin/playwright install chromium"
            )
            yield None
            return
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        try:
            browser = pw.chromium.launch(headless=headless)
        except Exception as e:
            logger.warning(
                "[playwright] chromium launch failed (%s). "
                "Run: .venv/bin/playwright install chromium",
                str(e)[:120],
            )
            pw.stop()
            yield None
            return
        try:
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1366, "height": 900},
                locale="en-US",
                extra_http_headers={"Accept-Language": HEADERS["Accept-Language"]},
            )
            # Light anti-detection: hide the webdriver flag before page scripts run.
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
            )
            yield RenderedFetcher(pw, browser, context)
        finally:
            try:
                browser.close()
            finally:
                pw.stop()

    return _impl()


_MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}


def parse_event_date(date_raw: str, today=None) -> str | None:
    """Parse a scraped date string to ISO YYYY-MM-DD.

    Handles: "May 9", "May 09, 2026", "5/15", "5/15/2026", "2026-06-01".
    For dates without a year, assumes current year; if that puts the date
    in the past, bumps to next year (calendars surface upcoming events).
    Returns None for strings it can't parse.
    """
    if not date_raw:
        return None
    from datetime import date
    today = today or date.today()
    s = date_raw.strip()

    # ISO: 2026-05-15
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # MM/DD or MM/DD/YYYY (or YY)
    m = re.match(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", s)
    if m:
        try:
            month, day = int(m.group(1)), int(m.group(2))
            year_str = m.group(3)
            year = int(year_str) if year_str else today.year
            if year < 100:
                year += 2000
            d = date(year, month, day)
            if not year_str and d < today:
                d = date(today.year + 1, month, day)
            return d.isoformat()
        except ValueError:
            return None

    # "May 9" / "May 09, 2026" / "September 1"
    m = re.match(r"^([A-Za-z]+)\.?\s+(\d{1,2})(?:,\s*(\d{4}))?", s)
    if m:
        month_str = m.group(1).lower()
        if month_str not in _MONTH_MAP:
            return None
        try:
            month = _MONTH_MAP[month_str]
            day = int(m.group(2))
            year_str = m.group(3)
            year = int(year_str) if year_str else today.year
            d = date(year, month, day)
            if not year_str and d < today:
                d = date(today.year + 1, month, day)
            return d.isoformat()
        except ValueError:
            return None

    return None
