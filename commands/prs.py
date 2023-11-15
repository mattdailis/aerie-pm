import click
from tabulate import tabulate

from cli import cli
import db
from utils.group_by import group_by
from utils.make_table import make_table
from utils.opt import opt


@cli.command()
@click.option("--open", is_flag=True, help="show only open PRs")
@click.option("--merged", is_flag=True, help="show only open PRs")
def prs(open, merged):
    if open and merged:
        print("Pick one: --open, or --merged")
        return

    prs = db.retrieve()["prs"]

    if open:
        prs = [pr for pr in prs if pr["state"] == "OPEN"]

    if merged:
        prs = [pr for pr in prs if pr["state"] == "MERGED"]

    for milestone, issues in sorted(
        group_by(prs, opt("milestone", "title", default="z_None")).items()
    ):
        columns = [
            "repo",
            "number",
            "title",
            lambda issue: ",".join(label["name"] for label in issue["labels"])
            if "labels" in issue
            else "",
            "state",
        ]
        print(
            f"### {milestone}:\n"
            + tabulate(
                make_table(columns, issues, sort_by=opt("updatedAt", default="3000"))
            )
        )
        """
        What else do I want to know about PRs?

        - Is this closing an issue, or is it ad-hoc?
        - Is it stale?
        """