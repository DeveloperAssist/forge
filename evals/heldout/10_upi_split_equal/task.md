can u add split_equal to splitter.py? its for splitting the hostel maggi/pizza bill before sending UPI requests.

split_equal(total_paise, names) -> dict {name: paise}
- all amounts are int paise. the shares must add up to exactly total_paise (no paisa lost)
- shares differ by at most 1 paisa; the leftover paise go to the people earliest in the names list
- dict keeps the same order as names
- raise ValueError if names is empty, has a duplicate name, or total_paise is negative. total 0 is fine (everyone 0)

eg split_equal(1000, ["A","B","C"]) -> {"A": 334, "B": 333, "C": 333}
