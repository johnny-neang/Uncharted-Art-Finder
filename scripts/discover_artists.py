"""Scan curated source rosters for *new* artist names not in our canon."""
from __future__ import annotations

import argparse
from datetime import date
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .common import (
    DATA, fetch_image, extract_image_candidates, get, load_json, logger,
    polite_delay, save_json, setup_logging, slugify,
)


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


def discover_from_source(src: dict) -> list[dict]:
    logger.info("=== source: %s ===", src["name"])
    r = get(src["url"])
    if not r:
        return []
    links = extract_artist_links_from_page(r.text, src["url"])
    logger.info("  found %d artist link(s)", len(links))
    for l in links[:15]:
        logger.info("    - %s  ->  %s", l["name"], l["url"][:80])
    return links


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
    for src in sources:
        if src.get("kind") != "roster":
            continue
        try:
            links = discover_from_source(src)[: args.max_per_source]
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
            fresh_links.append(link)
        polite_delay(1.0)

    logger.info("[discover] %d unique fresh links across all rosters", len(fresh_links))

    # Embed images for the first N
    for link in fresh_links[: args.max_new]:
        logger.info("embed image for %s", link["name"])
        img = fetch_candidate_image(link["url"])
        new_candidates.append({
            "slug": link["slug"],
            "name": link["name"],
            "url": link["url"],
            "source_name": link["source_name"],
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
