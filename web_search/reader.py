"""Webpage content reader and cleaner module."""

import logging
from typing import Optional
from bs4 import BeautifulSoup
import html2text
import requests

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
}

DISALLOWED_TAGS = [
    "script",
    "style",
    "noscript",
    "header",
    "footer",
    "nav",
    "aside",
    "form",
    "svg",
    "iframe",
]


def extract_clean_markdown(html_content: str, base_url: str = "") -> str:
    """Clean raw HTML and convert main readable text into Markdown.

    Args:
        html_content: Raw HTML string of the webpage.
        base_url: Base URL for resolving relative links.

    Returns:
        Clean, formatted Markdown string representing main content.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content tags
    for tag in soup(DISALLOWED_TAGS):
        tag.decompose()

    # Look for primary content containers if available
    main_content = (
        soup.find("article")
        or soup.find("main")
        or soup.find(id=lambda v: v and "content" in v.lower())
        or soup.find(class_=lambda v: v and "content" in v.lower())
        or soup.body
        or soup
    )

    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.ignore_images = True
    h2t.ignore_emphasis = False
    h2t.body_width = 80
    h2t.baseurl = base_url

    markdown = h2t.handle(str(main_content))

    # Clean redundant empty lines
    cleaned_lines = []
    prev_blank = False
    for line in markdown.splitlines():
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        cleaned_lines.append(line)
        prev_blank = is_blank

    return "\n".join(cleaned_lines).strip()


def fetch_page_content(
    url: str,
    timeout: Optional[int] = 12,
) -> str:
    """Fetch URL and return clean terminal-readable Markdown.

    Args:
        url: Destination web address.
        timeout: HTTP request timeout in seconds.

    Returns:
        Readable Markdown string of the page contents.

    Raises:
        ValueError: If the URL is empty or invalid.
        RuntimeError: If downloading or parsing fails.
    """
    if not url or not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL provided: {url}")

    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        response.raise_for_status()

        # Handle encoding properly
        if response.encoding is None:
            response.encoding = "utf-8"

        return extract_clean_markdown(response.text, base_url=url)

    except requests.RequestException as exc:
        logger.error("Failed to fetch %s: %s", url, exc)
        raise RuntimeError(f"Could not load webpage: {exc}") from exc
