"""Tests for the web_search.reader module."""

from unittest.mock import MagicMock, patch
import pytest
import requests

from web_search.reader import extract_clean_markdown, fetch_page_content


def test_extract_clean_markdown_strips_unwanted_tags() -> None:
    """Test that script, style, nav, and footer tags are removed."""
    html = """
    <html>
      <head>
        <style>body { color: red; }</style>
        <script>alert('malicious');</script>
      </head>
      <body>
        <nav><a href="/home">Home</a></nav>
        <article>
          <h1>Article Title</h1>
          <p>This is the important main text.</p>
        </article>
        <footer>Copyright 2026</footer>
      </body>
    </html>
    """
    markdown = extract_clean_markdown(html)

    assert "Article Title" in markdown
    assert "This is the important main text." in markdown
    assert "alert('malicious')" not in markdown
    assert "color: red" not in markdown
    assert "Copyright 2026" not in markdown


def test_fetch_page_content_invalid_url() -> None:
    """Test that an invalid or non-HTTP URL raises ValueError."""
    with pytest.raises(ValueError, match="Invalid URL"):
        fetch_page_content("ftp://invalid.com")

    with pytest.raises(ValueError, match="Invalid URL"):
        fetch_page_content("")


def test_fetch_page_content_success() -> None:
    """Test successful page content download and markdown conversion."""
    sample_html = (
        "<html><body><h1>Hello World</h1><p>Test paragraph.</p></body></html>"
    )
    mock_resp = MagicMock()
    mock_resp.text = sample_html
    mock_resp.encoding = "utf-8"
    mock_resp.raise_for_status.return_value = None

    with patch("web_search.reader.requests.get", return_value=mock_resp):
        content = fetch_page_content("https://example.com/test")

        assert "Hello World" in content
        assert "Test paragraph." in content


def test_fetch_page_content_http_error() -> None:
    """Test that HTTP errors raise a RuntimeError."""
    with patch(
        "web_search.reader.requests.get",
        side_effect=requests.RequestException("404 Not Found"),
    ):
        with pytest.raises(RuntimeError, match="Could not load webpage"):
            fetch_page_content("https://example.com/not-found")
