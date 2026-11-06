"""Training & Placement cell helpers (all companies and students are made-up samples)."""
from dataclasses import dataclass, field


@dataclass
class Student:
    roll: str
    name: str
    branch: str
    cgpa: float
    backlogs: int = 0
    placed_lpa: float | None = None


@dataclass
class Company:
    name: str
    package_lpa: float
    min_cgpa: float
    max_backlogs: int = 0
    branches: list[str] = field(default_factory=list)


def format_package(lpa: float) -> str:
    """12.5 -> '12.5 LPA', 8.0 -> '8 LPA'."""
    text = f"{lpa:.2f}".rstrip("0").rstrip(".")
    return f"{text} LPA"


def drive_summary(companies: list[Company]) -> str:
    if not companies:
        return "No drives yet"
    top = max(companies, key=lambda c: c.package_lpa)
    return f"{len(companies)} companies, highest {format_package(top.package_lpa)} ({top.name})"


def eligible_companies(student: Student, companies: list[Company]) -> list[str]:
    """Names of companies `student` may apply to, highest package first (ties by name)."""
    ok = []
    for c in companies:
        if student.cgpa < c.min_cgpa:
            continue
        if student.backlogs > c.max_backlogs:
            continue
        if c.branches and student.branch not in c.branches:
            continue
        if student.placed_lpa is not None and c.package_lpa < 1.5 * student.placed_lpa:
            continue
        ok.append(c)
    ok.sort(key=lambda c: (-c.package_lpa, c.name))
    return [c.name for c in ok]
