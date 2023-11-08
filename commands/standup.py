from cli import cli
import db

from group_by import group_by
from login_to_name import login_to_name
from opt import opt
from print_items import print_items
from sprint_is_active import sprint_is_active


@cli.command()
def standup():
    items = db.retrieve()["project_items"]["items"]
    items = [
        item for item in items if "sprint" in item and sprint_is_active(item["sprint"])
    ]
    items_by_assignee = group_by(
        items,
        opt(
            "assignees",
            lambda x: map(login_to_name, x),
            tuple,
            sorted,
            lambda x: ", ".join(x),
            default=tuple(),
        ),
    )
    print_items(
        sorted(items_by_assignee.items()),
        opt("milestone", "title", default="No milestone"),
        include_assignees=False,
    )
