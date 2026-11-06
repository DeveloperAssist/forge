from merit import merit_list, top_n


def s(roll, cgpa, att):
    return {"roll": roll, "cgpa": cgpa, "attendance": att}


def test_cgpa_first():
    assert merit_list([s("22CS002", 8.4, 95), s("22CS001", 9.1, 76)]) == ["22CS001", "22CS002"]


def test_top_n():
    assert top_n([s("22CS002", 7.0, 80), s("22CS001", 9.0, 80), s("22CS003", 8.0, 80)], 2) == ["22CS001", "22CS003"]
