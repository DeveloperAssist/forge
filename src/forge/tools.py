"""The agent's hands. Each tool is a plain function; its docstring and type hints become the schema the model reads."""

import difflib
import fnmatch
import inspect
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass

from .safety import ToolError, Workspace

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".forge", ".pytest_cache", ".ruff_cache",
             "dist", "build", ".mypy_cache", ".idea", ".vscode"}
MAX_OUTPUT = 8_000  # characters of tool output the model gets back; the rest is cut


@dataclass
class Tool:
    name: str
    fn: Callable
    kind: str  # "read", "edit" or "run": plan mode only offers "read" tools
    schema: dict


TYPES = {str: "string", int: "integer", bool: "boolean"}


def make_schema(fn: Callable) -> dict:
    """Build the JSON schema from the function: first docstring line = description, 'name: text' lines = params."""
    doc = inspect.getdoc(fn) or ""
    description = doc.split("\n\n")[0].replace("\n", " ")
    notes = dict(re.findall(r"^\s*(\w+): (.+)$", doc, re.M))
    props, required = {}, []
    for p in list(inspect.signature(fn).parameters.values())[1:]:  # skip the workspace argument
        props[p.name] = {"type": TYPES[p.annotation], "description": notes.get(p.name, "")}
        if p.default is inspect.Parameter.empty:
            required.append(p.name)
    return {"type": "function", "function": {
        "name": fn.__name__, "description": description,
        "parameters": {"type": "object", "properties": props, "required": required}}}


REGISTRY: dict[str, Tool] = {}


def tool(kind: str):
    def register(fn):
        REGISTRY[fn.__name__] = Tool(fn.__name__, fn, kind, make_schema(fn))
        return fn
    return register


