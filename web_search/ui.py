"""Rich terminal UI presentation components for web-search CLI."""

from typing import List, Optional
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


def display_results(results: List[SearchResult], query: str) -> None:
    """Render a list of search results in a clean formatted view.

    Args:
        results: List of SearchResult objects to display.
        query: The search query string for context.
    """
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

    table = Table(
        title=f"Search Results for: [bold cyan]\"{query}\"[/bold cyan]",
        title_justify="left",
        show_header=False,
        box=None,
        padding=(0, 1),
    )
    table.add_column("Index", style="bold yellow", width=4, justify="right")
    table.add_column("Details", style="white")

    for res in results:
        details = Text()
        details.append(f"{res.title}\n", style="bold bright_blue")
        details.append(f"{res.url}\n", style="green dim")
        if res.snippet:
            details.append(f"{res.snippet}\n", style="white")

        table.add_row(f"[{res.index}]", details)
        table.add_section()

    console.print()
    console.print(table)
    console.print(
        "[dim]Actions: Enter [[bold yellow]#item[/bold yellow]] to read in "
        "terminal | [[bold yellow]:b #[/bold yellow]] open in browser | "
        "[[bold yellow]:q[/bold yellow]] exit[/dim]\n"
    )


def display_article(
    title: str,
    url: str,
    markdown_content: str,
    max_lines: Optional[int] = None,
) -> None:
    """Display article content rendered from Markdown in the terminal.

    Args:
        title: Title of the article or search result.
        url: Original webpage URL.
        markdown_content: Clean markdown text of the webpage.
        max_lines: Optional maximum lines to display before truncation.
    """
    console.rule(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"[dim green]Source: {url}[/dim green]\n")

    if not markdown_content.strip():
        console.print(
            "[italic yellow]No readable text could be extracted "
            "from this page.[/italic yellow]"
        )
        return

    lines = markdown_content.splitlines()
    if max_lines and len(lines) > max_lines:
        truncated_content = "\n".join(lines[:max_lines])
        truncated_content += (
            f"\n\n*[Content truncated. Showing first {max_lines} "
            f"lines of {len(lines)}...]*"
        )
        md = Markdown(truncated_content)
    else:
        md = Markdown(markdown_content)

    console.print(md)
    console.rule("[bold cyan]End of Article[/bold cyan]")
    console.print()


def display_help() -> None:
    """Display interactive commands and usage instructions."""
    help_text = Text()
    help_text.append("Available Commands:\n", style="bold white")
    help_text.append("  <query>        ", style="bold yellow")
    help_text.append("Search for a new topic directly\n", style="white")
    help_text.append("  <number>       ", style="bold yellow")
    help_text.append(
        "Read result # text directly in the terminal\n", style="white"
    )
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
