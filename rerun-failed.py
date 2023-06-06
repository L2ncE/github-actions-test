import os

import requests
from github import Github

DEFAULT_WORKFLOW = "CI"


def rerun_last_failed_jobs(pr_url: str, workflow: str = DEFAULT_WORKFLOW) -> None:
    gh = Github(os.getenv("GITHUB_TOKEN"))
    repo_url, _, pr_number = pr_url.partition("/pull/")
    print("Repo URL:", repo_url)
    repo = gh.get_repo("/".join(repo_url.rsplit("/")[-2:]))
    pr = repo.get_pull(int(pr_number))
    workflow_ins = next((w for w in repo.get_workflows() if w.name == workflow), None)
    if workflow_ins is None:
        raise ValueError(f"Non exist workflow: {workflow}")
    run = next(
        (
            r
            for r in workflow_ins.get_runs(branch=pr.head.ref)
            if r.head_sha == pr.head.sha
        ),
        None,
    )

    if run is None:
        raise RuntimeError(f"No run for the workflow {workflow}")
    print(
        f"Workflow: {workflow}\n"
        f"Workflow ID: {workflow_ins.id}\n"
        f"Run URL: {run.html_url}\n"
        f"Run status: {run.status}\n"
        f"Run conclusion: {run.conclusion}\n"
    )
    if run.status != "completed" or run.conclusion not in ("failure", "cancelled"):
        raise ValueError("The run status doesn't meet the requirement to rerun")
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
        'X-GitHub-Api-Version': '2022-11-28',
    }
    res = requests.post(f"https://api.github.com/repos/{repo}/actions/runs/{run.id}/rerun-failed-jobs", headers=headers)
    print(res.json())
    print("Rerun success" if res.status_code == 201 else "Rerun failed")
    if res.status_code != 201:
        sys.exit(1)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <pr_url> [<workflow>]")
        sys.exit(1)

    pr_url = sys.argv[1]
    workflow = DEFAULT_WORKFLOW
    if len(sys.argv) > 2:
        workflow = sys.argv[2]

    rerun_last_failed_jobs(pr_url, workflow)
