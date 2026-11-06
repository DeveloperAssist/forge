"""Attendance helper for the 75% rule."""


def attendance_percent(attended: int, total: int) -> float:
    if total == 0:
        return 100.0
    return round(attended * 100 / total, 2)


def classes_can_bunk(attended: int, total: int, target: int = 75) -> int:
    """How many of the NEXT classes can I skip and still be at or above target %?"""
    bunk = 0
    while attended * 100 >= target * (total + bunk + 1):
        bunk += 1
    return bunk


def classes_needed(attended: int, total: int, target: int = 75) -> int:
    """How many of the NEXT classes must I attend in a row to reach target %?"""
    need = 0
    while (attended + need) * 100 < target * (total + need):
        need += 1
    return need
