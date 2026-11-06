"""forge: the command you run inside a project folder."""

import argparse
from pathlib import Path

import openai

from . import config, skills
from .agent import Agent
from .checkpoints import Checkpoints
from .llm import LLM
from .safety import Workspace
from .trace import Trace, both
from .ui import Screen, console

HELP = """[bold]Commands[/]
  /mode plan|ask|auto   how careful to be (plan = read only)
  /undo                 put the files back the way they were before the last task
  /init                 let Forge study the project and write FORGE.md (its notes for next time)
  /skills               the skills Forge can load
  /tokens               how full the context is
  /clear                forget the conversation
  /exit                 quit"""

INIT_TASK = """Study this project and write FORGE.md in the project folder: notes for a coding agent that will work
here later. Include: what the project does (2 lines), how to install, run and test it (exact commands), the main
folders and files, and code conventions you notice. Under 40 lines. Check every command before writing it down."""


def build(root: Path, args) -> Agent:
    s = config.load(root, provider=args.provider, model=args.model, mode=args.mode)
    screen = Screen()
    ws = Workspace(root, s.mode, screen.approve, s.allow_commands)
    ws.skills = skills.load(ws.root)
    trace = Trace(ws.root)
    agent = Agent(LLM(s), ws, s.max_steps, both(screen.event, trace.event), s.context_budget, Checkpoints(ws.root))
    trace.event("start", provider=s.provider, model=s.model, mode=s.mode)
    agent.settings = s
    agent.screen_stop = screen.stop_spinner
    return agent


def slash(agent: Agent, line: str) -> bool:
    """Handle a /command. Returns False to quit."""
    cmd, _, arg = line[1:].partition(" ")
    if cmd in ("exit", "quit"):
        return False
    if cmd == "mode" and arg in config.MODES:
        agent.ws.mode = arg
        console.print(f"[green]mode: {arg}[/]")
    elif cmd == "undo":
        files = agent.checkpoints.undo()
        console.print(f"[green]put back: {', '.join(files)}[/]" if files else "[yellow]nothing to undo[/]")
        if files:
            agent.messages.append(
                {
                    "role": "user",
                    "content": f"[note] The user undid your last changes to: "
                    f"{', '.join(files)}. Read files again before editing.",
                }
            )
            agent.ws.seen.clear()
    elif cmd == "init":
        agent.ask(INIT_TASK)
    elif cmd == "skills":
        for s in agent.ws.skills.values():
            console.print(f"[bold]{s.name}[/]  {s.description}")
        if not agent.ws.skills:
            console.print("no skills yet: add .forge/skills/<name>/SKILL.md")
    elif cmd == "clear":
        agent.messages = []
        console.print("[green]conversation cleared[/]")
    elif cmd == "tokens":
        t = agent.tokens
        console.print(
            f"context now {t['last_prompt']:,} tokens (compacts at {agent.context_budget:,}) · "
            f"used so far {t['prompt']:,} in, {t['output']:,} out"
        )
    else:
        console.print(HELP)
    return True


def repl(agent: Agent) -> None:
    s = agent.settings
    console.print(
        f"[bold]Forge[/] · {s.model} via {s.provider} · mode [bold]{agent.ws.mode}[/] · "
        f"{agent.ws.root.name}/   [dim](/help for commands)[/]"
    )
    while True:
        try:
            line = console.input("[bold green]›[/] ").strip()
        except EOFError, KeyboardInterrupt:
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
        except openai.APIError as e:  # the model's server said no (rate limit, bad request…): keep the session
            agent.screen_stop()
            console.print(f"[red]The model's server returned an error: {e}[/]")


def main() -> None:
    p = argparse.ArgumentParser(prog="forge", description="A coding agent for your terminal.")
    p.add_argument("prompt", nargs="*", help="run one task and exit, e.g. forge fix the failing test")
    p.add_argument("--provider", choices=list(config.PROVIDERS))
    p.add_argument("--model")
    p.add_argument("--mode", choices=config.MODES)
    p.add_argument("--dir", default=".", help="the project folder (default: here)")
    args = p.parse_args()
    agent = build(Path(args.dir), args)
    if args.prompt:
        agent.ask(" ".join(args.prompt))
    else:
        repl(agent)
