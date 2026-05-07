"""Swap stylized SVGs in sacramento-artist-directory-with-photos.html
for real photographs.

Two ways to provide images:

1) Drop files into local_files/<slug>-1.<ext> and <slug>-2.<ext>
   (e.g. local_files/valenzuela-1.jpg, local_files/conrad-2.png).

2) Run fetch_artist_images.py first to produce artist_images.json.

Either source is fine; the script merges both, with local_files taking
precedence over JSON.

The output is a *new* file:
   sacramento-artist-directory-with-photos.LOCAL.html

Original SVG art is preserved in the source — re-running with new
photos always starts from the master SVG file.
"""
import base64
import json
import re
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "sacramento-artist-directory-with-photos.html"
DST = ROOT / "sacramento-artist-directory-with-photos.LOCAL.html"
LOCAL_DIR = ROOT / "local_files"
JSON_PATH = ROOT / "artist_images.json"

SLUGS = [
    "valenzuela", "conrad", "lc_studio", "delgado", "garibaldi", "king", "grigio",
    "di_gregorio", "crandall_bear", "hart", "taylor", "gamez", "burner",
    "kille", "padilla", "huerta", "horner", "skinner",
    "groundswell", "wow", "ninedot",
]

# Maps an artist slug -> the two SVG keys used in the dashboard.
SLUG_TO_SVG_KEYS = {
    "valenzuela":     ("valenzuela_text",      "valenzuela_orbs"),
    "conrad":         ("conrad_koi",           "conrad_ladybird"),
    "lc_studio":      ("lc_underbelly",        "lc_treememory"),
    "delgado":        ("delgado_bear",         "delgado_cubist"),
    "garibaldi":      ("garibaldi_live",       "garibaldi_pop"),
    "king":           ("king_tapestry",        "king_encaustic"),
    "grigio":         ("grigio_curated",       "grigio_healthcare"),
    "di_gregorio":    ("digregorio_kaleido",   "digregorio_celestial"),
    "crandall_bear":  ("crandall_field",       "crandall_horizon"),
    "hart":           ("hart_missingmark",     "hart_popsculpt"),
    "taylor":         ("taylor_dance",         "taylor_historic"),
    "gamez":          ("gamez_phoenix",        "gamez_floral"),
    "burner":         ("burner_jazz",          "burner_symbolist"),
    "kille":          ("kille_elephant",       "kille_balloons"),
    "padilla":        ("padilla_character",    "padilla_color"),
    "huerta":         ("huerta_frida",         "huerta_diamuertos"),
    "horner":         ("horner_cartoon",       "horner_surreal"),
    "skinner":        ("skinner_creature",     "skinner_pop"),
    "groundswell":    ("groundswell_gallery",  "groundswell_clean"),
    "wow":            ("wow_muralcity",        "wow_festival"),
    "ninedot":        ("ninedot_logo",         "ninedot_placemaking"),
}

EXT_TO_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
}


def file_to_data_uri(path: Path) -> str | None:
    """Read a local image, optionally resize, return data URI."""
    if not path.exists():
        return None
    mime = EXT_TO_MIME.get(path.suffix.lower())
    if not mime:
        return None
    data = path.read_bytes()
    try:
        from PIL import Image
        img = Image.open(BytesIO(data))
        target_w = 480
        if img.width > target_w:
            new_h = int(img.height * (target_w / img.width))
            img = img.resize((target_w, new_h), Image.LANCZOS)
        if img.mode != "RGB":
            img = img.convert("RGB") if img.mode != "RGBA" else img
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                img = bg
        buf = BytesIO()
        img.save(buf, "JPEG", quality=82, optimize=True)
        data = buf.getvalue()
        mime = "image/jpeg"
    except Exception as e:
        print(f"  [PIL skip resize] {path.name}: {e}")
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def collect_images() -> dict[str, list[str]]:
    """Return {slug: [data_uri_1, data_uri_2]} merging local_files + json."""
    images: dict[str, list[str]] = {s: [None, None] for s in SLUGS}

    if JSON_PATH.exists():
        cache = json.loads(JSON_PATH.read_text())
        for slug, info in cache.items():
            for i, im in enumerate(info.get("images", [])[:2]):
                if im.get("data_uri"):
                    images.setdefault(slug, [None, None])[i] = im["data_uri"]

    if LOCAL_DIR.exists():
        for f in LOCAL_DIR.iterdir():
            if not f.is_file():
                continue
            stem = f.stem.lower()
            for slug in SLUGS:
                for idx in (1, 2):
                    if stem == f"{slug}-{idx}":
                        uri = file_to_data_uri(f)
                        if uri:
                            images[slug][idx - 1] = uri
                            print(f"  local: {slug} #{idx} <- {f.name}")

    return images


def build_img_replacement(svg_key: str, data_uri: str) -> tuple[re.Pattern, str]:
    """Return (regex, replacement) that swaps one inline SVG for an <img>."""
    pattern = re.compile(
        r'(SVG\.' + re.escape(svg_key) + r'\s*=\s*`)[\s\S]*?(`;)',
        re.M,
    )
    new = (
        f'\\1<img src="{data_uri}" '
        f'alt="{svg_key}" '
        f'style="width:100%;height:100%;object-fit:cover;display:block;">\\2'
    )
    return pattern, new


def main():
    if not SRC.exists():
        raise SystemExit(f"missing {SRC}")
    html = SRC.read_text()
    images = collect_images()

    swaps = 0
    misses = []
    for slug in SLUGS:
        keys = SLUG_TO_SVG_KEYS[slug]
        uris = images.get(slug, [None, None])
        for idx, (key, uri) in enumerate(zip(keys, uris)):
            if not uri:
                misses.append((slug, idx + 1, key))
                continue
            pat, rep = build_img_replacement(key, uri)
            new_html, n = pat.subn(rep, html, count=1)
            if n:
                html = new_html
                swaps += 1
                print(f"  ok: {slug} #{idx+1} ({key}) -> photo ({len(uri)//1024}KB)")
            else:
                print(f"  WARN: pattern miss for {key}")

    DST.write_text(html)
    print()
    print(f"[done] {swaps}/42 photo swaps; {len(misses)} kept as SVG")
    print(f"[out]  {DST.relative_to(ROOT)}  ({DST.stat().st_size//1024}KB)")
    if misses:
        print("[svg-fallback]")
        for slug, idx, key in misses:
            print(f"  {slug:14} #{idx}  ({key})")


if __name__ == "__main__":
    main()
