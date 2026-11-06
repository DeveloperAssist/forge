from splitter import request_lines, rupees


def test_rupees():
    assert rupees(12345) == "Rs 123.45"
    assert rupees(5) == "Rs 0.05"


def test_request_lines():
    lines = request_lines("Aman", {"Aman": 300, "Riya": 300, "Kabir": 0})
    assert lines == ["Riya -> Aman: Rs 3.00"]
