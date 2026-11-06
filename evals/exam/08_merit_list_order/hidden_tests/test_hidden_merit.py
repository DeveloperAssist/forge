import merit


def s(roll, cgpa, att):
    return {"roll": roll, "cgpa": cgpa, "attendance": att}


CLASS = [
    s("22CS007", 8.4, 95),
    s("22CS003", 9.1, 76),
    s("22CS010", 9.1, 88),
    s("22CS001", 8.4, 95),
    s("22CS005", 7.9, 99),
    s("22CS002", 9.1, 88),
    s("22CS009", 8.4, 80),
]


def test_order():
    assert merit.merit_list(CLASS) == [
        "22CS002", "22CS010", "22CS003", "22CS001", "22CS007", "22CS009", "22CS005"]


def test_order_does_not_depend_on_input_order():
    assert merit.merit_list(list(reversed(CLASS))) == merit.merit_list(CLASS)


def test_ranks_share_ties():
    assert merit.ranks(CLASS) == {
        "22CS002": 1, "22CS010": 1, "22CS003": 3, "22CS001": 4, "22CS007": 4, "22CS009": 6, "22CS005": 7}


def test_top_n():
    assert merit.top_n(CLASS, 3) == ["22CS002", "22CS010", "22CS003"]
