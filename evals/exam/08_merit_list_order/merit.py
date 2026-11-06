"""Placement-cell merit list."""


def merit_list(students):
    """Order: higher CGPA first; if CGPA ties, higher attendance first;
    if both tie, lower roll number first. Returns the list of roll numbers."""
    ranked = sorted(students, key=lambda s: s["roll"])
    ranked = sorted(ranked, key=lambda s: s["cgpa"], reverse=True)
    ranked = sorted(ranked, key=lambda s: s["attendance"], reverse=True)
    return [s["roll"] for s in ranked]


def ranks(students):
    """{roll: rank}. Students with the same CGPA AND attendance share a rank,
    and the next rank is skipped (1, 2, 2, 4 style)."""
    result = {}
    for i, roll in enumerate(merit_list(students)):
        result[roll] = i + 1
    return result


def top_n(students, n):
    return merit_list(students)[:n]
