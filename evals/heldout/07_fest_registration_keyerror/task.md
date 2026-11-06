running the fest registration report on today's form export crashes:

```
Traceback (most recent call last):
  File "registrations.py", line 39, in <module>
    print(report(load("export.json")))
  File "registrations.py", line 32, in report
    lines = contact_list(rows)
  File "registrations.py", line 15, in contact_list
    out.append(f"{r['name']} ({r['college']}) - {r['phone']}")
                                                 ~^^^^^^^^^
KeyError: 'phone'
```

phone and team are both optional on the google form now, so some entries just don't have them (or have them as "").
no phone -> show "-" in the contact list. no team -> they're solo, count each solo person as their own team.
report() should work on the whole export. dont drop anyone.
