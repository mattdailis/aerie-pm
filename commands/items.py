import click

from cli import cli
import db
from utils.group_by import group_by
from utils.opt import opt
from utils.sorters import milestone_sorter
from utils.print_items import print_items
from utils.sprint_end_date import sprint_end_date


@cli.command()
@click.option("--by-milestone", is_flag=True, help="group items by milestone")
@click.option("--by-sprint", is_flag=True, help="group items by sprint")
@click.option("--show-done", is_flag=True, help="include Done items in output")
def items(by_milestone, by_sprint, show_done):
    items = db.retrieve()["project_items"]["items"]
    issues = db.retrieve()["issues"]

    # Issues are easier to keep in sync - prefer the issue's milestone if available
    issue_dict = {(issue["repo"], issue["number"]): issue for issue in issues}

    for item in items:
        repo = item["repository"].split("/")[-1]
        number = item["content"]["number"]
        if (repo, number) in issue_dict:
            issue = issue_dict[(repo, number)]
            if "milestone" in issue:
                item["milestone"] = issue["milestone"]

    if not show_done:
        items = [item for item in items if item["status"] != "Done"]

    items = sorted(items, key=lambda item: (item["status"], item["content"]["number"]))

    if by_milestone:
        grouped = sorted(
            group_by(items, opt("milestone", "title", default="No milestone")).items(),
            key=lambda x: milestone_sorter(x[0]),
        )
        other_column = opt("sprint", "title", default="No sprint")
    else:
        grouped = sorted(
            group_by(
                items,
                opt(
                    "sprint",
                    lambda x: f"{sprint_end_date(x)} {x['title']}",
                    default="No Sprint",
                ),
            ).items()
        )
        other_column = opt("milestone", "title", default="No milestone")

    print_items(grouped, other_column)
