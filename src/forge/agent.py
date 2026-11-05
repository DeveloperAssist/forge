"""The agent loop: ask the model, run the tools it asks for, send back the results, repeat until it answers."""

from collections.abc import Callable

from . import tools
from .llm import LLM
from .prompt import system_prompt
from .safety import Workspace

Event = Callable[..., None]  # on_event(kind, **details): the screen and the trace listen to these


class Agent:
    def __init__(self, llm: LLM, ws: Workspace, max_steps: int = 40, on_event: Event | None = None):
        self.llm = llm
        self.ws = ws
        self.max_steps = max_steps
        self.on_event = on_event or (lambda kind, **d: None)
        self.messages: list[dict] = []
        self.tokens = {"prompt": 0, "output": 0, "last_prompt": 0}

    def ask(self, user_text: str) -> str:
        # the system prompt is rebuilt every turn: the mode, git status or FORGE.md may have changed
        system = {"role": "system", "content": system_prompt(self.ws.root, self.ws.mode)}
        self.messages = [system] + [m for m in self.messages if m["role"] != "system"]
        self.messages.append({"role": "user", "content": user_text})

        for step in range(1, self.max_steps + 1):
            self.on_event("thinking", step=step)
            reply = self.llm.chat(self.messages, tools.schemas(self.ws.mode))
            self.count(reply)
            self.messages.append(reply.as_message())

            if not reply.tool_calls:  # no tool requested: this is the final answer
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
                self.messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        text = f"I stopped after {self.max_steps} steps without finishing. Tell me how to continue."
        self.on_event("answer", text=text)
        return text

    def count(self, reply) -> None:
        self.tokens["prompt"] += reply.prompt_tokens
        self.tokens["output"] += reply.output_tokens
        self.tokens["last_prompt"] = reply.prompt_tokens  # how full the context window is right now
