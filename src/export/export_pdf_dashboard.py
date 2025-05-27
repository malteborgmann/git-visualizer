"""
Export dashboard module.

Generate visual analytics from a Git branch and export them as a PDF report.
"""

from datetime import datetime, timedelta

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.core.models import Branch


def create_dashboard_pdf(branch: Branch, filepath: str) -> None:
    """
    Generate visual analytics from a Git branch and export them into a single PDF file.

    Args:
        branch (Branch): The Git branch containing commit and user data.
        filepath (str): The path to the output PDF file.

    """
    with PdfPages(filepath) as pdf:
        _plot_user_commits(branch, pdf)
        _plot_daily_commits(branch, pdf)
        _plot_commit_heatmap(branch, pdf)


def _plot_user_commits(branch: Branch, pdf: PdfPages) -> None:
    """Plot the number of commits per user and save the figure to the PDF."""
    if not branch.user_commits:
        return

    df_user = (
        pd.DataFrame.from_dict(branch.user_commits, orient="index", columns=["Commits"])
        .rename_axis("User")
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(df_user["User"], df_user["Commits"])
    ax.set_title(f"Commits per User — {branch.name}")
    ax.set_xlabel("User")
    ax.set_ylabel("Number of Commits")
    ax.set_xticks(np.arange(len(df_user)))
    ax.set_xticklabels(df_user["User"], rotation=45, ha="right")
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _plot_daily_commits(branch: Branch, pdf: PdfPages) -> None:
    """Plot daily commits activity over time and saves the figure to the PDF."""
    if not branch.day_commits:
        return

    df_time = pd.DataFrame(
        {
            "Date": list(branch.day_commits.keys()),
            "Commits": list(branch.day_commits.values()),
        },
    ).sort_values("Date")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df_time["Date"], df_time["Commits"], marker="o")
    ax.set_title(f"Commits Over Time — {branch.name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Commits")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _plot_commit_heatmap(branch: Branch, pdf: PdfPages) -> None:
    """Plot weekly commits heatmap and saves the figure to the PDF."""
    if not branch.day_commits:
        return

    df = pd.DataFrame(
        {
            "Date": [
                        datetime.strptime(d, "%d/%m/%Y")
                        for d in branch.day_commits
                    ],
            "Commits": list(branch.day_commits.values()),
        },
    )

    start = df["Date"].min()
    end = df["Date"].max()
    start_monday = start - timedelta(days=start.weekday())
    end_sunday = end + timedelta(days=(6 - end.weekday()))
    all_days = pd.DataFrame({"Date": pd.date_range(start_monday, end_sunday)})

    df = all_days.merge(df, on="Date", how="left", validate="many_to_many").fillna(0)
    df["WeekStart"] = df["Date"] - pd.to_timedelta(df["Date"].dt.weekday, unit="d")
    df["WeekStartStr"] = df["WeekStart"].dt.strftime("%Y-%m-%d")
    df["Weekday"] = df["Date"].dt.weekday

    heatmap = df.pivot_table(
        index="Weekday", columns="WeekStartStr", values="Commits",
    ).reindex(index=range(7), fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 4))
    cax = ax.imshow(
        heatmap.to_numpy(),
        aspect="auto",
        cmap="YlGnBu",
        origin="lower",
    )

    ax.set_yticks(np.arange(7))
    ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.set_xticks(np.arange(heatmap.shape[1]))
    ax.set_xticklabels(
        [
            datetime.strptime(w, "%Y-%m-%d").strftime("%d.%m")
            for w in heatmap.columns
        ],
        rotation=45,
        ha="right",
    )

    ax.set_xticks(np.arange(-0.5, heatmap.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 7, 1), minor=True)
    ax.grid(which="minor", color="gray", linestyle="--", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    fig.colorbar(cax, ax=ax, label="Commits")
    ax.set_title(f"Commit Heatmap — {branch.name}")
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)
