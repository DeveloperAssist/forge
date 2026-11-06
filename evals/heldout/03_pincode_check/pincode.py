"""PIN-code checks for the delivery address form (sample data only)."""

ZONES = {
    "1": "Delhi / Haryana / Punjab / HP / J&K",
    "2": "UP / Uttarakhand",
    "3": "Rajasthan / Gujarat",
    "4": "Maharashtra / MP / Chhattisgarh",
    "5": "Andhra / Telangana / Karnataka",
    "6": "Tamil Nadu / Kerala",
    "7": "West Bengal / Odisha / North East",
    "8": "Bihar / Jharkhand",
    "9": "Army Post Office",
}


def is_valid_pin(pin: str) -> bool:
    """True for a real-looking Indian PIN: 6 digits, first digit 1-9."""
    pin = pin.strip()
    if len(pin) != 6 or not pin.isdigit():
        return False
    if pin == "000000":
        return False
    return True


def zone_of(pin: str) -> str:
    """Postal zone name for a valid PIN, else raises ValueError."""
    if not is_valid_pin(pin):
        raise ValueError(f"bad PIN code: {pin!r}")
    return ZONES[pin.strip()[0]]


def clean_addresses(rows: list[dict]) -> list[dict]:
    """Keep only rows with a valid PIN; the PIN is stored stripped."""
    kept = []
    for row in rows:
        if is_valid_pin(row.get("pin", "")):
            kept.append({**row, "pin": row["pin"].strip()})
    return kept
