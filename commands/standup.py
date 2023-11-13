from cli import cli
import db

from utils.group_by import group_by
from utils.login_to_name import login_to_name
from utils.opt import opt
from utils.print_items import print_items
from utils.sprint_is_active import sprint_is_active


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
            default="z_None"
        ),
    )
    print_items(
        sorted(items_by_assignee.items()),
        opt("milestone", "title", default="No milestone"),
        include_assignees=False,
    )
