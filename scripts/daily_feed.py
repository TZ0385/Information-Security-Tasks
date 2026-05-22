#!/usr/bin/env python3
"""
daily_feed.py — Aggregate infosec news, CVEs, tool releases, Telegram channels,
and X/Twitter security accounts into a daily digest.

Sources:
  - SANS Internet Storm Center
  - The Hacker News
  - Schneier on Security
  - PortSwigger Research
  - NVD High/Critical CVEs
  - KitPloit (tool releases)
  - GitHub trending security repos
  - Telegram security channels (via RSSHub)
  - X/Twitter security accounts (via RSSHub)

Output: feeds/YYYY-MM-DD.md
"""

import json
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
OUT   = Path(__file__).parent.parent / "feeds" / f"{TODAY}.md"

RSS_SOURCES = [
    ("SANS Internet Storm Center",  "https://isc.sans.edu/rssfeed_full.xml",      "news"),
    ("The Hacker News",             "https://feeds.feedburner.com/TheHackersNews", "news"),
    ("Schneier on Security",        "https://www.schneier.com/feed/atom/",         "news"),
    ("KitPloit",                    "https://feeds.feedburner.com/PentestTools",   "tools"),
    ("PortSwigger Research",        "https://portswigger.net/research/rss",        "news"),
]

# Telegram channels via RSSHub (public, no API key needed)
# RSSHub URL: https://rsshub.app/telegram/channel/{channel}
TELEGRAM_CHANNELS = [
    ("vxunderground",     "Malware samples & research",   "community"),
    ("thehackernews",     "The Hacker News",              "community"),
    ("cve_latest",        "Latest CVE alerts",            "community"),
    ("malwrhunterteam",   "Malware Hunter Team",          "community"),
    ("hackers_arise",     "Hackers-Arise",                "community"),
    ("DarkFeedChannel",   "DarkFeed threat intel",        "community"),
]

# X/Twitter accounts via RSSHub (public accounts, no auth)
# RSSHub URL: https://rsshub.app/twitter/user/{username}
TWITTER_ACCOUNTS = [
    ("GossiTheDog",      "Threat intel / ransomware",    "community"),
    ("troyhunt",         "Breaches / HaveIBeenPwned",    "community"),
    ("briankrebs",       "Investigative security news",  "community"),
    ("cyb3rops",         "Sigma / detection engineering","community"),
    ("SwiftOnSecurity",  "Blue team / Windows security", "community"),
    ("vxunderground",    "Malware research",             "community"),
    ("maddiestone",      "Zero-days / exploit research", "community"),
]

RSSHUB_BASE    = "https://rsshub.app"
NITTER_MIRRORS = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.net",
]

NVD_FEED = "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=20&cvssV3Severity=CRITICAL"


def fetch(url: str, timeout: int = 15) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "InfoSec-Tasks-Bot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        print(f"  [skip] {url}: {e}", file=sys.stderr)
        return None


def parse_rss(data: bytes) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # RSS 2.0
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link  = (item.findtext("link")  or "").strip()
            desc  = (item.findtext("description") or "").strip()
            if title and link:
                items.append({"title": title, "link": link, "desc": desc[:200]})

        # Atom
        if not items:
            for entry in root.findall("atom:entry", ns):
                title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                link_el = entry.find("atom:link", ns)
                link = (link_el.get("href") if link_el is not None else "") or ""
                if title and link:
                    items.append({"title": title, "link": link, "desc": ""})

    except ET.ParseError:
        pass
    return items[:8]


