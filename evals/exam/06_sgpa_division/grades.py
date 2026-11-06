"""SGPA / CGPA calculator (10-point scale)."""

GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}


def sgpa(courses):
    """courses: list of (credits, grade). Returns SGPA rounded to 2 decimals."""
    total_credits = sum(c for c, _ in courses)
    points = sum(c * GRADE_POINTS[g] for c, g in courses)
    return round(points // total_credits, 2)


def cgpa(semesters):
    """semesters: list of (sgpa, credits) for each semester. Rounded to 2 decimals."""
    total = sum(cr for _, cr in semesters)
    return round(sum(s * cr for s, cr in semesters) // total, 2)


def cgpa_to_percentage(cg):
    return round((cg - 0.75) * 10, 2)
