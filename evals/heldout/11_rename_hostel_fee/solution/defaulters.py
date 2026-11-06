"""Find students who have paid less than they owe."""
import fees


def dues(student: dict) -> int:
    owed = fees.hostel_fee(student["room"], student["months"], ac=student.get("ac", False))
    return owed - student.get("paid", 0)


def defaulters(students: list[dict]) -> list[tuple[str, int]]:
    """[(name, rupees still due), ...] for anyone who owes money, biggest due first."""
    out = [(s["name"], dues(s)) for s in students]
    out = [(name, due) for name, due in out if due > 0]
    out.sort(key=lambda x: (-x[1], x[0]))
    return out
