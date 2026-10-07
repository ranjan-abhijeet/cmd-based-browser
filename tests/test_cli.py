"""Tests for the web_search.cli module."""

from unittest.mock import patch

from web_search.cli import (
    main,
    open_in_browser,
    parse_arguments,
)
from web_search.searcher import SearchResult


def test_parse_arguments_multi_word_query() -> None:
    """Test parsing multi-word queries without quotes."""
    args = parse_arguments(["quantum", "computing", "breakthroughs"])
    assert args.query == ["quantum", "computing", "breakthroughs"]
    assert args.num == 10
    assert not args.one_shot


def test_parse_arguments_custom_flags() -> None:
    """Test custom flags for result count and one-shot mode."""
    args = parse_arguments(["machine", "learning", "-n", "5", "--one-shot"])
    assert args.query == ["machine", "learning"]
    assert args.num == 5
    assert args.one_shot is True


def test_open_in_browser_invokes_webbrowser() -> None:
    """Test that open_in_browser calls python webbrowser.open."""
    with patch("web_search.cli.webbrowser.open") as mock_open:
        open_in_browser("https://example.com")
        mock_open.assert_called_once_with("https://example.com")


def test_main_one_shot_execution() -> None:
    """Test executing main() in one-shot mode with mocked searcher."""
    mock_results = [
        SearchResult(
            index=1,
            title="Test Result",
            url="https://example.com",
            snippet="A test snippet.",
        )
    ]

    with patch(
        "web_search.cli.search_web", return_value=mock_results
    ) as mock_search, patch("web_search.cli.display_results") as mock_display:

        exit_code = main(["quantum", "computing", "--one-shot"])

        assert exit_code == 0
        mock_search.assert_called_once_with(
            "quantum computing", max_results=10
        )
        mock_display.assert_called_once_with(mock_results, "quantum computing")


def test_main_search_error_returns_one() -> None:
    """Test that main returns exit code 1 if search fails in one-shot mode."""
    with patch(
        "web_search.cli.search_web", side_effect=RuntimeError("Search error")
    ):
        exit_code = main(["failing", "query", "--one-shot"])
        assert exit_code == 1
