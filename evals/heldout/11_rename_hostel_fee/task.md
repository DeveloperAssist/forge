small cleanup in the hostel fee project: the function `calc` in fees.py is a terrible name. rename it to `hostel_fee`
and rename its parameter `n` to `months` (the warden's script calls it with keywords now, like hostel_fee("double", months=6)).
update every place that uses it (receipt.py, defaulters.py, my test file). dont leave the old name `calc` behind as an alias,
i want it gone. fees must come out exactly the same as before.
