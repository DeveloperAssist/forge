"""Seat number -> berth type for Indian Railways style coaches (simplified, sample)."""

COACH_SIZE = {"SL": 72, "3A": 72, "2A": 48}

# berths repeat in bays
PATTERN = {
    "SL": ["LB", "MB", "UB", "LB", "MB", "UB", "SL", "SU"],
    "3A": ["LB", "MB", "UB", "LB", "MB", "UB", "SL", "SU"],
    "2A": ["LB", "UB", "LB", "UB", "SL", "SU"],
}

NAMES = {
    "LB": "Lower",
    "MB": "Middle",
    "UB": "Upper",
    "SL": "Side Lower",
    "SU": "Side Upper",
}


def check_seat(coach: str, seat: int) -> None:
    if coach not in COACH_SIZE:
        raise ValueError(f"unknown class {coach}")
    if not 1 <= seat <= COACH_SIZE[coach]:
        raise ValueError(f"no such seat {seat} in {coach}")


def berth_type(coach: str, seat: int) -> str:
    check_seat(coach, seat)
    cycle = PATTERN[coach]
    return cycle[(seat - 1) % len(cycle)]


def berth_name(coach: str, seat: int) -> str:
    return NAMES[berth_type(coach, seat)]


def lower_berths(coach: str, seats: list[int]) -> list[int]:
    """Seats from `seats` that are lower berths (for senior citizens)."""
    return [s for s in seats if berth_type(coach, s) in ("LB", "SL")]
