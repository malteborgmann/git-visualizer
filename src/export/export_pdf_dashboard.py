# TODO: Auslagern in mehrere Funktionen, damit es cleaner ist
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def create_dashboard_pdf(branch, filename="dashboard.pdf"):
    with PdfPages(filename) as pdf:
        # --------- Commits pro User ---------
        if branch.user_commits:
            df_user = pd.DataFrame.from_dict(
                branch.user_commits, orient="index", columns=["Commits"]
            )
            df_user.index.name = "User"
            df_user = df_user.reset_index()

            fig, ax = plt.subplots(figsize=(12, 4))
            ax.bar(df_user["User"], df_user["Commits"])
            ax.set_title(f"Commits per User — {branch.name}")
            ax.set_xlabel("User")
            ax.set_ylabel("Number of Commits")
            # Rotate user labels
            ax.set_xticks(np.arange(len(df_user)))
            ax.set_xticklabels(df_user["User"], rotation=45, ha="right")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # --------- Zeitreihe: Commits pro Tag ---------
        if branch.day_commits:
            df_time = pd.DataFrame(
                {
                    "Date": [
                        datetime.strptime(d, "%d/%m/%Y") for d in branch.day_commits
                    ],
                    "Commits": list(branch.day_commits.values()),
                }
            ).sort_values("Date")

            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(df_time["Date"], df_time["Commits"], marker="o")
            ax.set_title(f"Commits Over Time — {branch.name}")
            ax.set_xlabel("Date")
            ax.set_ylabel("Commits")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
            # Rotate date labels
            fig.autofmt_xdate(rotation=45)
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # --------- Heatmap: Commits pro Kalenderwoche und Wochentag ---------
        if branch.day_commits:
            df = pd.DataFrame(
                {
                    "Date": [
                        datetime.strptime(d, "%d/%m/%Y")
                        for d in branch.day_commits.keys()
                    ],
                    "Commits": list(branch.day_commits.values()),
                }
            )

            # Full week range
            start = df["Date"].min()
            end = df["Date"].max()
            start_monday = start - timedelta(days=start.weekday())
            end_sunday = end + timedelta(days=(6 - end.weekday()))
            all_days = pd.DataFrame({"Date": pd.date_range(start_monday, end_sunday)})

            df = all_days.merge(df, on="Date", how="left").fillna(0)
            df["WeekStart"] = df["Date"] - pd.to_timedelta(
                df["Date"].dt.weekday, unit="d"
            )
            df["WeekStartStr"] = df["WeekStart"].dt.strftime("%Y-%m-%d")
            df["Weekday"] = df["Date"].dt.weekday

            heatmap = df.pivot(
                index="Weekday", columns="WeekStartStr", values="Commits"
            ).reindex(index=range(7), fill_value=0)

            fig, ax = plt.subplots(figsize=(12, 4))
            cax = ax.imshow(
                heatmap.values, aspect="auto", cmap="YlGnBu", origin="lower"
            )

            # Axes labels
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

            # Grid between cells
            ax.set_xticks(np.arange(-0.5, heatmap.shape[1], 1), minor=True)
            ax.set_yticks(np.arange(-0.5, 7, 1), minor=True)
            ax.grid(which="minor", color="gray", linestyle="--", linewidth=0.5)
            ax.tick_params(which="minor", bottom=False, left=False)

            # Colorbar
            fig.colorbar(cax, ax=ax, label="Commits")

            ax.set_title(f"Commit Heatmap — {branch.name}")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"PDF-Dashboard gespeichert als '{filename}'")
