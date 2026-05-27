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
