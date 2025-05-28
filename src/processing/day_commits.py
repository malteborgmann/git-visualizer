from datetime import datetime, timedelta

from src.core.models import Repository


def compute_day_commit_stats(repo:Repository) -> None:
    """
    Compute the number of commits per day for each branch in the repository.

    For each branch in the repository, this function counts how many commits were made on each day.
    It fills in any missing days between the first and last commit with a count of 0 to ensure
    continuity in time series data (e.g., for plotting). The result is stored in the `day_commits`
    attribute of each Branch object.

    The dates are formatted as strings in the format "DD/MM/YYYY" for consistency and sorting.

    Args:
        repo (Repository): The repository object containing branches and their commits.

    Returns:
        None: Updates are done in-place on each branch's `day_commits` dictionary.

    """
    fmt = "%d/%m/%Y"
    for branch in repo.branches.values():
        day_counts = {}
        for commit in branch.commits.values():
            day = commit.date.date().strftime(fmt)
            day_counts[day] = day_counts.get(day, 0) + 1

        # Fill in missing days
        first = datetime.strptime(min(day_counts), fmt)
        last = datetime.strptime(max(day_counts), fmt)
        current = first
        while current <= last:
            day = current.strftime(fmt)
            day_counts.setdefault(day, 0)
            current += timedelta(days=1)

        branch.day_commits = dict(
            sorted(day_counts.items(), key=lambda x: datetime.strptime(x[0], fmt)),
        )
