# Forge: build your own coding agent in Python

Forge is a small AI coding agent that runs in your terminal. You give it a task, like
"fix the failing test". It reads your files, edits them, runs the tests, and checks the result before it says "done".

- **No agent framework.** About 1,400 lines of plain Python: one loop, one list of tools, one model client.
- **Free to run, no GPU needed.** It uses free online models: Groq first, then Google Gemini when Groq's
  daily limit runs out. It switches by itself.
- **Safe by default.** It asks before every change. It never runs dangerous commands. `/undo` puts your files back.
- **Tested like the real ones.** It is scored on 32 broken projects it has never seen, graded by hidden tests
  (see [How well it works](#how-well-it-works)).

```
› fix the failing tests in split_bill
  read_file split.py · run_command pytest -q
  ✗ automatic check: you changed split.py but have not run anything since
  run_command pytest -q → 5 passed
› /undo   put back: split.py
```

## Quick start

You need [uv](https://docs.astral.sh/uv/) and Python 3.14 (uv installs it for you).

```bash
git clone <this repo> forge && cd forge
uv sync
```

**Get free API keys.** One is enough. Two let Forge switch when the first one hits its daily limit.

| Provider | Where to get the key | Free limit (check your console, it changes) |
|---|---|---|
| Groq (default) | console.groq.com | about 200,000 tokens a day (around 13 tasks) |
| Google Gemini (backup) | aistudio.google.com | shown per model in AI Studio |
| OpenRouter (last resort) | openrouter.ai | about 50 requests a day |

Put the keys in a file called `.env` in the Forge folder (it is in `.gitignore`, so it is never committed):

```
GROQ_API_KEY=...
GEMINI_API_KEY=...
```

Forge also reads `.env` from the project you point it at, and from `~/.forge/.env`. Never paste a key into code.

**Run it:**

```bash
uv run forge --dir examples/split_bill            # chat with it about a project
uv run forge --dir examples/split_bill "fix the failing tests"   # one task, then exit
uv run forge --mode plan --dir my_project         # read-only: it can look but not touch
```

## Commands

| Inside Forge | What it does |
|---|---|
| `/mode plan\|ask\|auto` | How careful to be. **plan** = read only. **ask** = you approve every edit and command (default). **auto** = edits go through, commands still ask. |
| `/undo` | Put the files back the way they were before the last task |
| `/init` | Forge studies the project and writes `FORGE.md`, its notes for next time |
| `/skills` | List the skills it can load |
| `/tokens` | How full the conversation (context) is |
| `/clear`, `/exit` | Forget the conversation; quit |

Options: `--provider groq|gemini|openrouter`, `--model NAME`, `--mode`, `--dir`.

## How it works

```
you ──► agent loop ──► model (Groq → Gemini → OpenRouter)
            ▲    │
            │    ▼ the model asks for a tool
            │  tools: read_file · list_files · search · edit_file · write_file
            │         run_command · update_plan · explore · use_skill
            │    │
            └────┘ the result goes back to the model; repeat until it answers
```

| File | Job |
|---|---|
| `agent.py` | The loop. Also the **done-check**: when the model says "fixed", Forge compares that with what really happened (did it run the tests? did they pass?) and sends it back to work, up to 3 times. |
| `tools.py` | Each tool is a plain Python function. Its docstring and type hints become the JSON schema the model sees. |
| `safety.py` | A path jail (no file outside the project), a block list (`rm -rf /`, `sudo`, `git push`, `.env`, `curl … \| sh` …), approvals, and "never edit a file you haven't read". |
| `llm.py` | One OpenAI-compatible client for every provider. Waits out short per-minute limits; **switches provider** on a daily limit, an overloaded server (503) or a too-big request (413). |
| `prompt.py` | The system prompt: rules, mode, git status, `FORGE.md`, skills. |
| `checkpoints.py` | Snapshots before each task, for `/undo`. |
| `skills.py` | Skills in `.forge/skills/<name>/SKILL.md`. Only their one-line descriptions sit in the prompt; the full text loads when needed. |
| `trace.py` | Every step of every task, one JSON line each, in `.forge/traces/`. Read it when something goes wrong. |
| `exam.py` | The exam runner (`forge-exam`). |

Other things it does:

- **Helper agent** (`explore`): a fresh agent with read-only tools looks around a big codebase and returns only its answer, so the main conversation stays small.
- **Compaction**: when the conversation gets too long, the model writes a summary of the old part.
- **Read-only when you ask**: "don't change any code" or "just explain" switches that task to plan mode.
- **Repeat detector**: if the model makes the same call twice with the same result, Forge tells it to try something else.

## How well it works

The exam is like SWE-bench: each task is a small broken project. The agent sees the task and the visible tests.
A **hidden** test suite, which the agent never sees, decides pass or fail. The tasks use Indian student examples:
GST paise rounding, UPI amounts, SGPA, IPL net run rate, PNR parsing, Zomato coupons.

| Run (model `gpt-oss-120b`) | Score |
|---|---|
| Main exam, first run | 16 / 20 |
| Main exam, after the fixes below | **18 / 20** |
| Held-out exam: 12 new tasks written by a separate agent, run **once** | **12 / 12** |

The exam runs used Cerebras (the same `gpt-oss-120b` model as Groq's free default) because a full exam needs
more than one day of Groq's free limit. Still failing: 06 (SGPA division) and 07 (PNR parsing).

What the failures taught us, and what changed:

1. **"All tests pass" is not the same as fixed.** Both failures said all tests pass, and the visible tests did pass.
   In task 06 the agent fixed the SGPA function the task named, and missed the same bug in the CGPA function next to it.
2. **Told "don't change any code, just explain", the model changed the code** so that a wrong test would pass.
   Forge now runs such requests read-only, and its rules say: never change correct code to pass a wrong test.

Run the exam yourself:

```bash
uv run forge-exam                       # Groq, 20 tasks (uses most of a day's free limit)
uv run forge-exam --set heldout         # the 12 held-out tasks
uv run forge-exam --fallback            # allow switching providers mid-exam
uv run python evals/check_exam.py       # check every task is valid: hidden tests fail on the bug, pass on the fix
```

Results are saved in `evals/results/`. A task stopped by a rate limit is shown as `----` (not scored), never as a fail.

## Tests

```bash
uv run pytest        # 59 offline tests, with a fake model: no key, no internet
uv run ruff check
```

## Project layout

```
src/forge/        the agent (files above)
tests/            offline tests (a FakeLLM plays the model)
examples/         split_bill: a small broken project to try Forge on
evals/exam/       20 exam tasks
evals/heldout/    12 held-out tasks
evals/results/    exam results (JSON)
```

## Credits

Made by Developers Assist for students. The exam tasks and examples are our own writing; all names and data in
them are made up.
