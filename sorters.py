status_sort = {
    "In Review": 1,
    "In Progress": 2,
    "Todo": 3,
    "Blocked": 3,
    "Done": 4,
}


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