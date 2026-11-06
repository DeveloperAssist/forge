"""Placement-cell merit list."""


def _key(s):
    return (-s["cgpa"], -s["attendance"], s["roll"])


def merit_list(students):
    """Order: higher CGPA first; if CGPA ties, higher attendance first;
    if both tie, lower roll number first. Returns the list of roll numbers."""
    return [s["roll"] for s in sorted(students, key=_key)]


def ranks(students):
    """{roll: rank}. Students with the same CGPA AND attendance share a rank,
    and the next rank is skipped (1, 2, 2, 4 style)."""
    ordered = sorted(students, key=_key)
    result = {}
    prev = None
    rank = 0
    for i, st in enumerate(ordered):
        score = (st["cgpa"], st["attendance"])
        if score != prev:
            rank = i + 1
            prev = score
        result[st["roll"]] = rank
    return result


def top_n(students, n):
    return merit_list(students)[:n]
