import pytest

import attendance


@pytest.mark.parametrize(
    "attended,total,target,expected",
    [
        (30, 36, 75, 4),
        (30, 40, 75, 0),   # exactly 75%: skipping even one drops below
        (20, 30, 75, 0),   # already below target
        (40, 40, 75, 13),
        (45, 50, 80, 6),
        (0, 0, 75, 0),
    ],
)
def test_can_bunk(attended, total, target, expected):
    assert attendance.classes_can_bunk(attended, total, target) == expected


def test_bunk_result_really_keeps_target():
    for attended in range(0, 60):
        for total in range(attended, 60):
            b = attendance.classes_can_bunk(attended, total)
            assert b >= 0
            if total + b:
                assert attended * 100 >= 75 * (total + b) or b == 0
            assert attended * 100 < 75 * (total + b + 1)


def test_needed_unchanged():
    assert attendance.classes_needed(20, 30) == 10
    assert attendance.classes_needed(30, 40) == 0