def cut(text: str, limit: int = MAX_OUTPUT) -> str:
    if len(text) <= limit:
        return text
    return text[: limit // 2] + f"\n… [{len(text) - limit} characters cut] …\n" + text[-limit // 2:]


def walk(ws: Workspace, start):
    for folder, dirs, files in os.walk(start):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            yield os.path.join(folder, f)


# --------------------------------------------------------------------------------------------------- read tools
@tool("read")
def read_file(ws: Workspace, path: str, offset: int = 1, limit: int = 400) -> str:
    """Read a text file. Lines come back numbered, so you can point at them.

    path: file path, relative to the project folder
    offset: first line to show (1 = the top)
    limit: how many lines to show
    """
    full = ws.path(path)
    if not full.is_file():
        raise ToolError(f"{path} is not a file. Use list_files to see what exists.")
    lines = full.read_text(encoding="utf-8", errors="replace").splitlines()
    ws.seen[full] = full.stat().st_mtime
    end = min(len(lines), offset - 1 + limit)
    shown = [f"{n:>5}│ {lines[n - 1]}" for n in range(offset, end + 1)]
    more = f"\n… {len(lines) - end} more lines (use offset={end + 1})" if end < len(lines) else ""
    return cut("\n".join(shown) + more) if shown else f"{path} is empty."


@tool("read")
def list_files(ws: Workspace, path: str = ".") -> str:
    """List the files in a folder and its sub-folders (skips .git, .venv, node_modules and caches).

    path: folder to list, relative to the project folder
    """
    start = ws.path(path)
    found = [ws.rel(ws.path(f)) for f in walk(ws, start)]
    if len(found) > 300:
        return "\n".join(found[:300]) + f"\n… and {len(found) - 300} more. List a sub-folder to see them."
    return "\n".join(found) or "(empty folder)"


@tool("read")
def search(ws: Workspace, pattern: str, path: str = ".", files: str = "*") -> str:
    """Search file contents with a regular expression. Returns file:line: text for each match.

    pattern: a Python regular expression, e.g. def total|class Cart
    path: folder or file to search in
    files: only files whose name matches this glob, e.g. *.py
    """
    try:
        rx = re.compile(pattern)
    except re.error as e:
        raise ToolError(f"Bad regular expression: {e}") from None
    start = ws.path(path)
    targets = [str(start)] if start.is_file() else walk(ws, start)
    hits = []
    for f in targets:
        if not fnmatch.fnmatch(os.path.basename(f), files):
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append(f"{ws.rel(ws.path(f))}:{n}: {line.strip()[:200]}")
                if len(hits) >= 100:
                    return "\n".join(hits) + "\n… stopped at 100 matches. Narrow the search."
    return "\n".join(hits) or "No matches."


# --------------------------------------------------------------------------------------------------- edit tools
def show_diff(path: str, old: str, new: str) -> str:
    lines = difflib.unified_diff(old.splitlines(), new.splitlines(), f"a/{path}", f"b/{path}", lineterm="", n=2)
    return "\n".join(lines)


def check_fresh(ws: Workspace, full) -> None:
    """No blind edits: the model must have read the file, and nobody may have changed it since."""
    if full not in ws.seen:
        raise ToolError(f"Read {ws.rel(full)} with read_file before editing it.")
    if full.stat().st_mtime != ws.seen[full]:
        raise ToolError(f"{ws.rel(full)} changed since you read it. Read it again first.")


@tool("edit")
def edit_file(ws: Workspace, path: str, old_text: str, new_text: str) -> str:
    """Replace one exact piece of a file with new text. old_text must appear exactly once: include enough lines.

    path: the file to change
    old_text: the exact text to replace, copied from the file (without the line numbers)
    new_text: what to put in its place
    """
    full = ws.path(path)
    if not full.is_file():
        raise ToolError(f"{path} does not exist. Use write_file to create it.")
    check_fresh(ws, full)
    old = full.read_text(encoding="utf-8")
    count = old.count(old_text)
    if count == 0:
        raise ToolError(f"old_text was not found in {path}. Copy it exactly from read_file (no line numbers).")
    if count > 1:
        raise ToolError(f"old_text appears {count} times in {path}. Add more surrounding lines to pick one.")
    new = old.replace(old_text, new_text)
    diff = show_diff(path, old, new)
    if not ws.may_edit(f"Edit {path}", diff):
        return "The user said no to this edit. Ask them what they want instead."
    full.write_text(new, encoding="utf-8")
    ws.seen[full] = full.stat().st_mtime
    return f"Edited {path}.\n{diff}"


@tool("edit")
def write_file(ws: Workspace, path: str, content: str) -> str:
    """Create a new file, or replace a whole file. Prefer edit_file for small changes to existing files.

    path: the file to write
    content: the complete file contents
    """
    full = ws.path(path)
    old = ""
    if full.exists():
        check_fresh(ws, full)
        old = full.read_text(encoding="utf-8")
    diff = show_diff(path, old, content)
    if not ws.may_edit(f"{'Rewrite' if old else 'Create'} {path}", diff):
        return "The user said no to this file. Ask them what they want instead."
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    ws.seen[full] = full.stat().st_mtime
    return f"Wrote {path} ({len(content.splitlines())} lines)."


# --------------------------------------------------------------------------------------------------- run tool
@tool("run")
def run_command(ws: Workspace, command: str, timeout: int = 120) -> str:
    """Run a shell command in the project folder, e.g. to run the tests. Returns the exit code and output.

    command: the command line, e.g. uv run pytest -q
    timeout: seconds before the command is stopped
    """
    if not ws.may_run(command):
        return "The user said no to this command. Ask them what to do instead."
    try:
        p = subprocess.run(command, shell=True, cwd=ws.root, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=min(timeout, 600))
    except subprocess.TimeoutExpired:
        return f"Stopped after {timeout} s. If it waits for input or runs a server, it cannot run here."
    out = (p.stdout + ("\n" + p.stderr if p.stderr else "")).strip()
    return cut(f"exit code {p.returncode}\n{out}")


def run_tool(ws: Workspace, name: str, args: dict) -> str:
    """Call a tool by name. Every failure becomes text the model can read and recover from."""
    t = REGISTRY.get(name)
    if t is None:
        return f"Error: there is no tool called {name}. Tools: {', '.join(REGISTRY)}."
    try:
        return t.fn(ws, **args)
    except ToolError as e:
        return f"Error: {e}"
    except TypeError as e:
        return f"Error: wrong arguments for {name}: {e}"
    except OSError as e:
        return f"Error: {e}"


def schemas(mode: str) -> list[dict]:
    return [t.schema for t in REGISTRY.values() if mode != "plan" or t.kind == "read"]
