from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from datetime import datetime

def create_dashboard_pdf(repository, filename="dashboard.pdf"):
    with PdfPages(filename) as pdf:
        for branch in repository.branches.values():
        
            labels = list(branch.user_commits.keys())
            counts = list(branch.user_commits.values())
            fig, ax = plt.subplots()
            ax.bar(labels, counts)
            ax.set_title(f"Commits per User — {branch.name}")
            ax.set_xlabel("User")
            ax.set_ylabel("Number of Commits")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

     
            dates = list(branch.day_commits.keys())
            values = list(branch.day_commits.values())

            dates_dt = [datetime.strptime(d, "%d/%m/%Y") for d in dates]
            fig, ax = plt.subplots()
            ax.plot(dates_dt, values)
            ax.set_title(f"Commits Over Time — {branch.name}")
            ax.set_xlabel("Date")
            ax.set_ylabel("Commits")
            fig.autofmt_xdate() 
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"PDF-Dashboard gespeichert als '{filename}'")
