import datetime

from cli import cli
import db
from utils.days_off import is_day_off

from utils.group_by import group_by
from utils.login_to_name import login_to_name
from utils.opt import opt
from utils.print_items import print_items
from utils.sprint_end_date import sprint_end_date
from utils.sprint_is_active import sprint_is_active

active_team_members = [
    "lklyne",
    "adrienmaillard",
    "skovati",
    "cohansen",
    "mattdailis",
    "goetzrrGit",
    "JoelCourtney",
    "Mythicaeda",
    "jmdelfa",
    "duranb",
    "AaronPlave",
    "jeffpamer",
]


@cli.command()
def standup():
    """
    Show items in current sprint grouped by assignee(s)
    """
    items = []
    active_sprint = None
    for item in db.retrieve()["project_items"]["items"]:
        if "sprint" in item and sprint_is_active(item["sprint"]):
            items.append(item)
            active_sprint = item["sprint"]

    items_by_assignee = group_by(
        items,
        opt(
            "assignees",
            lambda x: map(login_to_name, x),
            tuple,
            sorted,
            lambda x: ", ".join(x),
            default="z_None",
        ),
    )

    work_days_elapsed, work_days_remaining = get_sprint_work_days_breakdown(
        active_sprint
    )

    print(active_sprint["title"])
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    print(
        f"{work_days_elapsed} work days spent{' (including today)' if not is_day_off(today) else ''}, {work_days_remaining} to go"
    )

    print_items(
        sorted(items_by_assignee.items()),
        opt("milestone", "title", default="No milestone"),
        include_assignees=False,
    )

    not_on_the_board = set(active_team_members)
    for item in items:
        for assignee in opt("assignees", default=[])(item):
            if assignee in not_on_the_board:
                not_on_the_board.remove(assignee)

    if not_on_the_board:
        print()
        print("Not on the board:")
        for name in sorted(login_to_name(login) for login in not_on_the_board):
            print(f"- {name}")


def get_sprint_work_days_breakdown(active_sprint):
    date = active_sprint["startDate"]
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    end_date = sprint_end_date(active_sprint)
    work_days_elapsed = 0
    work_days_remaining = 0
    while date <= today:
        if not is_day_off(date):
            work_days_elapsed += 1
        date = datetime.datetime.strftime(
            datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1),
            "%Y-%m-%d",
        )
    while date < end_date:
        if not is_day_off(date):
            work_days_remaining += 1
        date = datetime.datetime.strftime(
            datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1),
            "%Y-%m-%d",
        )
    return work_days_elapsed, work_days_remaining
