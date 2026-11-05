import pytest

from forge.llm import Reply, ToolCall
from forge.safety import Workspace


class FakeLLM:
    """Plays back scripted replies instead of calling a model, and remembers what it was sent."""

    def __init__(self, *replies: Reply):
        self.replies = list(replies)
        self.sent: list[list[dict]] = []

    def chat(self, messages, tools):
        self.sent.append([dict(m) for m in messages])
        return self.replies.pop(0)


def call(tool_name: str, i: int = 0, **args) -> Reply:
    return Reply("", [ToolCall(f"c{i}", tool_name, args)], prompt_tokens=100)


def say(text: str, tokens: int = 100) -> Reply:
    return Reply(text, prompt_tokens=tokens)


@pytest.fixture
def project(tmp_path):
    (tmp_path / "app.py").write_text("def total(a, b):\n    return a - b\n", encoding="utf-8")
    (tmp_path / "conftest.py").write_text("", encoding="utf-8")  # lets pytest import app.py
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("from app import total\n\ndef test_total():\n"
                                                    "    assert total(2, 3) == 5\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def ws(project):
    answers = []

    def approve(kind, title, detail):
        answers.append((kind, title))
        return True

    w = Workspace(project, "auto", approve, ["python -m pytest", "git status"])
    w.asked = answers
    return w
