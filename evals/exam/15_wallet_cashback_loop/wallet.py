"""A tiny UPI wallet. Money in paise."""
import rewards


class Wallet:
    def __init__(self, owner: str, balance_paise: int = 0):
        self.owner = owner
        self.balance = balance_paise
        self.history = []  # list of (kind, paise)

    def _record(self, kind: str, paise: int) -> None:
        self.history.append((kind, paise))
        rewards.on_transaction(self, kind, paise)

    def pay(self, paise: int) -> None:
        if paise > self.balance:
            raise ValueError("insufficient balance")
        self.balance -= paise
        self._record("pay", paise)

    def receive(self, paise: int) -> None:
        self.balance += paise
        self._record("receive", paise)

    def credit_cashback(self, paise: int) -> None:
        self.balance += paise
        self._record("cashback", paise)

    def cashback_earned(self) -> int:
        return sum(p for kind, p in self.history if kind == "cashback")
