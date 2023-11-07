import datetime
from pytz import timezone

import click
from tabulate import tabulate
from rich.console import Console
from rich.markdown import Markdown

import db
import gh

_console = Console()

repos = ["aerie", "aerie-ui", "aerie-docs"]

# PROJECT_ID = "PVT_kwDOAkGRE84ACh6K"


def tag(name, *contents):
    res = f"<{name}>"
    for content in contents:
        res += str(content)
    res += f"</{name}>"
    return res


@click.group()
def cli():
    pass


@cli.command()
@click.option("--items", is_flag=True, help="also fetch items. This may take a little while")
def fetch(items):
    fetch_items = items
    try:
        issues = db.retrieve()["issues"]
        prs = db.retrieve()["prs"]
    except:
        issues = []
        prs = []

    new_issues = []
    new_prs = []
    for repo in repos:
        cached_issue_update_times = [issue["updatedAt"] for issue in issues if issue["repo"] == repo]
        if cached_issue_update_times:
            last_updated = max(cached_issue_update_times)
        else:
            last_updated = None
        print(f"Fetching issues from {repo}")
        for issue in gh.get_issues(f"NASA-AMMOS/{repo}", updated_after=last_updated):
            issue["repo"] = repo
            new_issues.append(issue)

        print(f"Fetching PRs from {repo}")
        for pr in gh.get_prs(f"NASA-AMMOS/{repo}", updated_after=last_updated):
            pr["repo"] = repo
            new_prs.append(pr)

    updated_issues = {(issue["repo"], issue["number"]) for issue in new_issues}
    issues = [issue for issue in issues if (issue["repo"], issue["number"]) not in updated_issues]

    print(f"Updated issues ({len(new_issues)}):")
    print_issues(new_issues)
    issues.extend(new_issues)

    updated_prs = {(pr["repo"], pr["number"]) for pr in new_prs}
    prs = [pr for pr in prs if (pr["repo"], pr["number"]) not in updated_prs]

    print(f"Updated PRs ({len(new_prs)}):")
    print_issues(new_prs)
    prs.extend(new_prs)

    if fetch_items:
        print("Fetching project items")
        project_items = gh.get_project_items("NASA-AMMOS", 2)
    else:
        print("Using cached items only")
        project_items = db.retrieve()["project_items"]

    db.store({"issues": issues, "project_items": project_items, "prs": prs})


@cli.command()
@click.option("--show-closed", is_flag=True, help="include closed issues in output")
@click.option(
    "--not-in-project", is_flag=True, help="show only issues that are not in a project"
)
def issues(show_closed, not_in_project):
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


def print_issues(issues, show_state=True):
    for milestone, issues in sorted(
        group_by(issues, opt("milestone", "title", default="z_None")).items()
    ):
        columns = [
            "repo",
            "number",
            "title",
            lambda issue: ",".join(label["name"] for label in issue["labels"]) if "labels" in issue else "",
        ]
        if show_state:
            columns.append("state")
        print(
            f"### {milestone}:\n"
            + tabulate(make_table(columns, issues, sort_by=opt("updatedAt", default="3000")))
        )


def opt(*keys, default=None):
    def _(obj):
        res = obj
        for key in keys:
            if type(key) == str:
                func = lambda x: x[key]
            else:
                func = key
            try:
                res = func(res)
            except (KeyError, TypeError):
                return default
        return res

    return _


def group_by(elements, key):
    res = {}
    for element in elements:
        value = key(element)
        if value not in res:
            res[value] = []
        res[value].append(element)
    return res


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


@cli.command()
@click.option("--by-milestone", is_flag=True, help="group items by milestone")
@click.option("--by-sprint", is_flag=True, help="group items by sprint")
@click.option("--show-done", is_flag=True, help="include Done items in output")
def items(by_milestone, by_sprint, show_done):
    items = db.retrieve()["project_items"]["items"]
    issues = db.retrieve()["issues"]

    # Issues are easier to keep in sync - prefer the issue's milestone if available
    issue_dict = {
        (issue["repo"], issue["number"]): issue
        for issue in issues
    }

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
            key=lambda x: milestone_sorter(x[0])
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


def milestone_sorter(title):
    res = title.split(" - ")
    if len(res) > 1 and "Ad Hoc" in res[1]:
        res[1] = "z_" + res[1]
    return " - ".join(res)


def get_label_sort(item):
    if "labels" not in item:
        return 0
    labels = item["labels"]
    if "bug" in labels:
        return -2
    if "fix" in labels:
        return 0
    if "icebox" in labels:
        return 1
    return 0


