"""SGPA / CGPA on a 10-point scale (sample grading scheme)."""

POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}


def grade_points(grade: str) -> int:
    grade = grade.strip().upper()
    if grade not in POINTS:
        raise ValueError(f"unknown grade {grade!r}")
    return POINTS[grade]


def sgpa(subjects: list[tuple[str, int]]) -> float:
    """subjects = [(grade, credits), ...] for one semester."""
    if not subjects:
        return 0.0
    total = 0
    for grade, _credits in subjects:
        total += grade_points(grade)
    return round(total / len(subjects), 2)


def cgpa(semesters: list[list[tuple[str, int]]]) -> float:
    """CGPA over all semesters = weighted over every subject taken."""
    every = [s for sem in semesters for s in sem]
    return sgpa(every)


def has_backlog(subjects: list[tuple[str, int]]) -> bool:
    return any(grade_points(g) == 0 and c > 0 for g, c in subjects)


def result_line(name: str, subjects: list[tuple[str, int]]) -> str:
    status = "BACKLOG" if has_backlog(subjects) else "PASS"
    return f"{name}: SGPA {sgpa(subjects):.2f} ({status})"
