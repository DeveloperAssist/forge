canteen token board crashes when the counter opens in the morning (no orders yet):

```
$ python canteen.py
Traceback (most recent call last):
  File "canteen.py", line 39, in <module>
    print(board_text([]))
  File "canteen.py", line 29, in board_text
    token = now_serving(orders)
  File "canteen.py", line 19, in now_serving
    return pending(orders)[0].token
           ~~~~~~~~~~~~~~~^^^
IndexError: list index out of range
```

same thing when every order is already ready. the docstrings say what it should do: now_serving gives None when nothing is waiting
(board shows "Now serving: -"), avg_wait is 0.0 when no order is ready yet. board should never crash.
