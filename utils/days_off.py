import datetime

format = "%Y-%m-%d"


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, format)


reference_rdo = parse_date("2023-11-17")

holidays = [
    "2023-11-23",
    "2023-11-24",
    "2023-12-25",
    "2023-12-26",
    "2023-12-29",
    "2024-01-01",
    "2024-01-15",
    "2024-02-19",
]


def is_day_off(date_string):
    """
    Expects string formatted as %Y-%m-%d. E.g. "2023-11-23"
    """
    date = parse_date(date_string)
    return (
        date.weekday() in (5, 6)
        or date_string in holidays
        or (date - reference_rdo).days % 14 == 0
    )
