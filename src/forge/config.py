"""Settings: which model to talk to and how careful to be.

Order of precedence: command-line flags > environment variables > forge.toml > the defaults below.
"""

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Every one of these speaks the OpenAI chat API, so one client works for all of them.
# Groq, Gemini and OpenRouter have a free tier; Cerebras is a paid trial.
# When one runs out of free quota, Forge moves to the next one in `fallbacks` that you have a key for.
PROVIDERS = {
    "groq": {"base_url": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-120b",
             "key_env": "GROQ_API_KEY", "signup": "console.groq.com"},
    "cerebras": {"base_url": "https://api.cerebras.ai/v1", "model": "gpt-oss-120b",
                 "key_env": "CEREBRAS_API_KEY", "signup": "cloud.cerebras.ai"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "model": "gemini-3.5-flash",
               "key_env": "GEMINI_API_KEY", "signup": "aistudio.google.com"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "model": "openai/gpt-oss-120b:free",
                   "key_env": "OPENROUTER_API_KEY", "signup": "openrouter.ai"},
    "ollama": {"base_url": "http://localhost:11434/v1", "model": "forge-8b",  # optional: needs a GPU, forge setup
               "key_env": None, "signup": "ollama.com"},
}

MODES = ("plan", "ask", "auto")  # plan = read only · ask = approve every change · auto = edits run, commands ask


@dataclass
class Settings:
    provider: str = "groq"
    model: str = ""
    mode: str = "ask"
    max_steps: int = 40
    context_budget: int = 24_000  # tokens we let the conversation grow to before compacting
    # cerebras is not in the list: since July 2026 it is a card-only $5 trial, not a free tier
    fallbacks: list[str] = field(default_factory=lambda: ["groq", "gemini", "openrouter"])
    allow_commands: list[str] = field(default_factory=lambda: [
        "pytest", "python -m pytest", "uv run pytest", "ruff", "uv run ruff",
        "git status", "git diff", "git log", "ls", "dir",
    ])

    def chain(self) -> list[tuple[str, str]]:
        """(provider, model) pairs to try in order: the one you picked first, then the fallbacks you have keys for."""
        out = [(self.provider, self.model)]
        for name in self.fallbacks:
            if name != self.provider and has_key(name):
                out.append((name, PROVIDERS[name]["model"]))
        return out


def has_key(provider: str) -> bool:
    env = PROVIDERS[provider]["key_env"]
    return env is None or bool(os.environ.get(env))


def api_key(provider: str) -> str:
    env = PROVIDERS[provider]["key_env"]
    if env is None:
        return "local"  # Ollama ignores the key, but the client wants one
    key = os.environ.get(env, "")
    if not key:
        raise SystemExit(f"Set {env} first (free key: {PROVIDERS[provider]['signup']}), or pick another --provider")
    return key


def load_keys(*folders: Path) -> None:
    """Read API keys from a .env file (KEY=value lines). Only our key names, and never over a key already set."""
    names = {p["key_env"] for p in PROVIDERS.values() if p["key_env"]}
    for folder in folders:
        env = folder / ".env"
        if not env.is_file():
            continue
        for line in env.read_text(encoding="utf-8").splitlines():
            name, _, value = line.strip().partition("=")
            if name in names and value and not os.environ.get(name):
                os.environ[name] = value.strip().strip('"').strip("'")


def load(root: Path, **overrides) -> Settings:
    load_keys(root, Path.cwd(), Path.home() / ".forge")  # the project, where you ran forge, then your own
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


def fit_to_model(s: Settings) -> str:
    """For local models: size the context budget to the model's real window. Returns a warning, or ""."""
    if s.provider != "ollama":
        return ""
    from .local_models import DEFAULT_WINDOW, budget_for, window

    n_ctx = window(s.model)
    if n_ctx is None:
        return (f"Ollama has no model {s.model!r} (or is not running). Run `forge setup` once, "
                "or pick one with --model.")
    s.context_budget = min(s.context_budget, budget_for(n_ctx))
    if n_ctx <= DEFAULT_WINDOW:
        return (f"{s.model} has only a {n_ctx:,}-token window: on long tasks it will silently forget the task. "
                "Run `forge setup` and use forge-8b or forge-4b.")
    return ""
