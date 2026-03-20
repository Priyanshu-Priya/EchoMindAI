"""
Content detector — infer content type from user input and extract URLs.
"""

import re
from typing import Optional

import httpx

from bot.core.logger import log


# URL extraction pattern
_URL_REGEX = re.compile(
    r'https?://[^\s<>"\')\]]+',
    re.IGNORECASE,
)

# Domain → content type mapping
_DOMAIN_TYPE_MAP = {
    # Video
    "youtube.com": "video",
    "youtu.be": "video",
    "vimeo.com": "video",
    # Podcast
    "open.spotify.com/episode": "podcast",
    "open.spotify.com/show": "podcast",
    "podcasts.apple.com": "podcast",
    "podcasts.google.com": "podcast",
    "overcast.fm": "podcast",
    # Article
    "medium.com": "article",
    "substack.com": "article",
    "dev.to": "article",
    "hackernoon.com": "article",
    "towardsdatascience.com": "article",
    "arxiv.org": "article",
    "blog": "article",
}


def extract_url(text: str) -> Optional[str]:
    """Pull the first URL from the user's input."""
    match = _URL_REGEX.search(text)
    return match.group(0) if match else None


def detect_content_type(text: str, url: Optional[str] = None) -> Optional[str]:
    """Infer content type from the URL domain or text keywords.

    Returns one of: 'video', 'article', 'podcast', 'book', or None
    (None means the AI should decide).
    """
    check_text = url or text
    lower = check_text.lower()

    for domain, content_type in _DOMAIN_TYPE_MAP.items():
        if domain in lower:
            return content_type

    # Keyword heuristics for non-URL inputs
    text_lower = text.lower()
    book_keywords = ["book", "by ", "author", "read ", "novel", "memoir"]
    if any(kw in text_lower for kw in book_keywords):
        return "book"

    podcast_keywords = ["podcast", "episode", "ep."]
    if any(kw in text_lower for kw in podcast_keywords):
        return "podcast"

    return None  # let AI decide


async def fetch_url_metadata(url: str) -> dict:
    """Best-effort fetch of page title from a URL.

    Returns: { 'page_title': str | None }
    """
    result = {"page_title": None}

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=8.0,
            headers={"User-Agent": "ResonanceBot/1.0"},
        ) as client:
            
            # Special handling for YouTube via oEmbed API to prevent hallucination
            if "youtube.com" in url.lower() or "youtu.be" in url.lower():
                oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
                resp = await client.get(oembed_url)
                if resp.status_code == 200:
                    result["page_title"] = resp.json().get("title")
                return result

            # Standard webpage parsing
            resp = await client.get(url)
            resp.raise_for_status()

            # Extract <title> tag
            title_match = re.search(
                r"<title[^>]*>(.*?)</title>",
                resp.text[:5000],
                re.IGNORECASE | re.DOTALL,
            )
            if title_match:
                title = title_match.group(1).strip()
                # Clean up common suffixes
                for sep in [" - YouTube", " | Medium", " — Substack"]:
                    title = title.split(sep)[0].strip()
                result["page_title"] = title

    except Exception as e:
        log.debug("Failed to fetch metadata for %s: %s", url, e)

    return result
