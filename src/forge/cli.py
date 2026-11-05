"""forge: the command you run inside a project folder."""

import argparse
from pathlib import Path

from . import config
from .agent import Agent
from .llm import LLM
from .safety import Workspace
from .ui import Screen, console

HELP = """[bold]Commands[/]
  /mode plan|ask|auto   how careful to be (plan = read only)
  /tokens               how full the context is
  /clear                forget the conversation
  /exit                 quit"""


def build(root: Path, args) -> tuple[Agent, Screen]:
    s = config.load(root, provider=args.provider, model=args.model, mode=args.mode)
    screen = Screen()
    ws = Workspace(root, s.mode, screen.approve, s.allow_commands)
    agent = Agent(LLM(s), ws, s.max_steps, screen.event)
    agent.settings = s
    return agent, screen


def slash(agent: Agent, line: str) -> bool:
    """Handle a /command. Returns False to quit."""
    cmd, _, arg = line[1:].partition(" ")
    if cmd in ("exit", "quit"):
        return False
    if cmd == "mode" and arg in config.MODES:
        agent.ws.mode = arg
        console.print(f"[green]mode: {arg}[/]")
    elif cmd == "clear":
        agent.messages = []
        console.print("[green]conversation cleared[/]")
    elif cmd == "tokens":
        t = agent.tokens
        console.print(f"context now {t['last_prompt']:,} tokens · used so far {t['prompt']:,} in, {t['output']:,} out")
    else:
        console.print(HELP)
    return True


def repl(agent: Agent) -> None:
    s = agent.settings
    console.print(f"[bold]Forge[/] · {s.model} via {s.provider} · mode [bold]{agent.ws.mode}[/] · "
                  f"{agent.ws.root.name}/   [dim](/help for commands)[/]")
    while True:
        try:
            line = console.input("[bold green]›[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.startswith("/"):
            if not slash(agent, line):
                break
            continue
        try:
            agent.ask(line)
        except KeyboardInterrupt:
            console.print("[yellow]stopped[/]")


def main() -> None:
    p = argparse.ArgumentParser(prog="forge", description="A coding agent for your terminal.")
    p.add_argument("prompt", nargs="*", help="run one task and exit, e.g. forge fix the failing test")
    p.add_argument("--provider", choices=list(config.PROVIDERS))
    p.add_argument("--model")
    p.add_argument("--mode", choices=config.MODES)
    p.add_argument("--dir", default=".", help="the project folder (default: here)")
    args = p.parse_args()
    agent, _ = build(Path(args.dir), args)
    if args.prompt:
        agent.ask(" ".join(args.prompt))
    else:
        repl(agent)
