"""The system prompt: who the agent is, how it should work, and what it knows about this project."""

import platform
import subprocess
from datetime import date
from pathlib import Path

RULES = """You are Forge, a coding agent working inside the user's project folder.

How you work:
- Look before you act: use list_files, search and read_file to understand the code first.
- Read a file before you edit it. Make small, exact edits with edit_file; use write_file only for new files.
- After changing code, run the tests (or the program) with run_command and read the result. If they fail, fix it.
- Do one thing at a time and keep going until the task is done or you need the user.
- Never invent file contents, test results or command output: check with a tool.
- When you finish, reply in a few short lines: what you changed and how you checked it."""

PLAN_RULES = """You are in PLAN mode: read-only. Explore the code, then reply with a short numbered plan
(which files, what changes, how to test). Do not try to change anything."""


def git_status(root: Path) -> str:
    try:
        p = subprocess.run(["git", "status", "--short", "--branch"], cwd=root, capture_output=True, text=True,
                           timeout=10)
        return p.stdout.strip()[:1500] if p.returncode == 0 else "not a git repository"
    except (OSError, subprocess.TimeoutExpired):
        return "git not available"


def system_prompt(root: Path, mode: str) -> str:
    shell = "cmd.exe (Windows)" if platform.system() == "Windows" else "sh"
    parts = [RULES]
    if mode == "plan":
        parts.append(PLAN_RULES)
    parts.append(f"Environment:\n- project folder: {root.name}\n- OS: {platform.system()}, commands run in "
                 f"{shell}\n- today: {date.today().isoformat()}\n- git: {git_status(root)}")
    memory = root / "FORGE.md"
    if memory.exists():
        parts.append("Project notes from FORGE.md (follow them):\n" + memory.read_text(encoding="utf-8")[:6000])
    return "\n\n".join(parts)
