"""GSTIN helpers. A GSTIN has 15 characters; the first two digits are the state code
(07 Delhi, 09 Uttar Pradesh, 10 Bihar, 20 Jharkhand, 27 Maharashtra, 29 Karnataka)."""


def state_code(gstin: str) -> str:
    gstin = gstin.strip().upper()
    if len(gstin) != 15:
        raise ValueError(f"GSTIN must have 15 characters: {gstin!r}")
    return gstin[:1]


def same_state(a: str, b: str) -> bool:
    return state_code(a) == state_code(b)
