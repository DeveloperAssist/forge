"""The agent loop: ask the model, run the tools it asks for, send back the results, repeat until it answers."""

import re
from collections.abc import Callable

from . import tools
from .checkpoints import Checkpoints
from .llm import LLM
from .prompt import system_prompt
from .safety import Workspace

Event = Callable[..., None]  # on_event(kind, **details): the screen and the trace listen to these

SUMMARY_PROMPT = """Summarise this coding session so far for yourself, so you can continue without the full history.
Keep: the user's goal, decisions made, files changed (and how), commands run and their results, what is still left
to do, and any exact names (files, functions, errors) you will need. Short bullet points, no greetings."""


class Agent:
    def __init__(self, llm: LLM, ws: Workspace, max_steps: int = 40, on_event: Event | None = None,
                 context_budget: int = 24_000, checkpoints: Checkpoints | None = None, helper: bool = False):
        self.llm = llm
        self.ws = ws
        self.max_steps = max_steps
        self.on_event = on_event or (lambda kind, **d: None)
        self.context_budget = context_budget
        self.checkpoints = checkpoints
        self.helper = helper
        self.messages: list[dict] = []
        self.tokens = {"prompt": 0, "output": 0, "last_prompt": 0}
        if not helper:
            ws.explore = self.explore

    # ------------------------------------------------------------------------------------------------ the loop
    def ask(self, user_text: str) -> str:
        if self.checkpoints:
            self.checkpoints.snapshot(user_text)  # /undo comes back to here
        # the system prompt is rebuilt every turn: the mode, git status, FORGE.md or skills may have changed
        system = {"role": "system", "content": system_prompt(self.ws.root, self.ws.mode, self.ws.skills,
                                                             helper=self.helper)}
        self.messages = [system] + [m for m in self.messages if m["role"] != "system"]
        self.messages.append({"role": "user", "content": user_text})
        self.on_event("user", text=user_text)
        self.ws.changed.clear()
        self.ws.last_exit = None
        pushbacks = 0

        for step in range(1, self.max_steps + 1):
            if self.tokens["last_prompt"] > self.context_budget:
                self.compact()
            self.on_event("thinking", step=step)
            reply = self.llm.chat(self.messages, tools.schemas(self.ws))
            self.count(reply)
            self.messages.append(reply.as_message())

            if not reply.tool_calls:  # no tool requested: the model says it is done
                problem = self.check_done(reply.text)
                if problem and pushbacks < 3:  # don't take its word for it: send it back to work
                    pushbacks += 1
                    self.on_event("check", text=problem)
                    self.messages.append({"role": "user", "content": f"[automatic check] {problem}"})
                    self.ws.last_exit = None  # one pushback per failed run: an honest "still failing" may stand
                    continue
                self.on_event("answer", text=reply.text)
                return reply.text

            if reply.text:
                self.on_event("note", text=reply.text)
            for call in reply.tool_calls:
                self.on_event("tool_call", name=call.name, args=call.args)
                if call.bad_args:
                    result = f"Error: your arguments were not valid JSON: {call.bad_args[:300]}"
                else:
                    result = tools.run_tool(self.ws, call.name, call.args)
                self.on_event("tool_result", name=call.name, result=result)
                if call.name == "update_plan":
                    self.on_event("plan", text=self.ws.plan)
                self.messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        text = f"I stopped after {self.max_steps} steps without finishing. Tell me how to continue."
        self.on_event("answer", text=text)
        return text

    # ------------------------------------------------------------------------------------------------ checks
    def check_done(self, text: str) -> str:
        """Small models sometimes say "fixed it!" without changing anything. Compare the claim with what happened."""
        if not text.strip():
            return "You replied with nothing. Carry on with the task using the tools, or say what is blocking you."
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        last = sentences[-1].lower()
        if last.endswith(":") or re.match(r"(let's|let me|i will|i'll|next,? i|now,? i|i need to)\b", last):
            return "You said what you will do next but did not do it. Call the tool now, in this reply."
        if self.ws.last_exit not in (None, 0):
            changed = ", ".join(sorted(self.ws.changed)) or "no files"
            return (f"The last command you ran failed (exit code {self.ws.last_exit}) and you have changed "
                    f"{changed} so far. It is not fixed yet. Read the error, change the code, run it again. "
                    "If you are stuck, say exactly what is still failing.")
        return ""

    # ------------------------------------------------------------------------------------------------ context
    def compact(self) -> None:
        """The conversation is too long for the model: replace the old part with a summary written by the model.

        The newest turns stay word for word. We cut only at a user message, so a tool call is never separated
        from its result (the API rejects that)."""
        keep_from = len(self.messages)
        users = [i for i, m in enumerate(self.messages) if m["role"] == "user"]
        if len(users) >= 2:
            keep_from = users[-1]  # keep the current task's turn whole
        old = self.messages[1:keep_from]
        if not old:  # one long task: keep every step, but clear the bulky output of all but the last 6 tools
            results = [m for m in self.messages if m["role"] == "tool"]
            for m in results[:-6]:
                if not m["content"].startswith("[cleared"):
                    m["content"] = f"[cleared to save space: {len(m['content'])} characters; run it again if needed]"
            self.tokens["last_prompt"] = 0
            self.on_event("compact", before=self.context_budget, kept=len(self.messages))
            return
        transcript = "\n".join(f"{m['role']}: {str(m.get('content') or m.get('tool_calls'))[:2000]}" for m in old)
        reply = self.llm.chat([{"role": "system", "content": SUMMARY_PROMPT},
                               {"role": "user", "content": transcript}], [])
        summary = {"role": "user", "content": "[summary of the earlier conversation]\n" + reply.text}
        before = self.tokens["last_prompt"]
        self.messages = [self.messages[0], summary] + self.messages[keep_from:]
        self.tokens["last_prompt"] = 0
        self.on_event("compact", before=before, kept=len(self.messages))

    def explore(self, question: str) -> str:
        """A helper agent: same model, read-only tools, an empty conversation. Only its answer comes back."""
        helper_ws = Workspace(self.ws.root, "plan", self.ws.approve, self.ws.allow_commands)
        helper_ws.skills = {}

        def relay(kind, **d):  # show the helper's steps indented, so you can see it work
            if kind in ("tool_call", "tool_result"):
                self.on_event("helper_" + kind, **d)

        helper = Agent(self.llm, helper_ws, max_steps=15, on_event=relay, helper=True)
        answer = helper.ask(question)
        self.tokens["prompt"] += helper.tokens["prompt"]
        self.tokens["output"] += helper.tokens["output"]
        return answer

    def count(self, reply) -> None:
        self.tokens["prompt"] += reply.prompt_tokens
        self.tokens["output"] += reply.output_tokens
        self.tokens["last_prompt"] = reply.prompt_tokens  # how full the context window is right now
