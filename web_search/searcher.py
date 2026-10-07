"""Web search engine interface using DuckDuckGo with fallback mechanisms."""

from dataclasses import dataclass
import logging
from typing import List, Optional
import urllib.parse
from bs4 import BeautifulSoup
import requests

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None  # type: ignore

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


@dataclass
class SearchResult:
    """Represents a single search result entry."""

    index: int
    title: str
    url: str
    snippet: str

    def __str__(self) -> str:
        """Return a string summary of the result."""
        return f"[{self.index}] {self.title}\n{self.url}\n{self.snippet}"


def _search_ddgs_api(query: str, max_results: int) -> List[SearchResult]:
    """Search using duckduckgo_search DDGS library.

    Args:
        query: The search term or question.
        max_results: Maximum number of results to fetch.

    Returns:
        List of SearchResult objects.
    """
    if DDGS is None:
        raise RuntimeError("duckduckgo_search package is not installed.")

    results: List[SearchResult] = []
    with DDGS() as ddgs:
        raw_results = list(ddgs.text(query, max_results=max_results))
        for idx, item in enumerate(raw_results, start=1):
            title = item.get("title", "").strip()
            url = item.get("href", "").strip()
            snippet = item.get("body", "").strip()
            if title and url:
                results.append(
                    SearchResult(
                        index=idx,
                        title=title,
                        url=url,
                        snippet=snippet,
                    )
                )
    return results


def _search_html_fallback(
    query: str, max_results: int
) -> List[SearchResult]:
    """Fallback search using DuckDuckGo HTML endpoint.

    Args:
        query: The search term or question.
        max_results: Maximum number of results to fetch.

    Returns:
        List of SearchResult objects.
    """
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    resp = requests.post(
        url,
        data=params,
        headers=DEFAULT_HEADERS,
        timeout=10,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    result_elements = soup.select(".result")
    results: List[SearchResult] = []

    for item in result_elements:
        if len(results) >= max_results:
            break

        link_tag = item.select_one(".result__title .result__url, .result__a")
        snippet_tag = item.select_one(".result__snippet")

        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        raw_href = link_tag.get("href", "")

        # Unquote DDG redirect URL if needed
        if "uddg=" in raw_href:
            query_str = urllib.parse.urlparse(raw_href).query
            parsed = urllib.parse.parse_qs(query_str)
            clean_url = parsed.get("uddg", [raw_href])[0]
        else:
            clean_url = raw_href

        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        if title and clean_url and clean_url.startswith("http"):
            results.append(
                SearchResult(
                    index=len(results) + 1,
                    title=title,
                    url=clean_url,
                    snippet=snippet,
                )
            )

    return results


def search_web(
    query: str,
    max_results: int = 10,
    timeout: Optional[int] = 10,
) -> List[SearchResult]:
    """Execute a web search for the given query.

    Attempts primary retrieval via DDGS, falling back to direct
    HTML scraping if an exception occurs.

    Args:
        query: Search topic or keywords.
        max_results: Target number of search items.
        timeout: Request timeout in seconds.

    Returns:
        List of SearchResult objects.

    Raises:
        ValueError: If query is empty.
        RuntimeError: If all search attempts fail.
    """
    clean_query = query.strip()
    if not clean_query:
        raise ValueError("Search query cannot be empty.")

    # Try DDGS first
    try:
        results = _search_ddgs_api(clean_query, max_results)
        if results:
            return results
    except Exception as exc:
        logger.warning("Primary DDGS search failed: %s. Trying fallback.", exc)

    # Fallback to HTML parsing
    try:
        results = _search_html_fallback(clean_query, max_results)
        if results:
            return results
    except Exception as exc:
        logger.error("Fallback search failed: %s", exc)
        raise RuntimeError(
            f"Failed to fetch search results for '{clean_query}': {exc}"
        ) from exc

    return []
