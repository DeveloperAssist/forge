"""forge-exam: score the agent on small broken projects it has never seen, SWE-bench style.

For each task: copy the project WITHOUT its hidden tests and solution to a temp folder, give Forge the task in auto
mode, then drop the hidden tests in and run them. Pass = the hidden tests pass. Nothing else counts.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from . import config
from .agent import Agent
from .llm import LLM
from .safety import Workspace
from .trace import Trace

HIDDEN = {"hidden_tests", "solution", "bad_fix", "grading.md", "task.md", "__pycache__", ".pytest_cache"}


def hidden_pass(folder: Path, task: Path) -> tuple[bool, str]:
    shutil.copytree(task / "hidden_tests", folder / "hidden_tests", dirs_exist_ok=True)
    p = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "hidden_tests"],
        cwd=folder,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return p.returncode == 0, (p.stdout.strip().splitlines() or [""])[-1]


def run_task(task: Path, settings: config.Settings, out: Path) -> dict:
    work = Path(tempfile.mkdtemp(prefix=f"forge-{task.name}-"))
    shutil.copytree(task, work, dirs_exist_ok=True, ignore=lambda d, names: [n for n in names if n in HIDDEN])
    events = []
    trace = Trace(out)  # traces go to the results folder, not into the task

    def listen(kind, **d):
        events.append(kind)
        trace.event(kind, **d)

    ws = Workspace(work, "auto", lambda *a: True, settings.allow_commands)  # a throwaway copy: say yes to all
    llm = LLM(settings)
    llm.max_wait = 65 * 60  # unattended: an hourly limit may make us wait up to an hour
    agent = Agent(llm, ws, settings.max_steps, listen, settings.context_budget)
    start = time.perf_counter()
    try:
        answer, error = agent.ask((task / "task.md").read_text(encoding="utf-8").strip()), ""
    except Exception as e:  # a crash or an API error is a fail, but the exam goes on
        answer, error = "", f"{type(e).__name__}: {e}"
    secs = time.perf_counter() - start
    passed, summary = hidden_pass(work, task)
    # the model's server stopped us (limit, outage): that says nothing about the agent, so it is not scored
    scored = not error.startswith(
        (
            "RateLimitError",
            "RuntimeError: Still rate-limited",
            "APIConnectionError",
            "APITimeoutError",
            "InternalServerError",
        )
    )
    shutil.rmtree(work, ignore_errors=True)
    return {
        "task": task.name,
        "pass": passed and scored,
        "scored": scored,
        "hidden": summary,
        "seconds": round(secs, 1),
        "steps": events.count("thinking"),
        "tool_calls": events.count("tool_call"),
        "pushbacks": events.count("check"),
        "tokens_in": agent.tokens["prompt"],
        "tokens_out": agent.tokens["output"],
        "models": [m for _, m in agent.llm.chain[: agent.llm.at + 1]],
        "error": error,
        "answer": answer[:2000],
        "trace": trace.path.name,
    }


def main() -> None:
    p = argparse.ArgumentParser(prog="forge-exam")
    p.add_argument("--set", default="exam", help="evals/<set>: exam or heldout")
    p.add_argument("--provider", choices=list(config.PROVIDERS))
    p.add_argument("--model")
    p.add_argument("--only", help="run tasks whose name contains this")
    p.add_argument("--fallback", action="store_true", help="allow switching provider on limits (default: one model)")
    args = p.parse_args()
    # the agent's commands use this project's Python (3.14, with pytest), like `uv run` would
    os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")
    root = Path(__file__).resolve().parents[2]
    tasks = sorted(t for t in (root / "evals" / args.set).iterdir() if (t / "task.md").exists())
    if args.only:
        tasks = [t for t in tasks if args.only in t.name]
    s = config.load(root, provider=args.provider, model=args.model, mode="auto")
    if not args.fallback:
        s.fallbacks = []  # an exam scores ONE model: a switch would mix two models in one score
    out = root / "evals" / "results" / f"{args.set}-{s.provider}-{s.model.replace('/', '_').replace(':', '_')}"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for t in tasks:
        r = run_task(t, s, out)
        rows.append(r)
        mark = "PASS" if r["pass"] else "fail" if r["scored"] else "----"
        print(
            f"{mark}  {r['task']:<32} {r['seconds']:>6} s  {r['steps']:>2} steps  "
            f"{r['pushbacks']} pushbacks  {r['error'][:60]}",
            flush=True,
        )
    passed = sum(r["pass"] for r in rows)
    unscored = sum(not r["scored"] for r in rows)
    summary = {
        "set": args.set,
        "provider": s.provider,
        "model": s.model,
        "passed": passed,
        "total": len(rows),
        "not_scored": unscored,
        "seconds": round(sum(r["seconds"] for r in rows), 1),
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "rows": rows,
    }
    (out / f"{time.strftime('%Y%m%d-%H%M%S')}.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"\n{s.model} via {s.provider}: {passed}/{len(rows)} passed ({summary['seconds']} s)")
