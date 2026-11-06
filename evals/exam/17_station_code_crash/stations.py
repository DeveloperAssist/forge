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
    return STATIONS.get(code)
