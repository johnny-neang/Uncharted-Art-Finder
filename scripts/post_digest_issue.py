"""Post the day's digest as a GitHub Issue using the GITHUB_TOKEN.

Skips silently if GITHUB_TOKEN or GH_REPO is not set (e.g. local runs).
"""
from __future__ import annotations

import argparse
import os
from datetime import date

import requests

from .common import DIGESTS, logger, setup_logging


def post_issue(repo: str, token: str, title: str, body: str) -> dict | None:
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"title": title, "body": body, "labels": ["digest", "automated"]}
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    if r.status_code in (200, 201):
        data = r.json()
        logger.info("[done] posted issue #%d: %s", data["number"], data["html_url"])
        return data
    logger.warning("Failed to post issue: %d %s", r.status_code, r.text[:300])
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=str(date.today()))
    p.add_argument("--log", default="INFO")
    args = p.parse_args()
    setup_logging(args.log)

    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GH_REPO") or os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        logger.info("GITHUB_TOKEN or GH_REPO not set; skipping issue post")
        return

    md_path = DIGESTS / f"{args.date}.md"
    if not md_path.exists():
        logger.warning("No digest at %s", md_path)
        return
    body = md_path.read_text()

    title = f"Daily Digest · {args.date}"
    post_issue(repo, token, title, body)


if __name__ == "__main__":
    main()
