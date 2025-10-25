# ABOUTME: Input handling with prompt_toolkit
# ABOUTME: Multi-line input, history navigation, autocomplete

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.patch_stdout import patch_stdout
from typing import List


class InputHandler:
    """Handle user input with enhanced features"""

    def __init__(self):
        self.history = InMemoryHistory()
        self.session = None
        self._setup_session()

    def _setup_session(self):
        """Setup prompt_toolkit session with completions and keybindings"""

        # Command autocomplete
        commands = WordCompleter([
            '/help', '/stats', '/history', '/search', '/export',
            '/clear', '/exit'
        ], ignore_case=True)

        # Custom style
        style = Style.from_dict({
            'prompt': 'cyan bold',
        })

        # Key bindings for multi-line
        kb = KeyBindings()

        @kb.add('escape', 'enter')  # Alt+Enter for newline
        def _(event):
            event.current_buffer.insert_text('\n')

        self.session = PromptSession(
            completer=commands,
            complete_while_typing=True,
            history=self.history,
            style=style,
            key_bindings=kb,
            multiline=False,  # Single line by default
            enable_history_search=True
        )

    async def get_input(self, prompt: str = "You: ") -> str:
        """Get user input with enhanced features (async compatible)

        Returns:
            User input string
        """
        try:
            # Use patch_stdout to make it work with async
            with patch_stdout():
                user_input = await self.session.prompt_async(prompt)
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            raise

    async def get_multiline_input(self, prompt: str = "You: ") -> str:
        """Get multi-line input (Alt+Enter for newlines, Enter to submit)

        Returns:
            User input string
        """
        # Temporarily enable multiline
        original_multiline = self.session.multiline
        self.session.multiline = True

        try:
            with patch_stdout():
                user_input = await self.session.prompt_async(prompt)
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            raise
        finally:
            self.session.multiline = original_multiline

    def add_to_history(self, text: str):
        """Manually add command to history"""
        self.history.append_string(text)

    def get_history(self, limit: int = 100) -> List[str]:
        """Get command history

        Args:
            limit: Maximum number of history items to return

        Returns:
            List of history strings
        """
        history_strings = []
        for item in self.history.get_strings():
            history_strings.append(item)
            if len(history_strings) >= limit:
                break
        return list(reversed(history_strings))  # Most recent first
