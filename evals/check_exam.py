"""Prove every exam task is valid.

For each task folder in evals/exam/NN_name:
  1. copy the task (minus solution/ and bad_fix/) to a temp dir and run hidden_tests/:
     they must FAIL on the original code (pytest exit code 1, i.e. real test failures,
     not a collection error);
  2. copy solution/ over it: hidden_tests/ must PASS, and the visible tests/ must pass too.

"No-change" tasks (they have a bad_fix/ folder and a grading.md) are checked the other way round:
hidden tests PASS on the untouched code and FAIL once bad_fix/ is copied over it.

Run (from the project folder):  uv run python evals/check_exam.py [--set exam|heldout] [task-id ...]  (--set defaults to exam)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXAM = Path(__file__).resolve().parent / "exam"
SKIP = {"solution", "bad_fix", "__pycache__", ".pytest_cache"}


def run_pytest(workdir: Path, target: str) -> tuple[int, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    env.pop("PYTEST_ADDOPTS", None)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", str(workdir), target],
        cwd=workdir, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300,
    )
    return proc.returncode, proc.stdout + proc.stderr


def fresh_copy(task: Path, dest: Path) -> None:
    shutil.copytree(task, dest, ignore=lambda d, names: [n for n in names if n in SKIP])


def overlay(src: Path, dest: Path) -> None:
    for f in src.rglob("*"):
        if f.is_file():
            target = dest / f.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)


def check_task(task: Path) -> list[str]:
    problems: list[str] = []
    for required in ("task.md", "conftest.py", "tests", "hidden_tests"):
        if not (task / required).exists():
            problems.append(f"missing {required}")
    no_change = (task / "bad_fix").is_dir()
    if not no_change and not (task / "solution").is_dir():
        problems.append("missing solution/")
    if no_change and not (task / "grading.md").exists():
        problems.append("no-change task without grading.md")
    if problems:
        return problems

    with tempfile.TemporaryDirectory(prefix=f"exam_{task.name}_") as tmp:
        work = Path(tmp) / task.name
        fresh_copy(task, work)
        rc, out = run_pytest(work, "hidden_tests")
        if no_change:
            if rc != 0:
                problems.append(f"hidden tests should PASS on untouched code, got exit {rc}\n{out[-1500:]}")
            overlay(task / "bad_fix", work)
            rc, out = run_pytest(work, "hidden_tests")
            if rc != 1:
                problems.append(f"hidden tests should FAIL on bad_fix, got exit {rc}\n{out[-1500:]}")
            return problems

        if rc != 1:
            problems.append(f"hidden tests should FAIL (exit 1) on original, got exit {rc}\n{out[-1500:]}")
        overlay(task / "solution", work)
        rc, out = run_pytest(work, "hidden_tests")
        if rc != 0:
            problems.append(f"hidden tests should PASS with solution, got exit {rc}\n{out[-1500:]}")
        rc, out = run_pytest(work, "tests")
        if rc != 0:
            problems.append(f"visible tests should PASS with solution, got exit {rc}\n{out[-1500:]}")
    return problems


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = EXAM
    if "--set" in argv:
        i = argv.index("--set")
        root = EXAM.parent / argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    tasks = sorted(p for p in root.iterdir() if p.is_dir() and p.name[:2].isdigit())
    if argv:
        tasks = [t for t in tasks if any(t.name.startswith(a) for a in argv)]
    bad = 0
    for task in tasks:
        problems = check_task(task)
        if problems:
            bad += 1
            print(f"FAIL  {task.name}")
            for p in problems:
                print("      " + p.replace("\n", "\n      "))
        else:
            print(f"ok    {task.name}")
    print(f"\n{len(tasks) - bad}/{len(tasks)} tasks valid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
