import click

from cli import cli
import db
from utils.group_by import group_by
from utils.login_to_name import login_to_name
from utils.print_items import print_items
from utils.sprint_end_date import sprint_end_date
from utils.sprint_is_active import sprint_is_active
from utils.opt import opt


@cli.command()
@click.option("--by-assignee", is_flag=True, help="group items by assignee")
@click.option("--clipper", is_flag=True, help="show only clipper items")
@click.option("--bugs", is_flag=True, help="show only bugs")
def backlog(by_assignee, clipper, bugs):
    items = db.retrieve()["project_items"]["items"]
    items = [
        item
        for item in items
        if not ("sprint" in item and sprint_is_active(item["sprint"]))
        and not item["status"] == "Done"
    ]
    if clipper:
        items = [
            item for item in items if "labels" in item and "clipper" in item["labels"]
        ]
    if bugs:
        items = [item for item in items if "labels" in item and "bug" in item["labels"]]
    if by_assignee:
        grouped = sorted(
            group_by(
                items,
                opt(
                    "assignees",
                    lambda x: map(login_to_name, x),
                    tuple,
                    sorted,
                    lambda x: ", ".join(x),
                    default="Unassigned",
                ),
            ).items()
        )
    else:
        grouped = sorted(
            group_by(
                items,
                opt(
                    "sprint",
                    lambda x: f"{sprint_end_date(x)} {x['title']}",
                    default="Backlog",
                ),
            ).items()
        )
    print_items(
        grouped, opt("milestone", "title", default="No milestone"), status_first=False
    )
