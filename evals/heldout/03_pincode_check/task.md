the delivery address form accepts PIN code 000000 which is obviously fake. indian PIN codes are exactly 6 digits and the
first digit is never 0 (it's 1-9). spaces around it are fine (we strip them), but no spaces inside.
also my senior said isdigit() lets weird unicode digits through, only plain 0-9 should count.
fix is_valid_pin in pincode.py, the other functions use it
