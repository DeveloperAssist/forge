"""Settings: which model to talk to and how careful to be.

Order of precedence: command-line flags > environment variables > forge.toml > the defaults below.
"""

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Both speak the OpenAI chat API, so one client works for either.
PROVIDERS = {
    "ollama": {"base_url": "http://localhost:11434/v1", "model": "qwen3:8b", "key_env": None},
    "groq": {"base_url": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-120b", "key_env": "GROQ_API_KEY"},
}

MODES = ("plan", "ask", "auto")  # plan = read only · ask = approve every change · auto = edits run, commands ask


@dataclass
class Settings:
    provider: str = "ollama"
    model: str = ""
    mode: str = "ask"
    max_steps: int = 40
    context_budget: int = 24_000  # tokens we let the conversation grow to before compacting
    allow_commands: list[str] = field(default_factory=lambda: [
        "pytest", "python -m pytest", "uv run pytest", "ruff", "uv run ruff",
        "git status", "git diff", "git log", "ls", "dir",
    ])

    @property
    def base_url(self) -> str:
        return PROVIDERS[self.provider]["base_url"]

    @property
    def api_key(self) -> str:
        env = PROVIDERS[self.provider]["key_env"]
        if env is None:
            return "ollama"  # Ollama ignores the key, but the client wants one
        key = os.environ.get(env, "")
        if not key:
            raise SystemExit(f"Set {env} first (free key: console.groq.com), or use --provider ollama")
        return key


def load(root: Path, **overrides) -> Settings:
    s = Settings()
    toml = root / "forge.toml"
    if toml.exists():
        for k, v in tomllib.loads(toml.read_text(encoding="utf-8")).items():
            if hasattr(s, k):
                setattr(s, k, v)
    if os.environ.get("FORGE_PROVIDER"):
        s.provider = os.environ["FORGE_PROVIDER"]
    if os.environ.get("FORGE_MODEL"):
        s.model = os.environ["FORGE_MODEL"]
    for k, v in overrides.items():
        if v is not None:
            setattr(s, k, v)
    if s.provider not in PROVIDERS:
        raise SystemExit(f"Unknown provider {s.provider!r}: use one of {', '.join(PROVIDERS)}")
    if s.mode not in MODES:
        raise SystemExit(f"Unknown mode {s.mode!r}: use one of {', '.join(MODES)}")
    s.model = s.model or PROVIDERS[s.provider]["model"]
    return s
