import datetime


def sprint_is_active(sprint):
    format = "%Y-%m-%d"
    return (
        0
        < (
            datetime.datetime.utcnow()
            - datetime.datetime.strptime(sprint["startDate"], format)
        ).days
        < sprint["duration"]
    )
