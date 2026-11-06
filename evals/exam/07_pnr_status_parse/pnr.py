"""Parse the booking status text from IRCTC SMS / PNR enquiry."""


def parse_status(text: str) -> dict:
    """Return {"status": "CNF" | "RAC" | "WL", "coach": str | None, "seat": int | None,
    "berth": str | None, "position": int | None}.

    Examples: "CNF/B2/45" -> confirmed in coach B2, seat 45
              "RAC 23"    -> RAC position 23
              "WL 12"     -> waiting list position 12
    """
    text = text.strip()
    if text.startswith("CNF"):
        _, coach, seat = text.split("/")
        return {"status": "CNF", "coach": coach, "seat": int(seat), "berth": None, "position": None}
    if text.startswith("RAC"):
        return {"status": "RAC", "coach": None, "seat": None, "berth": None, "position": int(text[3:])}
    if text.startswith("WL"):
        return {"status": "WL", "coach": None, "seat": None, "berth": None, "position": int(text[2:])}
    raise ValueError(f"unknown status: {text!r}")


def is_confirmed(text: str) -> bool:
    return parse_status(text)["status"] == "CNF"
