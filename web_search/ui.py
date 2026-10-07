"""Rich terminal UI presentation components for web-search CLI."""

import math
from typing import List
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from web_search.searcher import SearchResult

console = Console()


def display_banner() -> None:
    """Print the web-search CLI welcome header."""
    header = Text()
    header.append("🔍 Web Search CLI", style="bold cyan")
    header.append(" — Terminal Internet Search & Browser\n", style="dim")
    header.append(
        "Type any topic to search, or a result number to read articles.",
        style="italic",
    )
    console.print(
        Panel(
            header,
            border_style="cyan",
            expand=False,
            padding=(0, 2),
        )
    )


def display_results(
    results: List[SearchResult],
    query: str,
    page: int = 1,
    page_size: int = 5,
    clear_screen: bool = True,
) -> None:
    """Render a page of search results wrapped cleanly to the terminal width.

    Args:
        results: List of SearchResult objects to display.
        query: The search query string for context.
        page: Current page number (1-indexed).
        page_size: Number of results to display per page.
        clear_screen: Whether to clear terminal screen before displaying.
    """
    if clear_screen:
        console.clear()

    if not results:
        no_res_msg = (
            f"[yellow]No results found for '[bold]{query}[/bold]'.[/yellow]"
        )
        console.print(
            Panel(
                no_res_msg,
                border_style="yellow",
            )
        )
        return

    total_results = len(results)
    total_pages = max(1, math.ceil(total_results / page_size))
    current_page = max(1, min(page, total_pages))

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_results)
    page_items = results[start_idx:end_idx]

    # Clean top header with query and page progress
    header = Text()
    header.append("🔍 Search: ", style="bold cyan")
    header.append(f'"{query}"', style="bold white")
    header.append(
        f"  │  Page {current_page} of {total_pages} ",
        style="dim cyan",
    )
    header.append(
        f"({start_idx + 1}-{end_idx} of {total_results})",
        style="dim",
    )

    console.print(
        Panel(
            header,
            border_style="cyan",
            expand=True,
            padding=(0, 1),
        )
    )

    # Responsive table wrapped to terminal width
    table = Table(
        expand=True,
        show_header=False,
        box=None,
        padding=(0, 1),
    )
    table.add_column("Index", style="bold yellow", width=5, justify="right")
    table.add_column(
        "Content",
        style="white",
        ratio=1,
        no_wrap=False,
        overflow="fold",
    )

    for res in page_items:
        details = Text(no_wrap=False, overflow="fold")
        details.append(f"{res.title}\n", style="bold bright_blue")
        details.append(f"{res.url}\n", style="green dim")
        if res.snippet:
            details.append(f"{res.snippet}\n", style="white")

        table.add_row(f"[{res.index}]", details)
        table.add_section()

    console.print(table)

    # Action navigation toolbar
    actions = Text()
    actions.append("Actions: ", style="bold dim")
    actions.append("[#item] ", style="bold yellow")
    actions.append("Read article  ", style="dim")
    if total_pages > 1:
        if current_page < total_pages:
            actions.append("[n] ", style="bold yellow")
            actions.append("Next 5  ", style="dim")
        if current_page > 1:
            actions.append("[p] ", style="bold yellow")
            actions.append("Prev 5  ", style="dim")
    actions.append("[:b #] ", style="bold yellow")
    actions.append("Browser  ", style="dim")
    actions.append("[:q] ", style="bold yellow")
    actions.append("Exit", style="dim")

    console.print(actions)
    console.print()


def display_article(
    title: str,
    url: str,
    markdown_content: str,
    chunk_size: int = 25,
    clear_screen: bool = True,
) -> None:
    """Display article content paged from top to bottom.

    Args:
        title: Title of the article or search result.
        url: Original webpage URL.
        markdown_content: Clean markdown text of the webpage.
        chunk_size: Number of lines to display per screen page.
        clear_screen: Whether to clear screen for each page.
    """
    if clear_screen:
        console.clear()

    console.rule(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"[dim green]Source: {url}[/dim green]\n")

    if not markdown_content.strip():
        console.print(
            "[italic yellow]No readable text could be extracted "
            "from this page.[/italic yellow]"
        )
        console.input("\n[dim]Press Enter to return to results...[/dim]")
        return

    lines = markdown_content.splitlines()
    total_lines = len(lines)

    if total_lines <= chunk_size:
        console.print(Markdown(markdown_content))
        console.rule("[bold cyan]End of Article[/bold cyan]")
        console.input("\n[dim]Press Enter to return to results...[/dim]")
        return

    # Multi-page article reading
    chunks = [
        lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)
    ]
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks, start=1):
        if clear_screen and idx > 1:
            console.clear()
            page_info = f"[dim](Page {idx}/{total_chunks})[/dim]"
            console.rule(f"[bold cyan]{title}[/bold cyan] {page_info}")
            console.print(f"[dim green]Source: {url}[/dim green]\n")

        chunk_text = "\n".join(chunk)
        console.print(Markdown(chunk_text))

        if idx < total_chunks:
            prompt_text = (
                f"\n[dim]-- Page {idx}/{total_chunks}: "
                "Press Enter for next page, or type 'q' to return --[/dim] "
            )
            try:
                user_choice = console.input(prompt_text).strip().lower()
            except (KeyboardInterrupt, EOFError):
                break
            if user_choice in ("q", "quit", "exit"):
                break
        else:
            console.rule("[bold cyan]End of Article[/bold cyan]")
            try:
                console.input(
                    "\n[dim]Press Enter to return to results...[/dim]"
                )
            except (KeyboardInterrupt, EOFError):
                pass


def display_help() -> None:
    """Display interactive commands and usage instructions."""
    help_text = Text()
    help_text.append("Available Commands:\n", style="bold white")
    help_text.append("  <query>        ", style="bold yellow")
    help_text.append("Search for a new topic directly\n", style="white")
    help_text.append("  <number>       ", style="bold yellow")
    help_text.append(
        "Read result # text cleanly from top to bottom\n", style="white"
    )
    help_text.append("  n, next        ", style="bold yellow")
    help_text.append("View next 5 search results\n", style="white")
    help_text.append("  p, prev        ", style="bold yellow")
    help_text.append("View previous 5 search results\n", style="white")
    help_text.append("  r, results     ", style="bold yellow")
    help_text.append("Re-display current search results\n", style="white")
    help_text.append("  :b <number>    ", style="bold yellow")
    help_text.append(
        "Open result # in your default web browser\n", style="white"
    )
    help_text.append("  :h, :help      ", style="bold yellow")
    help_text.append("Show this help menu\n", style="white")
    help_text.append("  :q, exit, quit ", style="bold yellow")
    help_text.append("Exit the program\n", style="white")

    console.print(
        Panel(
            help_text,
            title="Help & Controls",
            border_style="cyan",
            expand=False,
        )
    )


def print_info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[cyan]ℹ {message}[/cyan]")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✔ {message}[/green]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]⚠ {message}[/yellow]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✖ {message}[/bold red]")
