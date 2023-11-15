import click

from cli import cli
import db
from utils.print_issues import print_issues


@cli.command()
@click.option("--show-closed", is_flag=True, help="include closed issues in output")
@click.option(
    "--not-in-project", is_flag=True, help="show only issues that are not in a project. Useful for triaging new issues"
)
def issues(show_closed, not_in_project):
    """
    List issues in Aerie repos
    """
    issues = db.retrieve()["issues"]

    if not show_closed:
        issues = [issue for issue in issues if issue["state"] != "CLOSED"]

    if not_in_project:
        project_items = db.retrieve()["project_items"]["items"]

        issues_in_project = set()

        for item in project_items:
            repo = item["repository"].split("/")[-1]
            number = item["content"]["number"]
            issues_in_project.add((repo, number))

        issues = [
            issue
            for issue in issues
            if (issue["repo"], issue["number"]) not in issues_in_project
        ]

    print_issues(issues, show_state=show_closed)
