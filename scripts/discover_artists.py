"""Scan curated source rosters for *new* artist names not in our canon.

Source kinds (data/sources.json `kind` field):
  roster              — gallery roster page; links to /artist/<slug>/-style sub-pages
                        (default, original behavior — strict path filter, same-host only)
  studio              — standalone studio/artist site; the source URL IS the candidate
                        (no link-following, OG meta becomes the candidate)
  community-curator   — page that features Sacramento artists with non-standard URL shapes
                        (relaxed path filter, same-host only, broader name heuristic)
  public-art-registry — same crawl behavior as community-curator
  studio-tour         — same crawl behavior as community-curator
  mfa-program         — same crawl behavior as community-curator
  press               — not crawled here; press feeds aren't reliable artist sources
  any kind with `manual: true` — tracked but not auto-scraped (e.g. Facebook curator pages)
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
from datetime import date
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .common import (
    DATA, fetch_image, extract_image_candidates, extract_og_meta, get,
    load_json, logger, polite_delay, rendered_session, save_json,
    setup_logging, slugify,
)


LOOSE_KINDS = {"community-curator", "public-art-registry", "studio-tour", "mfa-program"}


def _fetch_source(src: dict, rf):
    """Dispatch a source URL to headless render or plain get() based on
    requires_js. Returns the same shape either way (response with .text)."""
    if src.get("requires_js"):
        if rf is None:
            logger.info("[skip-js] %s: requires_js but playwright unavailable", src["name"])
            return None
        return rf.fetch(src["url"])
    return get(src["url"])


def extract_artist_links_from_page(html: str, base: str, host_filter: str | None = None) -> list[dict]:
    """Pull (name, url) pairs from a roster page heuristically.

    Looks for: <a> with text that looks like a person name, leading to a /artist/, /art/,
    /artists/, /portfolio/, or /work/ subpath on the same host.
    """
    soup = BeautifulSoup(html, "html.parser")
    out: list[dict] = []
    seen: set[str] = set()
    base_host = urlparse(base).netloc

    artist_path_hints = ("/artist/", "/artists/", "/art/", "/portfolio_page/", "/portfolio/")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        full = urljoin(base, href)
        host = urlparse(full).netloc
        if host_filter and host_filter not in host:
            continue
        if host != base_host:
            continue
        path = urlparse(full).path
        if not any(h in path for h in artist_path_hints):
            continue
        if path.rstrip("/") in (urlparse(base).path.rstrip("/"),):
            continue

        name = (a.get_text() or "").strip()
        # Heuristic: 2-4 words, looks like a person/agency name
        words = name.split()
        if not (2 <= len(words) <= 5):
            continue
        if any(c.isdigit() for c in name):
            continue
        if name.lower() in ("read more", "view profile", "see more", "learn more"):
            continue

        key = full.rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append({"name": name, "url": full})

    return out


def extract_loose_links_from_page(html: str, base: str) -> list[dict]:
    """Looser link extraction for community-curator / public-art / studio-tour / MFA pages.

    Drops the strict path filter (these pages don't follow /artist/<slug>/ conventions)
    but keeps the same-host check and name heuristic. Will surface more noise — that's
    fine because Claude scoring is the filter that matters.
    """
    soup = BeautifulSoup(html, "html.parser")
    out: list[dict] = []
    seen: set[str] = set()
    base_host = urlparse(base).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full = urljoin(base, href)
        host = urlparse(full).netloc
        if host != base_host:
            continue
        if urlparse(full).path.rstrip("/") in ("", urlparse(base).path.rstrip("/")):
            continue

        name = (a.get_text() or "").strip()
        words = name.split()
        if not (2 <= len(words) <= 5):
            continue
        if any(c.isdigit() for c in name):
            continue
        low = name.lower()
        if low in ("read more", "view profile", "see more", "learn more", "view all", "see all"):
            continue
        # Drop link text that's obviously navigation, not a person/studio
        nav_terms = (
            "home", "about", "contact", "events", "shop", "donate", "subscribe", "menu",
            "studies", "program", "fee", "aid", "advising", "schedule", "transcript",
            "organization", "orientation", "career", "counseling", "campus", "majors",
            "admission", "apply", "enroll", "tuition", "scholarship", "calendar",
            "directory", "library", "athletic", "sport", "club", "housing", "dining",
            "policy", "privacy", "terms", "accessibility", "site map", "sitemap",
        )
        if any(w in low for w in nav_terms):
            continue

        key = full.rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append({"name": name, "url": full})

    return out


def discover_from_source(src: dict, rf) -> list[dict]:
    """Roster-kind discovery: strict path filter + same-host."""
    logger.info("=== source: %s ===", src["name"])
    r = _fetch_source(src, rf)
    if not r:
        return []
    links = extract_artist_links_from_page(r.text, src["url"])
    logger.info("  found %d artist link(s)", len(links))
    for l in links[:15]:
        logger.info("    - %s  ->  %s", l["name"], l["url"][:80])
    return links


def discover_from_loose(src: dict, rf) -> list[dict]:
    """community-curator / public-art-registry / studio-tour / mfa-program."""
    logger.info("=== source [%s]: %s ===", src.get("kind", "?"), src["name"])
    r = _fetch_source(src, rf)
    if not r:
        return []
    links = extract_loose_links_from_page(r.text, src["url"])
    logger.info("  found %d candidate link(s)", len(links))
    for l in links[:15]:
        logger.info("    - %s  ->  %s", l["name"], l["url"][:80])
    return links


def discover_from_studio(src: dict, rf) -> list[dict]:
    """The source URL itself is a single candidate (standalone studio/artist site).

    Pulls the name from OG meta or sources.json `name`. No link-following.
    """
    logger.info("=== source [studio]: %s ===", src["name"])
    r = _fetch_source(src, rf)
    if not r:
        return []
    og = extract_og_meta(r.text, src["url"])
    # Prefer the source's curated name (it's deliberately chosen) over the page's OG title
    name = src["name"] or og.get("og_title") or og.get("html_title") or ""
    name = name.strip()
    if not name:
        logger.warning("  could not derive a name for %s", src["url"])
        return []
    logger.info("    - %s  ->  %s", name, src["url"][:80])
    return [{"name": name, "url": src["url"], "_og": og}]


def fetch_candidate_image(url: str) -> dict | None:
    """Get a representative image for a candidate."""
    r = get(url)
    if not r:
        return None
    for img_url in extract_image_candidates(r.text, url, max_count=8):
        res = fetch_image(img_url)
        if res:
            uri, kb = res
            return {"data_uri": uri, "source_url": img_url, "kb": kb}
        polite_delay(0.2)
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max-per-source", type=int, default=20)
    p.add_argument("--max-new", type=int, default=10, help="how many new candidates to embed")
    p.add_argument("--log", default="INFO")
    args = p.parse_args()

    setup_logging(args.log)

    artists = load_json(DATA / "artists.json", []) or []
    sources = load_json(DATA / "sources.json", {}).get("discovery_sources", [])
    discoveries = load_json(DATA / "discoveries.json", {"candidates": [], "rejected_slugs": []})

    canon_slugs: set[str] = set()
    canon_names: set[str] = set()
    for a in artists:
        canon_slugs.add(a["slug"])
        canon_names.add(a["name"].lower())

    rejected = set(discoveries.get("rejected_slugs", []))
    existing_candidate_slugs = {c["slug"] for c in discoveries.get("candidates", [])}

    new_candidates: list[dict] = []
    fresh_links: list[dict] = []
    needs_browser = any(s.get("requires_js") and not s.get("manual") for s in sources)
    browser_ctx = rendered_session() if needs_browser else nullcontext(None)
    with browser_ctx as rf:
        for src in sources:
            kind = src.get("kind", "roster")
            if src.get("manual"):
                logger.info("[skip-manual] %s (manual:true — tracked but not auto-crawled)", src["name"])
                continue
            try:
                if kind == "roster":
                    links = discover_from_source(src, rf)[: args.max_per_source]
                elif kind == "studio":
                    links = discover_from_studio(src, rf)
                elif kind in LOOSE_KINDS:
                    links = discover_from_loose(src, rf)[: args.max_per_source]
                else:
                    # press, unknown — not crawled here
                    continue
            except Exception as e:
                logger.warning("source %s failed: %s", src["name"], e)
                continue
            for link in links:
                slug = slugify(link["name"])
                if slug in canon_slugs:
                    continue
                if link["name"].lower() in canon_names:
                    continue
                if slug in rejected:
                    continue
                if slug in existing_candidate_slugs:
                    continue
                link["slug"] = slug
                link["source_name"] = src["name"]
                link["source_kind"] = kind
                fresh_links.append(link)
            polite_delay(1.0)

    logger.info("[discover] %d unique fresh links across all sources", len(fresh_links))

    # Embed images for the first N
    for link in fresh_links[: args.max_new]:
        logger.info("embed image for %s", link["name"])
        # studio kind may carry pre-extracted OG meta; use og_image as a shortcut
        og = link.get("_og") or {}
        img = None
        if og.get("og_image"):
            res = fetch_image(og["og_image"])
            if res:
                uri, kb = res
                img = {"data_uri": uri, "source_url": og["og_image"], "kb": kb}
        if img is None:
            img = fetch_candidate_image(link["url"])
        new_candidates.append({
            "slug": link["slug"],
            "name": link["name"],
            "url": link["url"],
            "source_name": link["source_name"],
            "source_kind": link.get("source_kind"),
            "image": img,
            "first_seen": str(date.today()),
            "status": "pending",
        })
        polite_delay(0.5)

    # Merge into existing
    discoveries.setdefault("candidates", [])
    discoveries["candidates"].extend(new_candidates)
    discoveries["last_run"] = str(date.today())
    save_json(DATA / "discoveries.json", discoveries)

    logger.info("[done] added %d new candidates (total queued: %d)",
                len(new_candidates), len(discoveries["candidates"]))
    return new_candidates


if __name__ == "__main__":
    main()
