Users type station codes in lowercase or with spaces and the ticket card crashes (traceback below). Codes should
work in any case and with extra spaces, and a code we really don't know should raise a ValueError that names the
code instead of this crash.

```
>>> from ticket import ticket_card
>>> ticket_card("4521873690", "rnc", "NDLS", "12-01-2027")
Traceback (most recent call last):
  File "<python-input-1>", line 1, in <module>
    ticket_card("4521873690", "rnc", "NDLS", "12-01-2027")
  File "ticket.py", line 10, in ticket_card
    return f"PNR {pnr}\n{route_line(src, dst)}\nDate: {journey_date}"
  File "ticket.py", line 6, in route_line
    return f"{station_name(src).upper()} -> {station_name(dst).upper()}"
AttributeError: 'NoneType' object has no attribute 'upper'
```
