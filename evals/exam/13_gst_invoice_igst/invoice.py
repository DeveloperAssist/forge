"""Build a GST invoice."""
from gstin import same_state
from tax import split_tax


def make_invoice(seller_gstin: str, buyer_gstin: str, lines) -> dict:
    """lines: list of (description, amount_paise, rate_percent)."""
    intra = same_state(seller_gstin, buyer_gstin)
    rows = []
    totals = {"taxable": 0, "cgst": 0, "sgst": 0, "igst": 0}
    for desc, amount, rate in lines:
        tax = split_tax(amount, rate, intra)
        rows.append({"desc": desc, "amount": amount, "rate": rate, **tax})
        totals["taxable"] += amount
        for k in ("cgst", "sgst", "igst"):
            totals[k] += tax[k]
    totals["grand_total"] = totals["taxable"] + totals["cgst"] + totals["sgst"] + totals["igst"]
    return {"intra_state": intra, "rows": rows, "totals": totals}
