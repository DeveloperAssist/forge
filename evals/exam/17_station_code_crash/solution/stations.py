"""Station codes used on our PNR card."""

STATIONS = {
    "NDLS": "New Delhi",
    "HWH": "Howrah",
    "BCT": "Mumbai Central",
    "SBC": "Bengaluru",
    "RNC": "Ranchi",
    "PNBE": "Patna",
}


def station_name(code):
    key = code.strip().upper()
    if key not in STATIONS:
        raise ValueError(f"unknown station code: {key}")
    return STATIONS[key]
