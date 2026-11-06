"""Parse the booking status text from IRCTC SMS / PNR enquiry."""
import re

_WL = re.compile(r"^[A-Z]*WL[\s/]*(\d+)$")
_RAC = re.compile(r"^RAC[\s/]*(\d+)$")


def parse_status(text: str) -> dict:
    """Return {"status": "CNF" | "RAC" | "WL", "coach": str | None, "seat": int | None,
    "berth": str | None, "position": int | None}.

    Examples: "CNF/B2/45" -> confirmed in coach B2, seat 45
              "RAC 23"    -> RAC position 23
              "WL 12"     -> waiting list position 12
    """
    text = text.strip().upper()
    if text.startswith("CNF/"):
        parts = text.split("/")
        if len(parts) not in (3, 4):
            raise ValueError(f"unknown status: {text!r}")
        berth = parts[3] if len(parts) == 4 else None
        return {"status": "CNF", "coach": parts[1], "seat": int(parts[2]), "berth": berth, "position": None}
    m = _RAC.match(text)
    if m:
        return {"status": "RAC", "coach": None, "seat": None, "berth": None, "position": int(m.group(1))}
    m = _WL.match(text)
    if m:
        return {"status": "WL", "coach": None, "seat": None, "berth": None, "position": int(m.group(1))}
    raise ValueError(f"unknown status: {text!r}")


def is_confirmed(text: str) -> bool:
    return parse_status(text)["status"] == "CNF"
