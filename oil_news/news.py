"""Fetch oil headlines from Google News and keep only the prominent ones."""

import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

import feedparser

from . import config

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def score_headline(title: str) -> int:
    """Add up keyword weights found in the headline (case-insensitive)."""
    text = title.lower()
    return sum(weight for word, weight in config.KEYWORDS.items() if word in text)


def _normalize(title: str) -> str:
    """Turn a headline into a simple key so near-duplicates match.

    Google News appends " - Publisher" to titles, so we drop that first.
    """
    title = title.rsplit(" - ", 1)[0]
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def fetch_headlines(queries=None) -> list[dict]:
    """Download headlines for each search query. Returns a list of dicts."""
    queries = queries or config.SEARCH_QUERIES
    items = []
    for query in queries:
        feed = feedparser.parse(GOOGLE_NEWS_RSS.format(query=quote_plus(query)))
        for entry in feed.entries:
            if not getattr(entry, "published_parsed", None):
                continue
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            items.append({
                "title": entry.title,
                "link": entry.link,
                "source": getattr(getattr(entry, "source", None), "title", ""),
                "published": published,
            })
    return items


def pick_prominent(items: list[dict], min_score: int | None = None) -> list[dict]:
    """Score, filter and de-duplicate headlines. Newest first."""
    min_score = config.MIN_SCORE if min_score is None else min_score
    seen = set()
    result = []
    for item in sorted(items, key=lambda i: i["published"]):
        key = _normalize(item["title"])
        if key in seen:
            continue
        seen.add(key)
        score = score_headline(item["title"])
        if score >= min_score:
            result.append({**item, "score": score})
    return sorted(result, key=lambda i: i["published"], reverse=True)
