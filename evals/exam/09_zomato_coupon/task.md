Add an optional `coupon` argument to order_total. 'FLAT100' takes ₹100 off when the food subtotal is ₹499 or more,
'SAVE20' takes 20% off the food subtotal (at most ₹120, rounded down to the paisa); codes are case-insensitive, an
unknown code or FLAT100 on a subtotal under ₹499 raises ValueError, and delivery/platform fees are never discounted.
