"""A flight recorder: every step of every task, one JSON line each, in .forge/traces/. Read it when things go wrong."""

import json
import time
from pathlib import Path


class Trace:
    def __init__(self, root: Path):
        folder = root / ".forge" / "traces"
        folder.mkdir(parents=True, exist_ok=True)
        self.path = folder / time.strftime("%Y%m%d-%H%M%S.jsonl")
        self.start = time.perf_counter()

    def event(self, kind: str, **details) -> None:
        row = {"t": round(time.perf_counter() - self.start, 3), "kind": kind, **details}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def both(*listeners):
    """Send every event to several listeners (the screen and the trace)."""

    def event(kind, **details):
        for listen in listeners:
            listen(kind, **details)

    return event
