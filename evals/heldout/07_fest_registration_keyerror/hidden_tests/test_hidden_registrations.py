import json

import registrations

ROWS = [
    {"name": "Aman", "college": "BIT", "phone": "90000 00001", "event": "Hackathon", "team": "Bugs"},
    {"name": "Riya", "college": "BIT", "event": "Hackathon", "team": "Bugs"},
    {"name": "Kabir", "college": "NIT", "phone": "", "event": "Hackathon", "team": "Null Ptr"},
    {"name": "Sana", "college": "XLRI", "phone": "90000 00004", "event": "Quiz"},
    {"name": "Dev", "college": "IIT", "event": "Quiz", "team": ""},
    {"name": "Meera", "college": "IIT", "event": "Solo Dance"},
]


def test_contact_list_missing_phone():
    lines = registrations.contact_list(ROWS)
    assert len(lines) == 6
    assert lines[1] == "Riya (BIT) - -"
    assert lines[2] == "Kabir (NIT) - -"
    assert lines[3] == "Sana (XLRI) - 90000 00004"


def test_team_count_with_solo():
    # Bugs, Null Ptr, + 3 solo people
    assert registrations.team_count(ROWS) == 5


def test_report_from_file(tmp_path):
    path = tmp_path / "export.json"
    path.write_text(json.dumps(ROWS), encoding="utf-8")
    text = registrations.report(registrations.load(str(path)))
    assert text.splitlines()[0] == "6 people, 5 teams, 3 events"
    assert "Meera (IIT) - -" in text
