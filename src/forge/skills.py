"""Skills: instructions for one kind of task, loaded only when needed.

A skill is a folder with a SKILL.md: a short header (name, description) and the steps. The model always sees the
names and descriptions (a few words each); it loads the full steps with use_skill only when a task matches.
That keeps the context small however many skills you add.

Where they live: <project>/.forge/skills/ (this project) and ~/.forge/skills/ (all your projects).
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    name: str
    description: str
    body: str


HEADER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def parse(text: str, fallback_name: str) -> Skill:
    m = HEADER.match(text)
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M)) if m else {}
    body = text[m.end():] if m else text
    return Skill(meta.get("name", fallback_name).strip(), meta.get("description", "").strip(), body.strip())


def load(root: Path) -> dict[str, Skill]:
    skills = {}
    for base in (Path.home() / ".forge" / "skills", root / ".forge" / "skills"):  # the project's win on a clash
        for f in sorted(base.glob("*/SKILL.md")):
            s = parse(f.read_text(encoding="utf-8"), f.parent.name)
            skills[s.name] = s
    return skills


def index(skills: dict[str, Skill]) -> str:
    """The short list that goes in the system prompt."""
    lines = [f"- {s.name}: {s.description}" for s in skills.values()]
    return "Skills you can load with use_skill:\n" + "\n".join(lines)
