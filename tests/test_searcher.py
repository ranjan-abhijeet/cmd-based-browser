"""Tests for the web_search.searcher module."""

from unittest.mock import MagicMock, patch
import pytest

from web_search.searcher import (
    SearchResult,
    _search_ddgs_api,
    _search_html_fallback,
    search_web,
)


def test_search_result_dataclass() -> None:
    """Test SearchResult dataclass fields and string conversion."""
    result = SearchResult(
        index=1,
        title="Test Title",
        url="https://example.com",
        snippet="A brief test snippet.",
    )
    assert result.index == 1
    assert result.title == "Test Title"
    assert result.url == "https://example.com"
    assert result.snippet == "A brief test snippet."
    assert "[1] Test Title" in str(result)
    assert "https://example.com" in str(result)


def test_search_web_empty_query() -> None:
    """Test that an empty or whitespace query raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        search_web("")

    with pytest.raises(ValueError, match="cannot be empty"):
        search_web("   ")


def test_search_ddgs_api_parsing() -> None:
    """Test that _search_ddgs_api correctly parses raw DDGS items."""
    mock_items = [
        {
            "title": "Quantum Computing 101",
            "href": "https://example.org/quantum",
            "body": "Introductory quantum mechanics and computing.",
        },
        {
            "title": "Quantum Algorithms",
            "href": "https://example.org/algorithms",
            "body": "Shor's and Grover's algorithms.",
        },
    ]

    with patch("web_search.searcher.DDGS") as mock_ddgs_class:
        mock_instance = MagicMock()
        mock_instance.text.return_value = iter(mock_items)
        mock_ddgs_class.return_value.__enter__.return_value = mock_instance

        results = _search_ddgs_api("quantum", max_results=2)

        assert len(results) == 2
        assert results[0].index == 1
        assert results[0].title == "Quantum Computing 101"
        assert results[0].url == "https://example.org/quantum"
        assert "Introductory" in results[0].snippet


def test_search_html_fallback_parsing() -> None:
    """Test parsing HTML response in fallback mode."""
    target_link = "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fpython.org"
    sample_html = f"""
    <html>
      <body>
        <div class="result">
          <a class="result__a" href="{target_link}&rut=1">
            Python Official Site
          </a>
          <a class="result__snippet">The official home of Python.</a>
        </div>
      </body>
    </html>
    """
    mock_response = MagicMock()
    mock_response.text = sample_html
    mock_response.raise_for_status.return_value = None

    with patch(
        "web_search.searcher.requests.post", return_value=mock_response
    ):
        results = _search_html_fallback("python", max_results=5)

        assert len(results) == 1
        assert results[0].title == "Python Official Site"
        assert results[0].url == "https://python.org"
        assert "official home" in results[0].snippet


def test_search_web_fallback_invocation() -> None:
    """Test search_web triggers fallback when DDGS raises an exception."""
    with patch(
        "web_search.searcher._search_ddgs_api",
        side_effect=Exception("DDGS Rate Limit"),
    ), patch(
        "web_search.searcher._search_html_fallback",
        return_value=[
            SearchResult(
                index=1,
                title="Fallback Result",
                url="https://fallback.com",
                snippet="Snippet from fallback.",
            )
        ],
    ):
        results = search_web("test query")
        assert len(results) == 1
        assert results[0].title == "Fallback Result"


def test_search_web_failure_raises_runtime_error() -> None:
    """Test that search_web raises RuntimeError if all methods fail."""
    with patch(
        "web_search.searcher._search_ddgs_api",
        side_effect=Exception("Primary failed"),
    ), patch(
        "web_search.searcher._search_html_fallback",
        side_effect=Exception("Fallback failed"),
    ):
        with pytest.raises(RuntimeError, match="Failed to fetch"):
            search_web("error query")
