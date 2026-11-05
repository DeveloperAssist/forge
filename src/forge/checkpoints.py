"""Undo for the agent: a snapshot of the project before every task, kept in a hidden git repo in .forge/.

It works even if your project does not use git, and it never touches your own .git folder.
"""

import subprocess
from pathlib import Path


class Checkpoints:
    def __init__(self, root: Path):
        self.root = root
        self.git_dir = root / ".forge" / "checkpoints.git"
        self.stack: list[str] = []  # snapshot ids, newest last

    def git(self, *args: str) -> str:
        p = subprocess.run(["git", f"--git-dir={self.git_dir}", f"--work-tree={self.root}", *args],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if p.returncode != 0:
            raise RuntimeError(p.stderr.strip() or p.stdout.strip())
        return p.stdout.strip()

    def setup(self) -> None:
        if not self.git_dir.exists():
            self.git_dir.parent.mkdir(parents=True, exist_ok=True)
            self.git("init", "-q")
            # the agent's own files and virtual environments are never part of a snapshot
            (self.git_dir / "info" / "exclude").write_text(".forge/\n.venv/\nvenv/\nnode_modules/\n__pycache__/\n")

    def snapshot(self, label: str) -> str:
        self.setup()
        self.git("add", "-A")
        self.git("-c", "user.name=forge", "-c", "user.email=forge@localhost",
                 "commit", "-q", "--allow-empty", "-m", label[:200])
        sha = self.git("rev-parse", "HEAD")
        self.stack.append(sha)
        return sha

    def undo(self) -> list[str]:
        """Put every file back the way it was before the last task. Returns the files that changed."""
        if not self.stack:
            return []
        before = self.stack.pop()
        now = self.snapshot("before undo")
        self.stack.pop()  # that snapshot only exists so we can compare; it is not an undo point
        changes = self.git("diff", "--name-status", "--no-renames", before, now).splitlines()
        touched = []
        for line in changes:
            status, path = line.split("\t", 1)
            if status == "A":  # created by the agent: remove it
                (self.root / path).unlink(missing_ok=True)
            else:  # changed or deleted: bring back the old version
                self.git("checkout", before, "--", path)
            touched.append(path)
        return touched
