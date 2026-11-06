import httpx
import openai
from conftest import FakeLLM, call, say

from forge.agent import Agent
from forge.checkpoints import Checkpoints
from forge.llm import wait_seconds
from forge.skills import load, parse


def test_the_loop_runs_tools_then_answers(ws):
    llm = FakeLLM(call("read_file", path="app.py"),
                  call("edit_file", 1, path="app.py", old_text="a - b", new_text="a + b"),
                  call("run_command", 2, command="python -m pytest -q"),
                  say("Fixed total: it subtracted. Tests pass."))
    answer = Agent(llm, ws).ask("fix the test")
    assert answer == "Fixed total: it subtracted. Tests pass."
    assert ws.last_exit == 0
    tool_msgs = [m for m in llm.sent[-1] if m["role"] == "tool"]
    assert len(tool_msgs) == 3 and tool_msgs[2]["content"].startswith("exit code 0")


def test_a_false_done_is_sent_back(ws):
    llm = FakeLLM(call("run_command", command="python -m pytest -q"),
                  say("I fixed it, all tests pass."),            # it did not
                  say("Sorry: it still fails because total subtracts."))
    events = []
    Agent(llm, ws, on_event=lambda k, **d: events.append(k)).ask("fix the test")
    assert "check" in events
    pushed = llm.sent[2][-1]
    assert pushed["role"] == "user" and "failed (exit code 1)" in pushed["content"]


def test_saying_what_it_will_do_is_not_doing_it(ws):
    llm = FakeLLM(say("The bug is in total. Let's check the implementation in app.py."),
                  say("total subtracts instead of adding."))
    Agent(llm, ws).ask("why does the test fail?")
    assert "did not do it" in llm.sent[1][-1]["content"]


def test_step_limit(ws):
    llm = FakeLLM(*[call("list_files", i) for i in range(3)])
    assert "stopped after 3 steps" in Agent(llm, ws, max_steps=3).ask("look around")


def test_bad_json_arguments_go_back_to_the_model(ws):
    from forge.llm import Reply, ToolCall

    llm = FakeLLM(Reply("", [ToolCall("c0", "read_file", {}, bad_args='{"path": app.py')]), say("done reading."))
    Agent(llm, ws).ask("read app")
    assert "not valid JSON" in llm.sent[1][-1]["content"]


def test_helper_agent_works_in_its_own_context(ws):
    llm = FakeLLM(call("explore", question="where is total?"),
                  call("search", 1, pattern="def total"),        # the helper's turn
                  say("total is in app.py line 1."),             # the helper's answer
                  say("total lives in app.py."))
    agent = Agent(llm, ws)
    agent.ask("where is total?")
    helper_view = llm.sent[1]
    assert helper_view[0]["role"] == "system" and "HELPER" in helper_view[0]["content"]
    assert len(helper_view) == 2  # system + the question only: none of the main conversation
    main_tool_result = [m for m in llm.sent[3] if m["role"] == "tool"][0]["content"]
    assert main_tool_result == "total is in app.py line 1."


def test_compaction_summarises_old_turns(ws):
    llm = FakeLLM(say("first answer", tokens=50_000), say("- user asked X; answered."), say("second answer"))
    events = []
    agent = Agent(llm, ws, context_budget=10_000, on_event=lambda k, **d: events.append(k))
    agent.ask("question one")
    agent.ask("question two")
    assert "compact" in events
    roles = [m["role"] for m in llm.sent[-1]]
    assert roles == ["system", "user", "user"]
    assert llm.sent[-1][1]["content"].startswith("[summary of the earlier conversation]")


def test_undo_puts_files_back(ws):
    cp = Checkpoints(ws.root)
    llm = FakeLLM(call("read_file", path="app.py"),
                  call("edit_file", 1, path="app.py", old_text="a - b", new_text="a + b"),
                  call("write_file", 2, path="notes.txt", content="hi"),
                  call("run_command", 3, command="python -m pytest -q"),
                  say("Done."))
    Agent(llm, ws, checkpoints=cp).ask("fix it")
    assert (ws.root / "notes.txt").exists()
    assert sorted(cp.undo()) == ["app.py", "notes.txt"]
    assert "a - b" in (ws.root / "app.py").read_text() and not (ws.root / "notes.txt").exists()
    assert cp.undo() == []


def test_skills_are_found_and_loaded(ws):
    folder = ws.root / ".forge" / "skills" / "write-tests"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text("---\nname: write-tests\ndescription: add pytest tests\n---\n1. Read the code.",
                                     encoding="utf-8")
    ws.skills = load(ws.root)
    llm = FakeLLM(call("use_skill", name="write-tests"), say("Loaded."))
    Agent(llm, ws).ask("add tests")
    assert "write-tests: add pytest tests" in llm.sent[0][0]["content"]
    assert [m for m in llm.sent[1] if m["role"] == "tool"][0]["content"] == "1. Read the code."


def test_skill_without_header_uses_the_folder_name():
    s = parse("Just steps.", "deploy")
    assert (s.name, s.description, s.body) == ("deploy", "", "Just steps.")


def test_a_rejected_tool_call_goes_back_to_the_model(ws):
    import httpx
    import openai

    class Rejects(FakeLLM):
        def chat(self, messages, tools):
            if not self.sent:
                self.sent.append(messages)
                response = httpx.Response(400, request=httpx.Request("POST", "http://model"))
                raise openai.BadRequestError("attempted to call tool 'edit_file' which was not in request.tools",
                                             response=response, body=None)
            return super().chat(messages, tools)

    ws.mode = "plan"
    llm = Rejects(say("Plan: 1. change total to add."))
    assert Agent(llm, ws).ask("make a plan") == "Plan: 1. change total to add."
    note = llm.sent[1][-1]["content"]
    assert "rejected" in note and "read_file" in note and "edit_file, " not in note


def test_changed_files_must_be_checked_before_done(ws):
    llm = FakeLLM(call("read_file", path="app.py"),
                  call("edit_file", 1, path="app.py", old_text="a - b", new_text="a + b"),
                  say("Fixed. All tests pass."),                   # it never ran them
                  call("run_command", 2, command="python -m pytest -q"),
                  say("Fixed and checked: tests pass."))
    assert Agent(llm, ws).ask("fix it") == "Fixed and checked: tests pass."
    assert "have not run anything since" in llm.sent[3][-1]["content"]


def test_unparsable_reply_gets_a_retry(ws):
    response = httpx.Response(400, request=httpx.Request("POST", "http://x"))

    class Garbles(FakeLLM):
        def chat(self, messages, tools):
            if len(self.sent) == 0:
                self.sent.append(list(messages))
                raise openai.BadRequestError("Parsing failed. See 'failed_generation' for more details.",
                                             response=response, body=None)
            return super().chat(messages, tools)

    llm = Garbles(say("Nothing to change."))
    assert Agent(llm, ws).ask("look") == "Nothing to change."
    assert "rejected by the server" in llm.sent[1][-1]["content"]


def test_wait_seconds_reads_groq_messages():
    assert wait_seconds("Please try again in 9m27.216s. Need more tokens?") == 9 * 60 + 27.216
    assert wait_seconds("try again in 1m33.7s") == 93.7
    assert wait_seconds("try again in 2.5s") == 2.5
    assert wait_seconds("quota exceeded") is None
