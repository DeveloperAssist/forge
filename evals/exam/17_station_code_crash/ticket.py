"""Text card for a train ticket."""
from stations import station_name


def route_line(src, dst):
    return f"{station_name(src).upper()} -> {station_name(dst).upper()}"


def ticket_card(pnr, src, dst, journey_date):
    return f"PNR {pnr}\n{route_line(src, dst)}\nDate: {journey_date}"
