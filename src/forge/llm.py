"""One small client for any OpenAI-compatible chat API (Ollama on your laptop, or Groq's free tier)."""

import json
import re
from dataclasses import dataclass, field

from openai import OpenAI

from .config import Settings


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


class LLM:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(base_url=settings.base_url, api_key=settings.api_key, max_retries=4, timeout=300)

    def chat(self, messages: list[dict], tools: list[dict]) -> Reply:
        extra = {}
        if self.settings.provider == "ollama":
            extra["reasoning_effort"] = "none"  # qwen3 would otherwise think out loud first: slow on 8 GB
        r = self.client.chat.completions.create(
            model=self.settings.model, messages=messages, tools=tools or None, temperature=0.2, **extra,
        )
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
