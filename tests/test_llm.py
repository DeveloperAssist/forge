"""The provider chain: a daily limit moves to the next free provider; a per-minute limit just waits."""

from types import SimpleNamespace as NS

import httpx
import openai

from forge import config
from forge import llm as llm_mod
from forge.llm import LLM


def limit_error(text: str) -> openai.RateLimitError:
    response = httpx.Response(429, request=httpx.Request("POST", "http://x"))
    return openai.RateLimitError(text, response=response, body=None)


def ok(text: str):
    message = NS(content=text, tool_calls=None)
    return NS(choices=[NS(message=message)], usage=NS(prompt_tokens=10, completion_tokens=2))


class FakeClient:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.chat = NS(completions=NS(create=self.create))

    def create(self, **kw):
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out


def make(monkeypatch, clients: dict, keys=("GROQ_API_KEY", "GEMINI_API_KEY")):
    for env in ("GROQ_API_KEY", "CEREBRAS_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(env, raising=False)
    for env in keys:
        monkeypatch.setenv(env, "test")
    s = config.Settings(provider="groq", model="openai/gpt-oss-120b")
    llm = LLM(s)
    monkeypatch.setattr(llm, "client", lambda: clients[llm.provider])
    monkeypatch.setattr(llm_mod.time, "sleep", lambda secs: None)
    return llm


def test_chain_only_has_providers_with_keys(monkeypatch):
    llm = make(monkeypatch, {})
    assert [p for p, _ in llm.chain] == ["groq", "gemini"]


def test_daily_limit_switches_to_the_next_provider(monkeypatch):
    clients = {"groq": FakeClient(limit_error("tokens per day (TPD) ... Please try again in 9m27.2s.")),
               "gemini": FakeClient(ok("hello from gemini"))}
    llm = make(monkeypatch, clients)
    switched = []
    llm.on_switch = lambda provider, model, reason: switched.append(provider)
    assert llm.chat([{"role": "user", "content": "hi"}], []).text == "hello from gemini"
    assert switched == ["gemini"] and llm.provider == "gemini"


def test_short_limit_waits_on_the_same_provider(monkeypatch):
    clients = {"groq": FakeClient(limit_error("tokens per minute. Please try again in 4.2s."), ok("still groq"))}
    llm = make(monkeypatch, clients)
    waited = []
    llm.on_wait = waited.append
    assert llm.chat([{"role": "user", "content": "hi"}], []).text == "still groq"
    assert waited == [4.2] and llm.provider == "groq"


def test_keys_come_from_dot_env(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "already-set")
    (tmp_path / ".env").write_text('GEMINI_API_KEY="g-123"\nGROQ_API_KEY=from-file\nOTHER=x\n', encoding="utf-8")
    config.load_keys(tmp_path)
    import os
    assert os.environ["GEMINI_API_KEY"] == "g-123" and os.environ["GROQ_API_KEY"] == "already-set"
    assert "OTHER" not in os.environ or os.environ["OTHER"] != "x"


def test_gemini_thought_signature_goes_back():
    from forge.llm import Reply, ToolCall

    sig = {"google": {"thought_signature": "abc"}}
    msg = Reply("", [ToolCall("1", "read_file", {"path": "a.py"}, "", sig)]).as_message()
    assert msg["tool_calls"][0]["extra_content"] == sig
    assert "extra_content" not in Reply("", [ToolCall("2", "read_file", {})]).as_message()["tool_calls"][0]
