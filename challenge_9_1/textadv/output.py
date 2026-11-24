"""Terminal output: everything the player sees goes through Output.say()."""

from __future__ import annotations

import shutil
import textwrap
from collections.abc import Callable


class Output:
    def __init__(self, width: int | None = None, write: Callable[[str], None] = print):
        self._width = width
        self._write = write

    @property
    def width(self) -> int:
        if self._width:
            return self._width
        cols = shutil.get_terminal_size((80, 24)).columns
        return max(20, min(cols, 100) - 1)

    def say(self, text: str = "") -> None:
        """Print text, wrapping each paragraph (newline-separated) to the
        terminal width.  Leading spaces on a line are kept as a hanging indent."""
        for para in str(text).split("\n"):
            if not para.strip():
                self._write("")
                continue
            indent = para[: len(para) - len(para.lstrip())]
            self._write(
                textwrap.fill(
                    para.strip(),
                    self.width,
                    initial_indent=indent,
                    subsequent_indent=indent,
                )
            )


class BufferOutput(Output):
    """Collects output in memory (for tests)."""

    def __init__(self, width: int = 70):
        self.lines: list[str] = []
        super().__init__(width=width, write=self.lines.append)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def clear(self) -> None:
        self.lines.clear()


def join_list(words: list[str], conj: str = "and") -> str:
    if len(words) <= 1:
        return "".join(words)
    return f"{', '.join(words[:-1])} {conj} {words[-1]}"
