import placements
from placements import Company, Student

COMPANIES = [
    Company("Acme Tech", 6.0, 6.5, 0, []),
    Company("ByteKart", 12.0, 7.5, 0, ["CSE", "IT"]),
    Company("CoreMotors", 9.0, 6.0, 1, ["ME", "EE"]),
    Company("DataNest", 12.0, 7.0, 2, []),
    Company("EzPay", 18.0, 8.5, 0, ["CSE"]),
    Company("FinServe", 4.5, 6.0, 3, []),
]


def test_cse_unplaced_topper():
    s = Student("1", "Asha", "CSE", 9.0)
    assert placements.eligible_companies(s, COMPANIES) == ["EzPay", "ByteKart", "DataNest", "Acme Tech", "FinServe"]


def test_cgpa_cutoff_is_inclusive():
    s = Student("2", "Ravi", "IT", 7.5)
    assert placements.eligible_companies(s, COMPANIES) == ["ByteKart", "DataNest", "Acme Tech", "FinServe"]


def test_backlogs_and_branch():
    s = Student("3", "Imran", "ME", 7.2, backlogs=1)
    assert placements.eligible_companies(s, COMPANIES) == ["DataNest", "CoreMotors", "FinServe"]


def test_dream_offer_rule():
    s = Student("4", "Neha", "CSE", 9.2, placed_lpa=8.0)  # needs >= 12.0
    assert placements.eligible_companies(s, COMPANIES) == ["EzPay", "ByteKart", "DataNest"]
    s2 = Student("5", "Om", "CSE", 9.2, placed_lpa=12.1)  # needs >= 18.15
    assert placements.eligible_companies(s2, COMPANIES) == []


def test_empty_inputs():
    assert placements.eligible_companies(Student("6", "X", "CSE", 10.0), []) == []
