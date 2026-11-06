"""Batting stats for the college cricket league (sample scores only)."""
from dataclasses import dataclass


@dataclass
class Innings:
    runs: int
    balls: int
    out: bool = True   # False = not out


def total_runs(innings: list[Innings]) -> int:
    return sum(i.runs for i in innings)


def dismissals(innings: list[Innings]) -> int:
    return sum(1 for i in innings if i.out)


def batting_average(innings: list[Innings]) -> float | None:
    """Runs per dismissal (cricket's batting average). None if the batter was never out."""
    outs = dismissals(innings)
    if outs == 0:
        return None
    return round(total_runs(innings) / outs, 2)


def strike_rate(innings: list[Innings]) -> float:
    """Runs per 100 balls faced."""
    balls = sum(i.balls for i in innings)
    if balls == 0:
        return 0.0
    return round(total_runs(innings) * 100 / balls, 2)


def highest(innings: list[Innings]) -> str:
    """Best score, with a * when it was not out (e.g. '30*')."""
    if not innings:
        return "-"
    best = max(innings, key=lambda i: (i.runs, not i.out))
    return f"{best.runs}{'' if best.out else '*'}"
