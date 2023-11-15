import click

from cli import cli
import db
from utils.print_issues import print_issues


@cli.command()
def prs():
    prs = db.retrieve()["prs"]
    print_issues(prs, show_state=True)
