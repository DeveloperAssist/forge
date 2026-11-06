"""What you see in the terminal: tool calls as they happen, diffs, approval questions, the answer."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

console = Console(highlight=False)

ARG_SHOWN = {
    "read_file": "path",
    "list_files": "path",
    "search": "pattern",
    "edit_file": "path",
    "write_file": "path",
    "run_command": "command",
    "explore": "question",
    "use_skill": "name",
}


class Screen:
    def __init__(self):
        self.status = None

    def stop_spinner(self):
        if self.status:
            self.status.stop()
            self.status = None

    def event(self, kind: str, **d) -> None:
        if kind == "thinking":
            self.stop_spinner()
            self.status = console.status(f"[dim]thinking (step {d['step']})…[/]", spinner="dots")
            self.status.start()
            return
        self.stop_spinner()
        if kind == "note":
            console.print(f"[dim]{d['text']}[/]")
        elif kind == "plan":
            marks = {"[x]": "[green]✔[/]", "[>]": "[yellow]▸[/]", "[ ]": "[dim]○[/]"}
            for line in d["text"].splitlines():
                mark = next((v for k, v in marks.items() if line.strip().startswith(k)), "•")
                console.print(f"  {mark} {line.strip()[3:].strip() if mark != '•' else line.strip()}")
        elif kind == "wait":
            console.print(
                f"[yellow]free-tier token limit reached: waiting {d['seconds'] / 60:.1f} min, then carrying on[/]"
            )
        elif kind == "switch":
            console.print(f"[yellow]{d['reason']}: switching to {d['model']} via {d['provider']}[/]")
        elif kind == "compact":
            console.print(f"[dim]context was {d['before']:,} tokens: older parts summarised to make room[/]")
        elif kind in ("helper_tool_call", "helper_tool_result"):
            if kind == "helper_tool_call":
                key = ARG_SHOWN.get(d["name"])
                console.print(f"    [dim]↳ helper: {d['name']} {d['args'].get(key, '') if key else ''}[/]")
        elif kind == "check":
            console.print(f"[bold magenta]✗ check:[/] [magenta]{d['text'][:160]}[/]")
        elif kind == "tool_call":
            key = ARG_SHOWN.get(d["name"])
            shown = d["args"].get(key, "") if key else ""
            console.print(f"[bold cyan]●[/] [bold]{d['name']}[/] [cyan]{shown}[/]")
        elif kind == "tool_result":
            first = d["result"].splitlines()[0] if d["result"] else ""
            colour = "red" if first.startswith("Error") or first.startswith("exit code 1") else "dim"
            more = len(d["result"].splitlines()) - 1
            console.print(f"  [{colour}]⎿ {first[:110]}{f'  (+{more} lines)' if more > 0 else ''}[/]")
        elif kind == "answer":
            console.print()
            console.print(Markdown(d["text"] or "(no answer)"))
            console.print()

    def approve(self, kind: str, title: str, detail: str) -> bool:
        """Ask the human. Edits show their diff; commands show the command."""
        self.stop_spinner()
        if kind == "edit":
            body = Syntax(detail or "(no change)", "diff", theme="ansi_dark", word_wrap=True)
            console.print(Panel(body, title=f"[bold yellow]{title}[/]", border_style="yellow"))
        else:
            console.print(Panel(f"[bold]{title}[/]", title="[bold yellow]Run this command?[/]", border_style="yellow"))
        answer = console.input("[yellow]Allow? [y]es / [n]o:[/] ").strip().lower()
        return answer in ("y", "yes", "")
