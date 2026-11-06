Our UPI statement importer now gets amounts like '₹1,24,999.50', 'Rs. 499', 'INR 75.5' and '-₹249' from the new
bank export. Make parse_amount accept these too, and make sure every amount converts to the exact number of paise.
