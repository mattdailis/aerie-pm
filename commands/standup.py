import datetime

import click

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
@click.option("--previous", is_flag=True, help="show previous sprint")
def standup(previous):
    """
    Show items in current sprint grouped by assignee(s)
    """

    sprints = []
    all_items = db.retrieve()["project_items"]["items"]
    for item in all_items:
        if "sprint" in item and not item["sprint"] in sprints:
            sprints.append(item["sprint"])

    sprint_to_display = None
    if not previous:
        for sprint in sprints:
            if sprint_is_active(sprint):
                sprint_to_display = sprint
                break
        if sprint_to_display is None:
            print("There is no active sprint")
            return
    else:
        sprint_to_display = max(filter(lambda sprint: 0 < (datetime.datetime.utcnow() - datetime.datetime.strptime(sprint["startDate"], "%Y-%m-%d")).days and not sprint_is_active(sprint), sprints), key=lambda sprint: sprint["startDate"])

    items = []
    for item in all_items:
        if "sprint" in item and item["sprint"] == sprint_to_display:
            items.append(item)

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
        sprint_to_display
    )

    print(sprint_to_display["title"])
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    print(
        f"{work_days_elapsed} work days spent{' (including today)' if not is_day_off(today) and not previous else ''}, {work_days_remaining} to go"
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
