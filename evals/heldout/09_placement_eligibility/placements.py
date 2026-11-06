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
