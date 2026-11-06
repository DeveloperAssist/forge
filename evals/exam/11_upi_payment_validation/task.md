create_payment accepts junk like 'rahul.okaxis' or a ₹0 amount. Make it raise ValueError for a UPI ID that isn't
name@bank (exactly one @, neither side empty, no spaces), for a zero or negative amount, and for an amount above the
₹1 lakh UPI limit.
