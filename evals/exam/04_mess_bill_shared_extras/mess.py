"""Hostel mess bills. Money in paise."""


class MessBill:
    def __init__(self, student, extras=[]):
        self.student = student
        self.extras = extras

    def add_extra(self, item, price_paise):
        self.extras.append((item, price_paise))

    def total(self, base_paise=350000):
        return base_paise + sum(p for _, p in self.extras)


def bills_for(students):
    return {s: MessBill(s) for s in students}
