"""Local models through Ollama, and the trap that comes with them.

Ollama gives every model a 4,096-token window unless you ask for more, and when the conversation is longer it
quietly drops the oldest part: for an agent, that is the task itself. So `forge setup` makes two model variants with
a bigger window, sized to fit an 8 GB GPU, and Forge reads the real window size before every session.
"""

import re

import httpx

OLLAMA = "http://localhost:11434"
DEFAULT_WINDOW = 4096  # what Ollama uses when the model does not say

# name: (base model, window). Both fit fully on an 8 GB GPU (checked with `ollama ps`: 100% GPU).
VARIANTS = {
    "forge-8b": ("qwen3:8b", 8192),
    "forge-4b": ("qwen3:4b-instruct", 16384),
}


def window(model: str) -> int | None:
    """The model's real context window in tokens, or None if Ollama is not running or has no such model."""
    try:
        r = httpx.post(f"{OLLAMA}/api/show", json={"model": model}, timeout=10)
    except httpx.HTTPError:
        return None
    if r.status_code != 200:
        return None
    m = re.search(r"^num_ctx\s+(\d+)", r.json().get("parameters", ""), re.M)
    return int(m.group(1)) if m else DEFAULT_WINDOW


def budget_for(n_ctx: int) -> int:
    """How big we let the conversation grow before compacting: leave room for one tool result and the reply."""
    return max(2_000, int(n_ctx * 0.65))


def setup(say=print) -> bool:
    """Download the base models if needed and create the forge-8b / forge-4b variants."""
    for name, (base, n_ctx) in VARIANTS.items():
        say(f"{name}: {base} with a {n_ctx:,}-token window ...")
        try:
            pull = httpx.post(f"{OLLAMA}/api/pull", json={"model": base, "stream": False}, timeout=None)
            pull.raise_for_status()
            made = httpx.post(
                f"{OLLAMA}/api/create",
                timeout=120,
                json={"model": name, "from": base, "parameters": {"num_ctx": n_ctx}, "stream": False},
            )
            made.raise_for_status()
        except httpx.HTTPError as e:
            say(f"  could not reach Ollama ({e}). Is it installed and running? https://ollama.com")
            return False
        say(f"  ready: forge --model {name}")
    return True
