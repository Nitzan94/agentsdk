# ABOUTME: Rich terminal display module
# ABOUTME: Markdown rendering, panels, syntax highlighting, progress indicators

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from datetime import datetime
from typing import Optional


class RichDisplay:
    """Rich terminal display manager"""

    def __init__(self):
        self.console = Console()
        self.live_display: Optional[Live] = None
        self.current_message = ""

    def print_banner(self):
        """Display welcome banner"""
        banner = Table.grid(padding=1)
        banner.add_column(style="cyan bold", justify="center")

        banner.add_row("=" * 60)
        banner.add_row("Personal Assistant Agent")
        banner.add_row("Google Drive • Calendar • Gmail • Research • Memory")
        banner.add_row("=" * 60)

        self.console.print(banner)
        self.console.print()

    def print_help(self):
        """Display help panel"""
        help_table = Table(show_header=False, box=None, padding=(0, 2))
        help_table.add_column(style="cyan")
        help_table.add_column(style="dim")

        help_table.add_row("/help", "Show this help")
        help_table.add_row("/stats", "Show session statistics")
        help_table.add_row("/history [N]", "View last N messages (default 10)")
        help_table.add_row("/search <query>", "Search conversation history")
        help_table.add_row("/export", "Export conversation to markdown")
        help_table.add_row("/clear", "Clear screen")
        help_table.add_row("/exit", "Exit assistant")
        help_table.add_row("Ctrl+C", "Interrupt current response")
        help_table.add_row("Alt+Enter", "New line in input (multi-line)")

        panel = Panel(
            help_table,
            title="[bold cyan]Commands[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
        self.console.print()

    def show_user_message(self, message: str):
        """Display user message in panel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        panel = Panel(
            message,
            title=f"[bold blue]👤 You[/bold blue] [dim]{timestamp}[/dim]",
            border_style="blue",
            padding=(0, 1)
        )
        self.console.print(panel)

    def show_assistant_prefix(self):
        """Show assistant message header"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(
            f"[bold green]🤖 Assistant[/bold green] [dim]{timestamp}[/dim]"
        )

    def show_assistant_message(self, message: str, markdown: bool = True):
        """Display assistant message with optional markdown rendering"""
        if markdown:
            try:
                md = Markdown(message)
                panel = Panel(
                    md,
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(panel)
            except Exception:
                # Fallback to plain text if markdown fails
                panel = Panel(
                    message,
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(panel)
        else:
            panel = Panel(
                message,
                border_style="green",
                padding=(0, 1)
            )
            self.console.print(panel)

    def start_streaming(self):
        """Start live streaming display"""
        self.current_message = ""

    def update_stream(self, text: str):
        """Update streaming message"""
        self.current_message += text
        # For now, just accumulate - we'll render at the end
        # Rich Live() has issues with async, so we accumulate and display at end

    def end_stream(self, markdown: bool = True):
        """Finish streaming and display final message"""
        if self.current_message:
            self.show_assistant_message(self.current_message, markdown=markdown)
            self.current_message = ""

    def show_tool_usage(self, tool_name: str):
        """Show tool usage indicator"""
        self.console.print(
            f"[dim cyan]  ⚙️  Using tool: {tool_name}[/dim cyan]"
        )

    def show_spinner(self, text: str = "Processing..."):
        """Show spinner for long operations"""
        with self.console.status(f"[cyan]{text}[/cyan]", spinner="dots"):
            pass  # Caller should use this as context manager

    def show_error(self, message: str):
        """Display error message"""
        panel = Panel(
            f"[red]{message}[/red]",
            title="[bold red]Error[/bold red]",
            border_style="red"
        )
        self.console.print(panel)

    def show_info(self, message: str):
        """Display info message"""
        self.console.print(f"[cyan]ℹ️  {message}[/cyan]")

    def show_warning(self, message: str):
        """Display warning message"""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")

    def show_success(self, message: str):
        """Display success message"""
        self.console.print(f"[green]✓ {message}[/green]")

    def show_stats(self, session_id: str, stats: dict):
        """Display session statistics"""
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column(style="cyan bold")
        stats_table.add_column(style="white")

        stats_table.add_row("Session ID", session_id[:16] + "...")
        stats_table.add_row("Started", stats.get('started_at', 'Unknown'))
        stats_table.add_row("Last Active", stats.get('last_active_at', 'Unknown'))
        stats_table.add_row("Messages", str(stats.get('message_count', 0)))
        stats_table.add_row("Total Cost", f"${stats.get('total_cost_usd', 0):.4f}")

        panel = Panel(
            stats_table,
            title="[bold cyan]Session Statistics[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)

    def show_history(self, messages: list):
        """Display conversation history"""
        if not messages:
            self.show_info("No messages in history")
            return

        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')

            if role == 'user':
                panel = Panel(
                    content,
                    title=f"[bold blue]👤 You[/bold blue] [dim]{timestamp}[/dim]",
                    border_style="blue",
                    padding=(0, 1)
                )
            elif role == 'assistant':
                md = Markdown(content)
                panel = Panel(
                    md,
                    title=f"[bold green]🤖 Assistant[/bold green] [dim]{timestamp}[/dim]",
                    border_style="green",
                    padding=(0, 1)
                )
            else:
                panel = Panel(
                    content,
                    title=f"[dim]{role}[/dim] [dim]{timestamp}[/dim]",
                    border_style="dim",
                    padding=(0, 1)
                )

            self.console.print(panel)

    def clear_screen(self):
        """Clear the terminal screen"""
        self.console.clear()

    def print(self, *args, **kwargs):
        """Proxy to console.print"""
        self.console.print(*args, **kwargs)