def fetch_nvd_critical() -> list[dict]:
    data = fetch(NVD_FEED)
    if not data:
        return []
    try:
        j = json.loads(data)
        cves = []
        for vuln in j.get("vulnerabilities", [])[:10]:
            cve  = vuln.get("cve", {})
            cid  = cve.get("id", "")
            desc = next(
                (d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"),
                ""
            )[:200]
            metrics = cve.get("metrics", {})
            cvss = (
                metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore")
                or metrics.get("cvssMetricV30", [{}])[0].get("cvssData", {}).get("baseScore")
                or "N/A"
            )
            if cid:
                cves.append({"id": cid, "score": cvss, "desc": desc})
        return cves
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


def fetch_github_trending() -> list[dict]:
    data = fetch(
        "https://api.github.com/search/repositories"
        "?q=topic:security+topic:hacking+pushed:>2024-01-01&sort=stars&order=desc&per_page=8",
        timeout=10,
    )
    if not data:
        return []
    try:
        j = json.loads(data)
        repos = []
        for r in j.get("items", [])[:6]:
            repos.append({
                "name":  r["full_name"],
                "url":   r["html_url"],
                "desc":  (r.get("description") or "")[:150],
                "stars": r.get("stargazers_count", 0),
            })
        return repos
    except (json.JSONDecodeError, KeyError):
        return []


def fetch_telegram_feeds() -> list[tuple[str, str, list[dict]]]:
    """Fetch Telegram channels via RSSHub. Returns list of (channel, label, items)."""
    results = []
    for channel, label, _ in TELEGRAM_CHANNELS:
        url = f"{RSSHUB_BASE}/telegram/channel/{channel}"
        data = fetch(url, timeout=12)
        if not data:
            continue
        items = parse_rss(data)
        if items:
            results.append((channel, label, items[:5]))
    return results


def fetch_twitter_feeds() -> list[tuple[str, str, list[dict]]]:
    """Fetch X/Twitter accounts via RSSHub with Nitter fallback."""
    results = []
    for username, label, _ in TWITTER_ACCOUNTS:
        items = []
        # Try RSSHub first
        data = fetch(f"{RSSHUB_BASE}/twitter/user/{username}", timeout=12)
        if data:
            items = parse_rss(data)
        # Fallback: try Nitter mirrors
        if not items:
            for mirror in NITTER_MIRRORS:
                data = fetch(f"{mirror}/{username}/rss", timeout=10)
                if data:
                    items = parse_rss(data)
                    if items:
                        break
        if items:
            results.append((username, label, items[:4]))
    return results


def build_digest() -> str:
    lines = [
        f"# InfoSec Daily Digest — {TODAY}",
        "",
        f"> Auto-generated · [submit a resource]"
        f"(https://github.com/bb1nfosec/Information-Security-Tasks/issues/new"
        f"?template=submit-resource.yml)",
        "",
    ]

    # ── News ─────────────────────────────────────────────────────────────────
    lines += ["## Security News\n"]
    news_count = 0
    for name, url, category in RSS_SOURCES:
        if category != "news":
            continue
        data = fetch(url)
        if not data:
            continue
        items = parse_rss(data)
        if items:
            lines.append(f"### {name}\n")
            for item in items:
                lines.append(f"- [{item['title']}]({item['link']})")
            lines.append("")
            news_count += len(items)
    if news_count == 0:
        lines += ["_No news fetched today._\n"]

    # ── Critical CVEs ─────────────────────────────────────────────────────────
    lines += ["## Critical CVEs\n"]
    cves = fetch_nvd_critical()
    if cves:
        lines.append("| CVE | CVSS | Summary |")
        lines.append("|-----|------|---------|")
        for c in cves:
            cve_link = f"https://nvd.nist.gov/vuln/detail/{c['id']}"
            lines.append(f"| [{c['id']}]({cve_link}) | {c['score']} | {c['desc']} |")
        lines.append("")
    else:
        lines += ["_CVE feed unavailable today._\n"]

    # ── Tools ─────────────────────────────────────────────────────────────────
    lines += ["## New Tools & Releases\n"]
    tools_count = 0
    for name, url, category in RSS_SOURCES:
        if category != "tools":
            continue
        data = fetch(url)
        if not data:
            continue
        items = parse_rss(data)
        if items:
            for item in items:
                lines.append(f"- [{item['title']}]({item['link']})")
            lines.append("")
            tools_count += len(items)

    repos = fetch_github_trending()
    if repos:
        lines.append("### Trending on GitHub\n")
        for r in repos:
            lines.append(f"- [{r['name']}]({r['url']}) ★{r['stars']} — {r['desc']}")
        lines.append("")

    if tools_count == 0 and not repos:
        lines += ["_No tool releases fetched today._\n"]

    # ── Community Feeds ───────────────────────────────────────────────────────
    lines += ["## Community Feeds\n"]
    community_count = 0

    tg_feeds = fetch_telegram_feeds()
    if tg_feeds:
        lines.append("### Telegram Channels\n")
        for channel, label, items in tg_feeds:
            lines.append(f"**{label}** (@{channel})\n")
            for item in items:
                lines.append(f"- [{item['title']}]({item['link']})")
            lines.append("")
            community_count += len(items)

    tw_feeds = fetch_twitter_feeds()
    if tw_feeds:
        lines.append("### X / Twitter\n")
        for username, label, items in tw_feeds:
            lines.append(f"**{label}** (@{username})\n")
            for item in items:
                lines.append(f"- [{item['title']}]({item['link']})")
            lines.append("")
            community_count += len(items)

    if community_count == 0:
        lines += ["_Community feeds unavailable today (RSSHub/Nitter may be rate-limited)._\n"]

    lines += [
        "---",
        "",
        "_Sources: SANS ISC · The Hacker News · Schneier on Security · "
        "PortSwigger Research · KitPloit · NVD · GitHub · "
        "Telegram (RSSHub) · X/Twitter (RSSHub/Nitter)_",
    ]
    return "\n".join(lines) + "\n"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Building digest → {OUT}", file=sys.stderr)
    content = build_digest()
    OUT.write_text(content, encoding="utf-8")
    print(f"Written: {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
