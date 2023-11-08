import click

import gh
from cli import cli
import db
from print_issues import print_issues

from repos import repos

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