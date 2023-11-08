from tabulate import tabulate

from login_to_name import login_to_name
from make_table import make_table
from opt import opt
from sorters import get_label_sort, status_sort, milestone_sorter


def print_items(
    grouped, other_column, print=print, include_assignees=True, status_first=True
):
    for category, items in grouped:
        print()
        print(f"{category}:")
        columns = ["status"] if status_first else [lambda item: other_column(item)[:40]]
        columns.extend(
            [
                "title",
                lambda x: x["repository"].split("/")[-1]
                + " #"
                + str(x["content"]["number"]),
                opt("labels", lambda x: ",".join(x)),
            ]
        )
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
