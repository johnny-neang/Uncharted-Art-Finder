"""Fetch real artist images and embed as base64 data URIs.

Tries each artist's pages in order, scraping <img> and og:image candidates,
filtering for high-quality work shots, downloading, resizing, and saving
to artist_images.json.
"""
import base64
import json
import re
import sys
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

ARTISTS = {
    "valenzuela": {
        "name": "Bryan Valenzuela",
        "pages": [
            "http://www.bryanvalenzuela.com/murals",
            "http://www.bryanvalenzuela.com/the-manycolored-threads-that-weave-the-collective-dream",
            "https://www.wideopenwalls.com/artists/bryan-valenzuela",
            "https://comstocksmag.com/article/bryan-valenzuela-finds-meaning-words",
        ],
        "min_width": 500,
    },
    "conrad": {
        "name": "Maren Conrad",
        "pages": [
            "https://www.marenconrad.com/marrs",
            "https://www.marenconrad.com/murals",
            "https://www.marenconrad.com",
            "https://www.wideopenwalls.com/artists/maren-conrad",
        ],
        "min_width": 500,
    },
    "lc_studio": {
        "name": "LC Studio Tutto",
        "pages": [
            "https://www.studio-tutto.com/portfolio",
            "https://www.studio-tutto.com",
            "https://www.studio-tutto.com/murals",
            "https://www.wideopenwalls.com/artists/lin-fei-fei",
        ],
        "min_width": 500,
    },
    "delgado": {
        "name": "Raphael Delgado",
        "pages": [
            "https://artbyraphael.com/murals",
            "https://artbyraphael.com",
            "https://artbyraphael.com/portfolio",
            "https://www.wideopenwalls.com/artists/raphael-delgado",
        ],
        "min_width": 500,
    },
    "garibaldi": {
        "name": "David Garibaldi",
        "pages": [
            "https://garibaldiarts.com/gallery",
            "https://garibaldiarts.com",
            "https://garibaldiarts.com/about",
        ],
        "min_width": 500,
    },
    "king": {
        "name": "Jaya King",
        "pages": [
            "https://www.jayasart.com/muralsbyjaya",
            "https://www.jayasart.com",
            "https://www.jayasart.com/encaustic-paintings",
        ],
        "min_width": 500,
    },
    "grigio": {
        "name": "Grigio Art Consulting",
        "pages": [
            "https://www.grigioart.com/portfolio",
            "https://www.grigioart.com",
            "https://www.grigioart.com/projects",
        ],
        "min_width": 500,
    },
    "di_gregorio": {
        "name": "Jose Di Gregorio",
        "pages": [
            "https://www.josedigregorio.com/work",
            "https://www.josedigregorio.com",
            "https://www.josedigregorio.com/murals",
            "https://www.wideopenwalls.com/artists/jose-di-gregorio",
        ],
        "min_width": 500,
    },
    "crandall_bear": {
        "name": "Micah Crandall-Bear",
        "pages": [
            "http://www.micahcrandallbear.com/paintings",
            "http://www.micahcrandallbear.com",
            "http://www.micahcrandallbear.com/gallery",
        ],
        "min_width": 500,
    },
    "hart": {
        "name": "Gale Hart",
        "pages": [
            "https://galehart.com/sculpture",
            "https://galehart.com",
            "https://galehart.com/paintings",
        ],
        "min_width": 500,
    },
    "taylor": {
        "name": "Stephanie Taylor",
        "pages": [
            "https://stephanietaylorart.com/portfolio/sacramento/",
            "https://stephanietaylorart.com/portfolio",
            "https://stephanietaylorart.com",
        ],
        "min_width": 500,
    },
    "gamez": {
        "name": "Franceska Gamez",
        "pages": [
            "https://brandedarts.com/art/franceska-gamez/",
            "https://franceskagamez.com",
            "https://www.wideopenwalls.com/artists/franceska-gamez",
        ],
        "min_width": 500,
    },
    "burner": {
        "name": "Shaun Burner",
        "pages": [
            "https://brandedarts.com/art/shaun-burner/",
            "https://www.wideopenwalls.com/artists/shaun-burner",
            "https://shaunburner.com",
        ],
        "min_width": 500,
    },
    "kille": {
        "name": "Jeremiah Kille",
        "pages": [
            "https://www.groundswellart.com/groundswell-gallery-at-fort-sutter-hotel-jeremiah-kille",
            "https://www.groundswellart.com/jeremiah-kille",
            "https://jeremiahkille.com",
        ],
        "min_width": 500,
    },
    "padilla": {
        "name": "Anthony Padilla",
        "pages": [
            "http://www.kinetikideas.com/portfolio",
            "http://www.kinetikideas.com",
            "https://www.wideopenwalls.com/artists/anthony-padilla",
        ],
        "min_width": 500,
    },
    "huerta": {
        "name": "John S. Huerta",
        "pages": [
            "https://viva-frida.com/gallery",
            "https://viva-frida.com",
            "https://viva-frida.com/about",
        ],
        "min_width": 500,
    },
    "horner": {
        "name": "Waylon Horner",
        "pages": [
            "https://brandedarts.com/portfolio_page/waylon-horner/",
            "https://www.wideopenwalls.com/artists/waylon-horner",
            "https://waylonhorner.com",
        ],
        "min_width": 500,
    },
    "skinner": {
        "name": "Skinner",
        "pages": [
            "https://www.theartofskinner.com/murals",
            "https://www.theartofskinner.com/paintings",
            "https://www.theartofskinner.com",
        ],
        "min_width": 500,
    },
    "groundswell": {
        "name": "Groundswell Art",
        "pages": [
            "https://www.groundswellart.com/eleanor",
            "https://www.groundswellart.com/projects",
            "https://www.groundswellart.com",
        ],
        "min_width": 500,
    },
    "wow": {
        "name": "Wide Open Walls",
        "pages": [
            "https://www.wideopenwalls.com/about",
            "https://www.wideopenwalls.com",
            "https://www.wideopenwalls.com/festival",
        ],
        "min_width": 500,
    },
    "ninedot": {
        "name": "NINE dot ARTS",
        "pages": [
            "https://ninedotarts.com/projects",
            "https://ninedotarts.com",
            "https://ninedotarts.com/about",
        ],
        "min_width": 500,
    },
}

