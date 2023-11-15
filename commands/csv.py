from cli import cli
import db
from utils.opt import opt


@cli.command()
def csv():
    """
    Write items to a csv file called pm.csv in the current directory
    """
    items = db.retrieve()["project_items"]["items"]
    columns = [
        lambda item: opt("milestone", "title", default="No milestone")(item),
        opt("title"),
        lambda x: x["repository"].split("/")[-1] + " #" + str(x["content"]["number"]),
        opt("labels", lambda x: ",".join(x), default=""),
        opt("status"),
    ]
    import csv

    with open("pm.csv", "w") as f:
        writer = csv.writer(f)
        for item in items:
            writer.writerow(column(item) for column in columns)
