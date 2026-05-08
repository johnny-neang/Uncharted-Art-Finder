"""Scan event sources for upcoming Sacramento art events."""
from __future__ import annotations

import argparse
import re
from datetime import date, datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .common import (
    DATA, get, load_json, logger, polite_delay, save_json, setup_logging,
)


DATE_PATTERNS = [
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+\d{1,2}(?:,\s*\d{4})?",
    r"\d{1,2}/\d{1,2}(?:/\d{2,4})?",
    r"\d{4}-\d{2}-\d{2}",
]
DATE_RE = re.compile("|".join(DATE_PATTERNS), re.I)


def extract_events_from_page(html: str, base: str, source_name: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict] = []
    seen_titles: set[str] = set()

    # Scan headings + adjacent text for event-like patterns
    for el in soup.find_all(["article", "li", "div"]):
        text = el.get_text(" ", strip=True)
        if len(text) < 20 or len(text) > 600:
            continue
        # must contain a date pattern
        m = DATE_RE.search(text)
        if not m:
            continue

        title_el = el.find(["h1", "h2", "h3", "h4", "a"])
        title = title_el.get_text(strip=True) if title_el else text[:80]
        if len(title) < 6 or len(title) > 140:
            continue
        if title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())

        link = el.find("a", href=True)
        url = urljoin(base, link["href"]) if link else base

        events.append({
            "title": title.strip(),
            "date_raw": m.group(0),
            "snippet": text[:280].strip(),
            "url": url,
            "source": source_name,
        })

    return events[:30]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    sources = load_json(DATA / "sources.json", {}).get("event_sources", [])
    out: list[dict] = []

    for src in sources:
        logger.info("=== events: %s ===", src["name"])
        r = get(src["url"])
        if not r:
            continue
        try:
            evts = extract_events_from_page(r.text, src["url"], src["name"])
        except Exception as e:
            logger.warning("parse failed %s: %s", src["name"], e)
            continue
        logger.info("  %d events", len(evts))
        out.extend(evts)
        polite_delay(1.0)

    # De-dupe by title
    deduped: list[dict] = []
    seen: set[str] = set()
    for e in out:
        key = e["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    save_json(DATA / "events.json", {
        "events": deduped,
        "last_run": str(date.today()),
    })
    logger.info("[done] %d unique events", len(deduped))
    return deduped


if __name__ == "__main__":
    main()
