import json
import subprocess

issue_columns = [
    "assignees",
    "author",
    "body",
    "closed",
    "closedAt",
    "comments",
    "createdAt",
    "id",
    "labels",
    "milestone",
    "number",
    # "projectCards",
    # "projectItems",
    "reactionGroups",
    "state",
    "title",
    "updatedAt",
    "url",
]

pr_columns = [
    # "additions",
    "assignees",
    "author",
    # "autoMergeRequest",
    # "baseRefName",
    "body",
    # "changedFiles",
    # "closed",
    # "closedAt",
    "comments",
    # "commits",
    "createdAt",
    # "deletions",
    # "files",
    # "headRefName",
    # "headRefOid",
    # "headRepository",
    # "headRepositoryOwner",
    # "id",
    # "isCrossRepository",
    "isDraft",
    "labels",
    # "latestReviews",
    # "maintainerCanModify",
    # "mergeCommit",
    # "mergeStateStatus",
    # "mergeable",
    # "mergedAt",
    # "mergedBy",
    "milestone",
    "number",
    # "potentialMergeCommit",
    # "projectCards",
    # "projectItems",
    # "reactionGroups",
    # "reviewDecision",
    # "reviewRequests",
    # "reviews",
    "state",
    # "statusCheckRollup",
    "title",
    "updatedAt",
    "url",
]


def get_issues(repo, updated_after=None):
    if updated_after is None:
        return json.loads(
            run(
                f"gh issue -R {repo} list --json {','.join(issue_columns)} --limit 100000 -s all"
            )
        )
    else:
        return json.loads(run(f'gh issue -R {repo} list --json {",".join(issue_columns)} --limit 100000 -s all --search "updated:>{updated_after}"'))


def get_project_items(org, project_id):
    return json.loads(
        run(
            f"gh project item-list --owner {org} {project_id} --limit 2000 --format=json"
        )
    )


def get_prs(repo, updated_after=None):
    if updated_after is None:
        return json.loads(
            run(
                f"gh pr -R {repo} list --json {','.join(pr_columns)} --limit 1500 -s all"
            )
        )
    else:
        return json.loads(run(f'gh pr -R {repo} list --json {",".join(pr_columns)} --limit 1500 -s all --search "updated:>{updated_after}"'))


def run(command_str):
    print(command_str)
    return subprocess.run([cmd.strip('"') for cmd in command_str.split()], stdout=subprocess.PIPE).stdout


if __name__ == "__main__":
    get_issues("NASA-AMMOS/aerie")
    get_issues("NASA-AMMOS/aerie-ui")
