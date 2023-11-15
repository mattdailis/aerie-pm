import click

from cli import cli
import db
from utils.print_issues import print_issues


@cli.command()
@click.option("--open", is_flag=True, help="show only open PRs")
def prs(open):
    prs = db.retrieve()["prs"]

    if open:
        prs = [pr for pr in prs if pr["state"] == "OPEN"]

    print_issues(prs, show_state=True)
