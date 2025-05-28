from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.widgets.tree import TreeNode

from src.core.models import Branch, Repository
from src.export.export_pdf_dashboard import create_dashboard_pdf
from src.tui.export_dialog import ExportDialog, ExportRequestMessage
from src.tui.plots.TimeSeriesPlot import TimeSeriesPlot
from src.tui.plots.UserCommitPlot import UserCommitPlot


class GitVisualizerApp(App):
    """Main App using textual package.

    Package: https://textual.textualize.io/
    """

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_tab", "Toggle Tab"),
        ("x", "export_graphs", "Export Data"),
    ]

    def __init__(self, repository: Repository) -> None:  # noqa: D107
        super().__init__()
        self.repository = repository
        self.current_branch: Branch = None

    def compose(self) -> ComposeResult:
        """Call by Textual to create child widgets.

        Reference: https://textual.textualize.io/api/widget/#textual.widget.Widget.compose
        """
        # ==========================
        # BRANCH TREE AND STATS
        # ==========================
        tree = Tree("Branches", id="branch_tree")
        tree.root.expand()

        local_tree: TreeNode = tree.root.add("Local")
        remote_tree: TreeNode = tree.root.add("Remote")

        local_tree.expand()
        remote_tree.expand()

        self.setup_tree_branches(local_tree, remote_tree)

        stats = Vertical(
            Static(f"Files: {self.repository.total_files}", id="stat_files"),
            Static(f"Ignored: {self.repository.ignored}", id="stat_ignored"),
            Static(f"Lines of Code (LOC): {self.repository.loc}", id="stat_lines"),
            Static(
                f"Hooks: {' '.join(self.repository.hooks) if self.repository.hooks else 'None'}",
                id="stat_hooks",
            ),
            id="stats_header",
        )

        branch_tree_and_stats = Vertical(tree, stats, id="left_column")

        # ===========================
        # DataTable and Details
        # ===========================

        data_table = DataTable(
            id="data_table",
            show_header=True,
            show_row_labels=True,
            cursor_type="row",
        )

        commit_table_and_details = Vertical(
            data_table,
            Static("Select a commit to see details", id="commit_details"),
        )

        # ==========================
        # PLOTS AND Analytics
        # ==========================

        plots = Vertical(
            UserCommitPlot(id="plot_user_commits"),
            TimeSeriesPlot(id="time_series_plot"),
            id="plots_column",
        )

        # ==========================
        # Yield - Create App
        # ==========================

        yield branch_tree_and_stats

        with TabbedContent(initial="CommitsTab"):
            with TabPane("Commits", id="CommitsTab"):
                yield commit_table_and_details
            with TabPane("Stats", id="StatsTab"):
                yield plots

        yield Footer()

    def on_mount(self) -> None:
        """Add non-changing data to all components.

        Textual executes this method right after rendering the App.
        """
        table = self.query_one(DataTable)
        table.add_columns(
            *(
                "Hash",
                "Author",
                "Email",
                "Date",
                "Message",
            ),
        )

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """"""
        node: TreeNode = event.node

        if not node.data:  # Necessary for categories
            return

        self.current_branch = node.data
        table = self.query_one("#data_table", DataTable)
        table.clear()

        for hash, commit in self.current_branch.commits.items():
            table.add_row(
                hash[:7],  # Short ref of hash is 7 chars long
                commit.author_name,
                commit.author_email,
                commit.date.strftime("%Y-%m-%d %H:%M:%S"),
                commit.message[:70],
                key=hash,
            )


        self.query_one("#plot_user_commits", UserCommitPlot).update(
            list(self.current_branch.user_commits.keys()),
            list(self.current_branch.user_commits.values()),
        )

        self.query_one("#time_series_plot", TimeSeriesPlot).update(
            list(self.current_branch.day_commits.keys()),
            list(self.current_branch.day_commits.values()),
        )

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Change static Widget after new row is selected in the DataTable."""
        if self.current_branch is None:
            return

        full_hash = event.row_key
        commit = self.current_branch.commits.get(full_hash)

        if commit is None:
            return

        details = self.query_one("#commit_details", Static)

        added = str(commit.lines_added)
        deleted = str(commit.lines_deleted)
        changed = commit.changed_files

        details.update(
            f"[b]Commit:[/b] {commit.hash}\n"
            f"[b]Author:[/b] {commit.author_name}\n"
            f"[b]Date:[/b] {commit.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"[b]Message:[/b]\n{commit.message}\n\n"
            f"[b]Added:[/b] {added}\n"
            f"[b]Deleted:[/b] {deleted}\n"
            f"[b]Changed files:[/b]\n" + ("\n".join(f"- {f.path}" for f in changed) or "–"),
        )

    def setup_tree_branches(self, local_tree: TreeNode, remote_tree: TreeNode) -> None:
        """Add leaves to local and remote subtrees."""
        for branch_name, branch in self.repository.branches.items():
            # Selecting the parent Node. Either it is local or remote
            parent: TreeNode = remote_tree if branch.is_remote else local_tree
            category = branch.category  # z.B. "feature", "bugfix" etc.

            branch_name = branch.name.split("/")[-1]

            if category is None:
                parent.add_leaf(branch_name, branch)
                continue

            exists = False
            for child in parent.children:
                if str(child.label.plain) == str(category):
                    child.add_leaf(branch_name, branch)
                    exists = True
                    break
            if exists:
                continue

            # Add categories
            category_node = parent.add(str(category))
            category_node.expand()
            category_node.add_leaf(branch_name, branch)

    def action_toggle_tab(self) -> None:
        """Switch Tab on press of button "t"."""
        content = self.query_one(TabbedContent)
        if content.active is None:
            return
        if content.active == "CommitsTab":
            content.active = "StatsTab"
        elif content.active == "StatsTab":
            content.active = "CommitsTab"

    def action_export_graphs(self) -> None:
        """Push the export Dialog onto the current screen."""
        self.push_screen(ExportDialog())

    def on_export_requested(self, event: ExportRequestMessage) -> None:
        """
        Trigger the creation of PDF Dashboard.

        Calling the function that creates the PDF. Gets triggered by the button press
        of the ExportDialog OK Button

        Args:
            event: ExportRequestMessage

        """
        if not self.current_branch:
            self.notify("First select a Branch", timeout=3)
            return
        filename = event.filename
        create_dashboard_pdf(self.current_branch, filename)
        self.notify(f"Exported to {filename}", timeout=3)