def print_items(grouped, other_column, print=print, include_assignees=True, status_first=True):
    for category, items in grouped:
        print()
        print(f"{category}:")
        columns = ["status"] if status_first else [lambda item: other_column(item)[:40]]
        columns.extend([
            "title",
            lambda x: x["repository"].split("/")[-1]
                      + " #"
                      + str(x["content"]["number"]),
            opt("labels", lambda x: ",".join(x))
        ])
        if status_first and include_assignees:
            columns.append(opt("assignees", lambda x: ", ".join(map(login_to_name, x))))

        if status_first:
            columns.append(other_column)

        if not status_first and include_assignees:
            columns.append(opt("assignees", lambda x: ", ".join(map(login_to_name, x))))

        if not status_first:
            columns.append("status")

        def sort_by(item):
            res = (
                status_sort[item["status"]],
                get_label_sort(item),
                milestone_sorter(other_column(item)),
                -len(item["assignees"]) if "assignees" in item else 0,
                -item["content"]["number"],
            )
            return res

        print(
            tabulate(
                make_table(
                    columns,
                    items,
                    sort_by=sort_by,
                )
            )
        )


@cli.command()
def standup():
    items = db.retrieve()["project_items"]["items"]
    items = [item for item in items if "sprint" in item and sprint_is_active(item["sprint"])]
    items_by_assignee = group_by(items, opt("assignees", lambda x: map(login_to_name, x), tuple, sorted, lambda x: ", ".join(x), default=tuple()))
    print_items(sorted(items_by_assignee.items()), opt("milestone", "title", default="No milestone"), include_assignees=False)


@cli.command()
@click.option("--by-assignee", is_flag=True, help="group items by assignee")
@click.option("--clipper", is_flag=True, help="show only clipper items")
@click.option("--bugs", is_flag=True, help="show only bugs")
def backlog(by_assignee, clipper, bugs):
    items = db.retrieve()["project_items"]["items"]
    items = [item for item in items if not ("sprint" in item and sprint_is_active(item["sprint"])) and not item["status"] == "Done"]
    if clipper:
        items = [item for item in items if "labels" in item and "clipper" in item["labels"]]
    if bugs:
        items = [item for item in items if "labels" in item and "bug" in item["labels"]]
    if by_assignee:
        grouped = sorted(group_by(items, opt("assignees", lambda x: map(login_to_name, x), tuple, sorted,
                                                lambda x: ", ".join(x), default="Unassigned")).items())
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
    print_items(grouped, opt("milestone", "title", default="No milestone"), status_first=False)

@cli.command()
def csv():
    items = db.retrieve()["project_items"]["items"]
    columns = [
        lambda item: opt("milestone", "title", default="No milestone")(item),
        opt("title"),
        lambda x: x["repository"].split("/")[-1]
                  + " #"
                  + str(x["content"]["number"]),
        opt("labels", lambda x: ",".join(x), default=""),
        opt("status")
    ]
    import csv
    with open("pm.csv", "w") as f:
        writer = csv.writer(f)
        for item in items:
            writer.writerow(column(item) for column in columns)


status_sort = {
    "In Review": 1,
    "In Progress": 2,
    "Todo": 3,
    "Blocked": 3,
    "Done": 4,
}


def make_table(columns, items, sort_by=None):
    if type(sort_by) == str:
        key = lambda x: x[sort_by]
    else:
        key = sort_by
    table = []
    if key is not None:
        items = sorted(items, key=lambda x: key(x))
    for issue in items:
        row = []
        for col in columns:
            if type(col) == str:
                row.append(issue[col])
            else:
                row.append(col(issue))
        table.append(row)
    return table


def sprint_is_active(sprint):
    format = "%Y-%m-%d"
    return 0 < (datetime.datetime.utcnow() - datetime.datetime.strptime(sprint["startDate"], format)).days < sprint["duration"]


def sprint_end_date(sprint):
    format = "%Y-%m-%d"
    end_date = datetime.datetime.strptime(
        sprint["startDate"], format
    ) + datetime.timedelta(days=sprint["duration"])
    return end_date.strftime(format)


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


def login_to_name(login):
    logins = {
        "lklyne": "Lyle Klyne",
        "camargo": "Chris Camargo",
        "parkerabercrombie": "Parker Abercrombie",
        "bashbash": "Basak Ramaswamy",
        "adrienmaillard": "Adrien Maillard",
        "skovati": "Luke Jurgella",
        "twisol": "Jonathan Castello",
        "biqua": "Emily Winner",
        "ewferg": "Eric Ferguson",
        "bradNASA": "Brad Clement",
        "cohansen": "Cody Hansen",
        "mattdailis": "Matt Dailis",
        "goetzrrGit": "Ryan Goetz",
        "JoelCourtney": "Joel Courtney",
        "Mythicaeda": "Theresa Kamerman",
        "jmdelfa": "Juan Delfa",
        "duranb": "Bryan Duran",
        "AaronPlave": "Aaron Plave",
        "joswig": "Chet Joswig",
        "cartermak": "Carter Mak",
        "jeffpamer": "Jeff Pamer",
        "sschaffe": "Steve Schaffer"
    }
    if login in logins:
        return logins[login]
    else:
        return login


if __name__ == "__main__":
    cli()
