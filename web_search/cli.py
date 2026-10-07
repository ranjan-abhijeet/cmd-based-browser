"""Command-line interface entry point for web-search."""

import argparse
import sys
from typing import List, Optional
import webbrowser

from web_search import __version__
from web_search.reader import fetch_page_content
from web_search.searcher import SearchResult, search_web
from web_search.ui import (
    console,
    display_article,
    display_banner,
    display_help,
    display_results,
    print_error,
    print_info,
    print_warning,
)


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Optional list of argument strings. Defaults to sys.argv[1:].

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="web-search",
        description="Command-line internet search tool and text browser.",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help=(
            "Search query topic or question "
            "(e.g. web-search quantum computing)."
        ),
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=10,
        help="Number of search results to return (default: 10).",
    )
    parser.add_argument(
        "--one-shot",
        action="store_true",
        help=(
            "Display search results and exit without opening "
            "interactive prompt."
        ),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args(args)


def open_in_browser(url: str) -> None:
    """Open the specified URL in the system's default web browser.

    Args:
        url: The web URL to open.
    """
    print_info(f"Opening in default browser: {url}")
    try:
        webbrowser.open(url)
    except Exception as exc:
        print_error(f"Failed to open browser: {exc}")


def read_result_article(result: SearchResult) -> None:
    """Fetch and display article text inside the terminal.

    Args:
        result: The search result item to read.
    """
    with console.status(
        f"[cyan]Fetching article content from {result.url}...[/cyan]",
        spinner="dots",
    ):
        try:
            markdown = fetch_page_content(result.url)
        except Exception as exc:
            print_error(f"Could not read webpage: {exc}")
            return

    display_article(
        title=result.title,
        url=result.url,
        markdown_content=markdown,
    )


def interactive_session(
    initial_results: Optional[List[SearchResult]] = None,
    max_results: int = 10,
) -> None:
    """Run the interactive search and navigation REPL loop.

    Args:
        initial_results: Pre-fetched search results from CLI query if any.
        max_results: Default count of search results to fetch per query.
    """
    current_results = initial_results or []

    while True:
        try:
            prompt_str = (
                "\n[bold cyan]web-search[/bold cyan] "
                "[dim](topic, #, :b #, :h, :q)[/dim] > "
            )
            user_input = console.input(prompt_str).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting web-search. Goodbye![/dim]")
            break

        if not user_input:
            continue

        lowered = user_input.lower()

        # Handle exit commands
        if lowered in (":q", "exit", "quit"):
            console.print("[dim]Goodbye![/dim]")
            break

        # Handle help commands
        if lowered in (":h", ":help"):
            display_help()
            continue

        # Handle opening link in external browser: :b <number>
        if lowered.startswith(":b ") or lowered.startswith(":b"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1 and parts[1].strip().isdigit():
                target_idx = int(parts[1].strip())
                matched = next(
                    (r for r in current_results if r.index == target_idx),
                    None,
                )
                if matched:
                    open_in_browser(matched.url)
                else:
                    max_idx = len(current_results)
                    print_warning(
                        f"Index {target_idx} not found. "
                        f"Please choose from 1 to {max_idx}."
                    )
            else:
                print_warning("Usage: :b <number> (e.g. :b 1)")
            continue

        # Handle reading result number directly in terminal
        if user_input.isdigit():
            target_idx = int(user_input)
            matched = next(
                (r for r in current_results if r.index == target_idx),
                None,
            )
            if matched:
                read_result_article(matched)
            else:
                max_idx = len(current_results)
                print_warning(
                    f"Index {target_idx} not found. "
                    f"Please choose from 1 to {max_idx}."
                )
            continue

        # Treat any other text as a new search query
        query = user_input
        with console.status(
            f"[cyan]Searching for '{query}'...[/cyan]", spinner="dots"
        ):
            try:
                results = search_web(query, max_results=max_results)
            except Exception as exc:
                print_error(f"Search failed: {exc}")
                continue

        current_results = results
        display_results(current_results, query)


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint function.

    Args:
        args: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Integer exit code (0 for success).
    """
    parsed_args = parse_arguments(args)
    query_words = parsed_args.query

    if not query_words:
        display_banner()
        display_help()
        interactive_session(max_results=parsed_args.num)
        return 0

    full_query = " ".join(query_words).strip()

    try:
        with console.status(
            f"[cyan]Searching for '{full_query}'...[/cyan]", spinner="dots"
        ):
            try:
                results = search_web(full_query, max_results=parsed_args.num)
            except Exception as exc:
                print_error(f"Search failed: {exc}")
                return 1

        display_results(results, full_query)

        if not parsed_args.one_shot:
            interactive_session(
                initial_results=results, max_results=parsed_args.num
            )
    except KeyboardInterrupt:
        console.print("\n[dim]Search cancelled. Exiting.[/dim]")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
