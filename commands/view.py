import datetime

import click
from pytz import timezone
from rich.markdown import Markdown

from cli import cli
import db
from login_to_name import login_to_name
from print_issues import print_issues

from console import _console


@cli.command()
@click.argument("issue_number")
@click.option(
    "-u", "--ui", is_flag=True, help="specify that this issue should be from aerie-ui"
)
@click.option(
    "-a", "--aerie", is_flag=True, help="specify that this issue should be from aerie"
)
@click.option(
    "-d", "--docs", is_flag=True, help="specify that this issue should be from aerie-docs"
)
def view(issue_number, ui, aerie, docs):
    issues = db.retrieve()["issues"]
    prs = db.retrieve()["prs"]

    if issue_number.startswith("#"):
        issue_number = issue_number[1:]

    if ui:
        issues = [issue for issue in issues if issue["repo"] == "aerie-ui"]
        prs = [pr for pr in prs if pr["repo"] == "aerie-ui"]
    if aerie:
        issues = [issue for issue in issues if issue["repo"] == "aerie"]
        prs = [pr for pr in prs if pr["repo"] == "aerie"]
    if docs:
        issues = [issue for issue in issues if issue["repo"] == "aerie-docs"]
        prs = [pr for pr in prs if pr["repo"] == "aerie-docs"]
    issues = [issue for issue in issues if issue["number"] == int(issue_number)]
    prs = [pr for pr in prs if pr["number"] == int(issue_number)]
    issues += prs
    if not issues:
        raise Exception(f"Issue #{issue_number} not found")
    if len(issues) > 1:
        print(f"Multiple issues found with #{issue_number}:")
        print_issues(issues)
        return
    issue = issues[0]
    header = "\n".join(
        (
            f'## {issue["title"]}(#{issue["number"]}) [{issue["state"]}]',
            f'#### @{login_to_name(issue["author"]["login"])} on {utc_to_pdt(issue["createdAt"])}',
        )
    )

    console = _console
    with console.pager(styles=True):
        render_md(console, header + "\n\n" + issue["body"])

        for comment in issue["comments"]:
            render_md(console, "---")
            render_md(
                console,
                f'_@{login_to_name(comment["author"]["login"])} on {utc_to_pdt(comment["createdAt"])}_',
            )
            render_md(console, comment["body"])
        render_md(console, "---")

        console.print(issue["url"])


def render_md(console, md):
    console.print(Markdown(md, hyperlinks=False), width=90)


def utc_to_pdt(utc):
    # 2023-09-27T22:16:35Z
    format = "%Y-%m-%dT%H:%M:%SZ"
    datetime_utc = datetime.datetime.strptime(utc, format).replace(
        tzinfo=datetime.timezone.utc
    )
    days_ago = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime_utc
    ).days
    res = datetime_utc.astimezone(timezone("US/Pacific")).strftime(
        "%A, %Y-%m-%d at %I:%M %p"
    )
    if days_ago == 0:
        res = res + " (Today)"
    elif days_ago == 1:
        res = res + " (Yesterday)"
    else:
        res = res + f" ({days_ago} days ago)"
    return res