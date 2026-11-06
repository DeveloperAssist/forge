from placements import Company, Student, format_package


def test_format_package():
    assert format_package(8.0) == "8 LPA"
    assert format_package(12.5) == "12.5 LPA"


def test_dataclasses():
    s = Student("21CS001", "Asha", "CSE", 8.1)
    c = Company("Acme Tech", 6.0, 7.0)
    assert s.placed_lpa is None and c.branches == []
