from pathlib import Path
import json

pm_directory = Path.home() / ".pm"
db_location = pm_directory / "pm.json"


empty_db = {
    "issues": [],
    "prs": [],
    "project_items": {
        "items": []
    }
}


def retrieve():
    ensure_pm_directory_exists()
    with open(db_location, "r") as f:
        return json.load(f)


def store(contents):
    ensure_pm_directory_exists()
    with open(db_location, "w") as f:
        json.dump(contents, f)


def ensure_pm_directory_exists():
    pm_directory.mkdir(parents=True, exist_ok=True)
    if not db_location.is_file():
        print("Creating empty database at" , db_location)
        with open(db_location, "w") as f:
            json.dump(empty_db, f)