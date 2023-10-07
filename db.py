import json

db_location = "/Users/dailis/.pm/pm.json"


def retrieve():
    with open(db_location, "r") as f:
        return json.load(f)


def store(contents):
    with open(db_location, "w") as f:
        json.dump(contents, f)
