import pytest

import grades


@pytest.mark.parametrize(
    "subjects,expected",
    [
        ([("O", 4), ("B", 2)], 8.67),
        ([("A", 3), ("A", 3)], 8.0),
        ([("A+", 4), ("C", 1)], 8.2),
        ([("O", 3), ("F", 3)], 5.0),
        ([("B+", 4), ("P", 2), ("A", 3)], 6.67),
        ([("A", 4), ("O", 0)], 8.0),       # audit course changes nothing
        ([("b+", 2), (" a ", 2)], 7.5),
    ],
)
def test_sgpa_weighted(subjects, expected):
    assert grades.sgpa(subjects) == pytest.approx(expected)


def test_cgpa_weights_every_subject():
    sem1 = [("O", 4), ("B", 2)]          # 52 / 6
    sem2 = [("A", 2)]                    # 16 / 2
    assert grades.cgpa([sem1, sem2]) == pytest.approx(8.5)


def test_result_line():
    assert "8.67" in grades.result_line("Riya", [("O", 4), ("B", 2)])
