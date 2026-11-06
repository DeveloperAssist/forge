When I run `python report.py` I get this and no summary. Fix it.

```
Traceback (most recent call last):
  File "report.py", line 15, in <module>
    main()
  File "report.py", line 9, in main
    print(f"Total: ₹{total_spent(orders) / 100:,.2f}")
                     ~~~~~~~~~~~^^^^^^^^
  File "orders.py", line 15, in total_spent
    return sum(order_amount(o) for o in orders)
  File "orders.py", line 15, in <genexpr>
    return sum(order_amount(o) for o in orders)
               ~~~~~~~~~~~~^^^
  File "orders.py", line 11, in order_amount
    return order["price_paise"] * order["qty"]
           ~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~
TypeError: can't multiply sequence by non-int of type 'str'
```
