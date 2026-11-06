"""Ball-by-ball scorer for a gully cricket match."""

EXTRAS = ("wd", "nb")


def runs_off(ball: str) -> int:
    """Runs that one delivery adds to the total (wide/no-ball = 1 + runs off it)."""
    ball = ball.strip()
    if ball == "W":
        return 0
    if ball.startswith(EXTRAS):
        extra_runs = int(ball.split("+")[1]) if "+" in ball else 0
        return 1 + extra_runs
    return int(ball)


def is_legal(ball: str) -> bool:
    return not ball.strip().startswith(EXTRAS)


def legal_balls(balls: list[str]) -> int:
    return sum(1 for b in balls if is_legal(b))


def overs_text(balls: list[str]) -> str:
    """Overs bowled as cricket writes them: 13 legal balls -> '2.1'."""
    n = legal_balls(balls)
    return f"{n // 6}.{n % 6}"


def total(balls: list[str]) -> int:
    return sum(runs_off(b) for b in balls)


def wickets(balls: list[str]) -> int:
    return sum(1 for b in balls if b.strip() == "W")


def run_rate(balls: list[str]) -> float:
    """Runs per over (6 legal balls), rounded to 2 decimals; 0.0 before any legal ball."""
    n = legal_balls(balls)
    if n == 0:
        return 0.0
    return round(total(balls) * 6 / n, 2)


def scoreline(balls: list[str]) -> str:
    return f"{total(balls)}/{wickets(balls)} in {overs_text(balls)} ov"
