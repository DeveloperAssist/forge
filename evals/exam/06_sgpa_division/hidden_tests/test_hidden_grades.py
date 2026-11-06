import grades


def test_sgpa_mixed():
    assert grades.sgpa([(4, "A+"), (3, "A"), (3, "B+")]) == 8.1


def test_sgpa_rounding():
    # 40 + 21 + 12 + 4 + 24 = 101 points over 13 credits = 7.769...
    assert grades.sgpa([(4, "O"), (3, "B+"), (2, "B"), (1, "P"), (3, "A")]) == 7.77


def test_cgpa():
    assert grades.cgpa([(8.1, 20), (7.45, 22)]) == 7.76
    assert grades.cgpa([(9.0, 21), (9.0, 23)]) == 9.0


def test_with_fail():
    assert grades.sgpa([(4, "F"), (4, "O")]) == 5.0
