"""Command-line interface entry point for web-search."""

import argparse
import math
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
            console.input("\n[dim]Press Enter to return to results...[/dim]")
            return

    display_article(
        title=result.title,
        url=result.url,
        markdown_content=markdown,
    )


def interactive_session(
    initial_results: Optional[List[SearchResult]] = None,
    initial_query: str = "",
    max_results: int = 10,
    page_size: int = 5,
) -> None:
    """Run the interactive search and navigation REPL loop.

    Args:
        initial_results: Pre-fetched search results from CLI query if any.
        initial_query: The search query string for the initial results.
        max_results: Default count of search results to fetch per query.
        page_size: Number of results displayed per page.
    """
    current_results = initial_results or []
    current_query = initial_query
    current_page = 1

    while True:
        try:
            prompt_str = (
                "\n[bold cyan]web-search[/bold cyan] "
                "[dim](topic, #, n, p, :b #, :h, :q)[/dim] > "
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

        # Handle next page navigation
        if lowered in ("n", "next"):
            if not current_results:
                print_warning("No active search results. Enter a topic first.")
                continue
            total_pages = max(1, math.ceil(len(current_results) / page_size))
            if current_page < total_pages:
                current_page += 1
                display_results(
                    current_results,
                    current_query,
                    page=current_page,
                    page_size=page_size,
                )
            else:
                print_warning("You are already on the last page of results.")
            continue

        # Handle previous page navigation
        if lowered in ("p", "prev", "previous"):
            if not current_results:
                print_warning("No active search results. Enter a topic first.")
                continue
            if current_page > 1:
                current_page -= 1
                display_results(
                    current_results,
                    current_query,
                    page=current_page,
                    page_size=page_size,
                )
            else:
                print_warning("You are already on the first page of results.")
            continue

        # Handle redisplay of current results
        if lowered in ("r", "results"):
            if current_results:
                display_results(
                    current_results,
                    current_query,
                    page=current_page,
                    page_size=page_size,
                )
            else:
                print_warning("No active search results to display.")
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
                # Redisplay search results cleanly after reading
                if current_results:
                    display_results(
                        current_results,
                        current_query,
                        page=current_page,
                        page_size=page_size,
                    )
            else:
                max_idx = len(current_results)
                print_warning(
                    f"Index {target_idx} not found. "
                    f"Please choose from 1 to {max_idx}."
                )
            continue

        # Treat any other text as a new search query
        query = user_input
        try:
            with console.status(
                f"[cyan]Searching for '{query}'...[/cyan]", spinner="dots"
            ):
                results = search_web(query, max_results=max_results)
        except KeyboardInterrupt:
            console.print("\n[dim]Search cancelled.[/dim]")
            continue
        except Exception as exc:
            print_error(f"Search failed: {exc}")
            continue

        current_results = results
        current_query = query
        current_page = 1
        display_results(
            current_results,
            current_query,
            page=current_page,
            page_size=page_size,
        )


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

        display_results(results, full_query, page=1, page_size=5)

        if not parsed_args.one_shot:
            interactive_session(
                initial_results=results,
                initial_query=full_query,
                max_results=parsed_args.num,
                page_size=5,
            )
    except KeyboardInterrupt:
        console.print("\n[dim]Search cancelled. Exiting.[/dim]")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
