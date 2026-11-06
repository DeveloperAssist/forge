"""Token board for the hostel canteen counter (sample orders only)."""
from dataclasses import dataclass


@dataclass
class Order:
    token: int
    item: str
    placed_min: int          # minutes since the counter opened
    ready_min: int | None    # None while still being cooked


def pending(orders: list[Order]) -> list[Order]:
    return sorted((o for o in orders if o.ready_min is None), key=lambda o: o.token)


def now_serving(orders: list[Order]) -> int | None:
    """Smallest token that is still waiting, or None when nothing is waiting."""
    waiting = pending(orders)
    return waiting[0].token if waiting else None


def avg_wait(orders: list[Order]) -> float:
    """Average minutes from placing to ready, over orders that are ready (0.0 if none)."""
    done = [o for o in orders if o.ready_min is not None]
    if not done:
        return 0.0
    return round(sum(o.ready_min - o.placed_min for o in done) / len(done), 1)


def board_text(orders: list[Order]) -> str:
    token = now_serving(orders)
    serving = "-" if token is None else str(token)
    return "\n".join([
        f"Now serving: {serving}",
        f"Waiting: {len(pending(orders))}",
        f"Avg wait: {avg_wait(orders)} min",
    ])


if __name__ == "__main__":
    print(board_text([]))