SKIP_PATTERNS = [
    "logo", "favicon", "icon", "avatar", "profile-pic",
    "loading", "spinner", "placeholder", "blank", "spacer",
    "social", "twitter", "facebook", "instagram-icon", "youtube",
    "wp-emoji", "gravatar", "_thumb_", "thumb-",
    "header.", "footer.", "nav-", "menu-",
]


def looks_like_artwork(url):
    """Filter out clearly non-artwork images."""
    low = url.lower()
    return not any(p in low for p in SKIP_PATTERNS)


def get_images_from_page(url, max_count=12):
    """Scrape candidate image URLs from a page."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            print(f"    [{r.status_code}] {url}")
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        candidates = []
        seen = set()

        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            full = urljoin(url, og["content"])
            if full not in seen and looks_like_artwork(full):
                candidates.append(full)
                seen.add(full)

        twitter = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter and twitter.get("content"):
            full = urljoin(url, twitter["content"])
            if full not in seen and looks_like_artwork(full):
                candidates.append(full)
                seen.add(full)

        for img in soup.find_all("img"):
            src = (img.get("src") or img.get("data-src") or img.get("data-image")
                   or img.get("data-lazy-src") or img.get("data-original"))
            if not src or src.startswith("data:"):
                continue
            full = urljoin(url, src)
            if full in seen or not looks_like_artwork(full):
                continue
            candidates.append(full)
            seen.add(full)

            srcset = img.get("srcset") or img.get("data-srcset")
            if srcset:
                largest_url = None
                largest_w = 0
                for entry in srcset.split(","):
                    parts = entry.strip().split()
                    if len(parts) >= 2 and parts[1].endswith("w"):
                        try:
                            w = int(parts[1][:-1])
                            if w > largest_w:
                                largest_w = w
                                largest_url = urljoin(url, parts[0])
                        except ValueError:
                            pass
                if largest_url and largest_url not in seen and looks_like_artwork(largest_url):
                    candidates.insert(0, largest_url)
                    seen.add(largest_url)

        for src in soup.find_all("source"):
            srcset = src.get("srcset") or src.get("data-srcset")
            if srcset:
                first = srcset.split(",")[0].strip().split()[0]
                full = urljoin(url, first)
                if full not in seen and looks_like_artwork(full):
                    candidates.append(full)
                    seen.add(full)

        return candidates[:max_count]
    except Exception as e:
        print(f"    [ERR scraping] {url}: {e}")
        return []


def download_and_validate(url, min_width=500):
    """Download an image, validate it's a real artwork shot, resize, return (bytes, mime)."""
    try:
        host = urlparse(url).netloc
        headers = {**HEADERS, "Referer": f"https://{host}/"}
        r = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            return None
        content = r.content
        if len(content) < 8000:
            return None

        if content[:3] == b"\xff\xd8\xff":
            mime = "image/jpeg"
        elif content[:8] == b"\x89PNG\r\n\x1a\n":
            mime = "image/png"
        elif content[:6] in (b"GIF87a", b"GIF89a"):
            mime = "image/gif"
        elif content[:4] == b"RIFF" and content[8:12] == b"WEBP":
            mime = "image/webp"
        else:
            return None

        try:
            img = Image.open(BytesIO(content))
            if img.width < min_width or img.height < 300:
                return None
            ratio = img.width / img.height
            if ratio > 4 or ratio < 0.25:
                return None

            target_w = 480
            if img.width > target_w:
                new_h = int(img.height * (target_w / img.width))
                img = img.resize((target_w, new_h), Image.LANCZOS)

            if img.mode in ("RGBA", "P", "LA"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")

            buf = BytesIO()
            img.save(buf, "JPEG", quality=80, optimize=True)
            content = buf.getvalue()
            mime = "image/jpeg"
        except Exception as e:
            print(f"    [PIL err] {e}")
            return None

        return (content, mime)
    except Exception as e:
        print(f"    [DL err] {url[:60]}: {e}")
        return None


def to_data_uri(content, mime):
    b64 = base64.b64encode(content).decode("ascii")
    return f"data:{mime};base64,{b64}"


def main():
    out_path = Path("artist_images.json")
    results = {}
    if out_path.exists():
        results = json.loads(out_path.read_text())
        print(f"Resuming with {sum(len(r['images']) for r in results.values())} images already cached")

    for slug, info in ARTISTS.items():
        if slug in results and len(results[slug].get("images", [])) >= 2:
            print(f"\n=== {info['name']} (cached, skipping) ===")
            continue

        print(f"\n=== {info['name']} ===")
        embedded = results.get(slug, {}).get("images", [])
        existing_urls = {im["source_url"] for im in embedded}

        for page in info["pages"]:
            if len(embedded) >= 2:
                break
            print(f"  Scraping {page}")
            candidates = get_images_from_page(page)
            for img_url in candidates:
                if len(embedded) >= 2:
                    break
                if img_url in existing_urls:
                    continue
                print(f"    Try: {img_url[:90]}")
                result = download_and_validate(img_url, info.get("min_width", 500))
                if result:
                    content, mime = result
                    embedded.append({
                        "data_uri": to_data_uri(content, mime),
                        "source_url": img_url,
                        "source_page": page,
                    })
                    existing_urls.add(img_url)
                    print(f"    OK ({len(content)//1024}KB)")
            time.sleep(0.5)

        results[slug] = {"name": info["name"], "images": embedded}
        out_path.write_text(json.dumps(results, indent=2))
        print(f"  -> {len(embedded)} images for {info['name']}")

    total = sum(len(r["images"]) for r in results.values())
    print(f"\n[done] {total} images saved to {out_path}")
    for slug, info in ARTISTS.items():
        n = len(results.get(slug, {}).get("images", []))
        marker = "OK" if n >= 2 else ("partial" if n == 1 else "MISS")
        print(f"  {marker:8} {info['name']}: {n}/2")


if __name__ == "__main__":
    main()
