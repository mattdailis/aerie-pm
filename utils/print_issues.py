from tabulate import tabulate

from utils.group_by import group_by
from utils.make_table import make_table

from utils.opt import opt


def print_issues(issues, show_state=True):
    for milestone, issues in sorted(
        group_by(issues, opt("milestone", "title", default="z_None")).items()
    ):
        columns = [
            "repo",
            "number",
            "title",
            lambda issue: ",".join(label["name"] for label in issue["labels"])
            if "labels" in issue
            else "",
        ]
        if show_state:
            columns.append("state")
        print(
            f"### {milestone}:\n"
            + tabulate(
                make_table(columns, issues, sort_by=opt("updatedAt", default="3000"))
            )
        )
