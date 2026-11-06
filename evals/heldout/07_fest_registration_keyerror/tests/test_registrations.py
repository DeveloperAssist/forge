from registrations import contact_list


def test_contact_line():
    rows = [{"name": "Aman", "college": "BIT", "phone": "90000 00001", "event": "Hackathon", "team": "Bugs"}]
    assert contact_list(rows) == ["Aman (BIT) - 90000 00001"]
