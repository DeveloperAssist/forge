"""Everything that stops the agent from doing damage: the path jail, the permission modes, blocked commands."""

import re
from collections.abc import Callable
from pathlib import Path


class ToolError(Exception):
    """A mistake the model can fix: the message goes back to it as the tool result."""


# Never run these, whatever the mode: wiping disks, piping the internet into a shell, pushing code, secrets.
BLOCKED = [
    r"\brm\s+-[a-z]*r[a-z]*f?\s+(/|~|\*|\.\s*$)", r"\bformat\s+[a-z]:", r"\bdel\s+/[sq]", r"\brmdir\s+/s",
    r"(curl|wget|iwr|Invoke-WebRequest)[^|]*\|\s*(sh|bash|python|iex)", r"\bgit\s+push\b", r"\bgit\s+reset\s+--hard",
    r"\bshutdown\b", r"\bmkfs", r"\bsudo\b", r"\.env\b", r"id_rsa", r"\bchmod\s+-R\s+777",
]


def blocked(command: str) -> str | None:
    for pattern in BLOCKED:
        if re.search(pattern, command, re.I):
            return pattern
    return None


# An approval function shows the user what is about to happen and returns True if they say yes.
Approve = Callable[[str, str, str], bool]  # (kind, title, detail) -> yes?


class Workspace:
    """The folder the agent works in, and the rules for touching it."""

    def __init__(self, root: Path, mode: str, approve: Approve, allow_commands: list[str]):
        self.root = root.resolve()
        self.mode = mode
        self.approve = approve
        self.allow_commands = allow_commands
        self.seen: dict[Path, float] = {}  # files the model has read, and when: no blind edits

    def path(self, p: str) -> Path:
        """Turn the model's path into a real one, and refuse anything outside the project folder."""
        full = (self.root / p).resolve()
        if full != self.root and self.root not in full.parents:
            raise ToolError(f"{p} is outside the project folder. Use paths inside {self.root.name}/.")
        return full

    def rel(self, full: Path) -> str:
        return full.relative_to(self.root).as_posix() or "."

    def may_edit(self, title: str, diff: str) -> bool:
        if self.mode == "plan":
            raise ToolError("Plan mode is read-only. Describe the change instead of making it.")
        if self.mode == "auto":
            return True
        return self.approve("edit", title, diff)

    def may_run(self, command: str) -> bool:
        if self.mode == "plan":
            raise ToolError("Plan mode is read-only. Say which command you would run instead.")
        if pattern := blocked(command):
            raise ToolError(f"Blocked command (matches {pattern!r}). Find a safer way, or ask the user to do it.")
        # "pytest && rm -rf src" starts with an allowed word, so chained commands are never on the safe list
        chained = re.search(r"[;&|<>`]|\$\(", command)
        safe = not chained and any(command == c or command.startswith(c + " ") for c in self.allow_commands)
        if safe:
            return True
        return self.approve("run", command, "")
