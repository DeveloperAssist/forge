from forge import tools
from forge.safety import Workspace


def run(ws, name, **args):
    return tools.run_tool(ws, name, args)


def test_schema_comes_from_the_function():
    s = tools.REGISTRY["read_file"].schema["function"]
    assert s["parameters"]["required"] == ["path"]
    assert s["parameters"]["properties"]["offset"]["type"] == "integer"
    assert "numbered" in s["description"]
    assert s["parameters"]["properties"]["path"]["description"].startswith("file path")


def test_read_file_numbers_the_lines(ws):
    out = run(ws, "read_file", path="app.py")
    assert out.splitlines()[1] == "    2│     return a - b"


def test_read_file_pages_long_files(ws):
    (ws.root / "long.py").write_text("\n".join(f"x{i} = {i}" for i in range(1, 51)), encoding="utf-8")
    out = run(ws, "read_file", path="long.py", offset=10, limit=5)
    assert out.startswith("   10│ x10 = 10")
    assert "use offset=15" in out


def test_list_files_skips_caches_and_missing_folders(ws):
    (ws.root / "__pycache__").mkdir()
    (ws.root / "__pycache__" / "app.pyc").write_text("x")
    out = run(ws, "list_files")
    assert "app.py" in out and "tests/test_app.py" in out and "pyc" not in out
    assert run(ws, "list_files", path="nope").startswith("Error: There is no folder")


def test_search_finds_lines(ws):
    assert run(ws, "search", pattern=r"def \w+", files="app.py") == "app.py:1: def total(a, b):"
    assert len(run(ws, "search", pattern=r"def \w+").splitlines()) == 2  # app.py and the test file
    assert run(ws, "search", pattern="(").startswith("Error: Bad regular expression")


def test_no_blind_edits(ws):
    out = run(ws, "edit_file", path="app.py", old_text="a - b", new_text="a + b")
    assert out.startswith("Error: Read app.py")


def test_edit_replaces_exactly_one_match(ws):
    run(ws, "read_file", path="app.py")
    out = run(ws, "edit_file", path="app.py", old_text="a - b", new_text="a + b")
    assert out.startswith("Edited app.py") and "+    return a + b" in out
    assert "a + b" in (ws.root / "app.py").read_text()
    assert ws.changed == {"app.py"}


def test_edit_refuses_ambiguous_text(ws):
    (ws.root / "two.py").write_text("x = 1\nx = 1\n", encoding="utf-8")
    run(ws, "read_file", path="two.py")
    assert "appears 2 times" in run(ws, "edit_file", path="two.py", old_text="x = 1", new_text="x = 2")


def test_edit_takes_off_copied_line_numbers(ws):
    run(ws, "read_file", path="app.py")
    out = run(ws, "edit_file", path="app.py", old_text="    2│     return a - b", new_text="    2│     return a + b")
    assert out.startswith("Edited")
    assert (ws.root / "app.py").read_text().splitlines()[1] == "    return a + b"


def test_failed_edit_shows_the_closest_text(ws):
    run(ws, "read_file", path="app.py")
    out = run(ws, "edit_file", path="app.py", old_text="  return a-b", new_text="  return a+b")
    assert "closest text" in out and "return a - b" in out


def test_edit_after_someone_else_changed_the_file(ws):
    import os

    run(ws, "read_file", path="app.py")
    os.utime(ws.root / "app.py", (1, 1))  # as if the user saved it in their editor
    assert "changed since you read it" in run(ws, "edit_file", path="app.py", old_text="a - b", new_text="a + b")


def test_write_file_creates_folders(ws):
    out = run(ws, "write_file", path="pkg/new.py", content="X = 1\n")
    assert out == "Wrote pkg/new.py (1 lines)."
    assert (ws.root / "pkg" / "new.py").read_text() == "X = 1\n"


def test_run_command_reports_the_exit_code(ws):
    out = run(ws, "run_command", command="python -m pytest -q")
    assert out.startswith("exit code 1") and ws.last_exit == 1


def test_user_can_say_no(project):
    ws = Workspace(project, "ask", lambda *a: False, [])
    tools.run_tool(ws, "read_file", {"path": "app.py"})
    assert "said no" in tools.run_tool(ws, "edit_file", {"path": "app.py", "old_text": "-", "new_text": "+"})
    assert "a - b" in (project / "app.py").read_text()


def test_mistakes_become_messages_not_crashes(ws):
    assert run(ws, "fly").startswith("Error: there is no tool called fly")
    assert run(ws, "read_file", path="app.py", colour="red").startswith("Error: wrong arguments")


def test_plan_mode_only_offers_read_tools(ws):
    ws.mode = "plan"
    names = {s["function"]["name"] for s in tools.schemas(ws)}
    assert {"read_file", "search", "update_plan"} <= names
    assert not names & {"edit_file", "write_file", "run_command"}


def test_long_output_is_cut_in_the_middle():
    out = tools.cut("a" * 5000 + "b" * 5000, limit=1000)
    assert out.startswith("a" * 500) and out.endswith("b" * 500) and "characters cut" in out
