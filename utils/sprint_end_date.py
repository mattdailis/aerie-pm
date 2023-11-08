import datetime


def sprint_end_date(sprint):
    format = "%Y-%m-%d"
    end_date = datetime.datetime.strptime(
        sprint["startDate"], format
    ) + datetime.timedelta(days=sprint["duration"])
    return end_date.strftime(format)
