from attendance import attendance_percent, classes_can_bunk, classes_needed


def test_percent():
    assert attendance_percent(30, 40) == 75.0


def test_needed():
    assert classes_needed(20, 30) == 10


def test_bunk():
    assert classes_can_bunk(30, 36) == 4
