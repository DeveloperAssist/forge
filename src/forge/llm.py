"""One small client for any OpenAI-compatible chat API (Ollama on your laptop, or Groq's free tier)."""

import json
import re
import time
from dataclasses import dataclass, field

import openai
from openai import OpenAI

from .config import PROVIDERS, Settings, api_key


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict
    bad_args: str = ""  # set when the model sent arguments that are not valid JSON


@dataclass
class Reply:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    prompt_tokens: int = 0
    output_tokens: int = 0

    def as_message(self) -> dict:
        """The assistant turn, in the shape the API wants it back next time."""
        msg = {"role": "assistant", "content": self.text}
        if self.tool_calls:
            msg["tool_calls"] = [
                {"id": c.id, "type": "function",
                 "function": {"name": c.name, "arguments": c.bad_args or json.dumps(c.args)}}
                for c in self.tool_calls
            ]
        return msg


THINK = re.compile(r"<think>.*?</think>", re.S)
MAX_WAIT = 20 * 60  # longer than this, give up and tell the user
SHORT_WAIT = 90     # shorter than this, wait on the same provider instead of switching


def limited(e: Exception) -> bool:
    """Is this the server saying "too much for your free tier" (rate limit, or a request too big for it)?"""
    return getattr(e, "status_code", None) in (413, 429) or isinstance(e, openai.RateLimitError)


def wait_seconds(error: str) -> float | None:
    """Groq says e.g. "Please try again in 9m27.216s". Turn that into seconds (None if it does not say)."""
    m = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m)?([\d.]+)?s?", error)
    if not m or not any(m.groups()):
        return None
    h, mins, s = m.groups()
    return int(h or 0) * 3600 + int(mins or 0) * 60 + float(s or 0)


def retry_after(e: Exception) -> float | None:
    """Some servers put the wait in the Retry-After header instead of the message."""
    try:
        return float(e.response.headers.get("retry-after"))
    except (AttributeError, TypeError, ValueError):
        return None


class LLM:
    """Talks to the first provider in the chain; when its free quota runs out, moves to the next one."""

    on_wait = None    # on_wait(seconds): the screen shows "free-tier limit, waiting..."
    on_switch = None  # on_switch(provider, model, reason): the screen shows which model takes over

    def __init__(self, settings: Settings):
        self.settings = settings
        self.chain = settings.chain()
        self.at = 0  # which provider in the chain we are using now
        self.clients = {}

    @property
    def provider(self) -> str:
        return self.chain[self.at][0]

    @property
    def model(self) -> str:
        return self.chain[self.at][1]

    def client(self) -> OpenAI:
        if self.provider not in self.clients:
            self.clients[self.provider] = OpenAI(base_url=PROVIDERS[self.provider]["base_url"],
                                                 api_key=api_key(self.provider), max_retries=2, timeout=300)
        return self.clients[self.provider]

    def next_provider(self, reason: str) -> bool:
        if self.at + 1 >= len(self.chain):
            return False
        self.at += 1
        if self.on_switch:
            self.on_switch(self.provider, self.model, reason)
        return True

    def chat(self, messages: list[dict], tools: list[dict]) -> Reply:
        for _ in range(12):
            extra = {"reasoning_effort": "none"} if self.provider == "ollama" else {}  # qwen3: no thinking aloud
            try:
                r = self.client().chat.completions.create(
                    model=self.model, messages=messages, tools=tools or None, temperature=0.2, **extra,
                )
                break
            except (openai.RateLimitError, openai.APIStatusError) as e:
                if not limited(e):
                    raise
                secs = wait_seconds(str(e)) or retry_after(e)
                if secs is not None and secs <= SHORT_WAIT:  # a per-minute limit: just wait a little
                    if self.on_wait:
                        self.on_wait(secs)
                    time.sleep(secs + 1)
                elif self.next_provider(f"{self.provider} free limit reached"):  # daily limit: next provider
                    continue
                elif secs is not None and secs <= MAX_WAIT:  # nowhere else to go: wait if it is not too long
                    if self.on_wait:
                        self.on_wait(secs)
                    time.sleep(secs + 2)
                else:
                    raise
        else:
            raise RuntimeError("Still rate-limited after many waits. Try again later or add another free key.")
        m = r.choices[0].message
        calls = []
        for c in m.tool_calls or []:
            try:
                args, bad = json.loads(c.function.arguments or "{}"), ""
            except json.JSONDecodeError:
                args, bad = {}, c.function.arguments
            calls.append(ToolCall(c.id, c.function.name, args, bad))
        text = THINK.sub("", m.content or "").strip()
        usage = r.usage
        return Reply(text, calls, usage.prompt_tokens if usage else 0, usage.completion_tokens if usage else 0)
