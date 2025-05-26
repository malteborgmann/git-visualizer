import os

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Input,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)
from textual.widgets.tree import TreeNode
from textual_plotext import PlotextPlot

from src.core.models import Branch, Repository
from src.export.export_pdf_dashboard import create_dashboard_pdf


class ExportRequested(Message):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        super().__init__()


class ExportDialog(ModalScreen):
    """Modal für Dateinamen-Eingabe beim Export."""

    def compose(self):
        with Container(id="export_modal"):
            yield Static("Enter export filename:", id="export_prompt")
            yield Input(placeholder="branches_report.pdf", id="export_filename")

            with Container(id="export_buttons"):
                yield Button("OK", id="export_ok")
                yield Button("Cancel", id="export_cancel")

    def on_mount(self):
        input_field = self.query_one("#export_filename", Input)
        self.set_focus(input_field)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "export_ok":
            raw_input = (
                self.query_one("#export_filename", Input).value.strip()
                or "branches_report.pdf"
            )

            export_path = os.path.join(os.getcwd(), raw_input)
            if not export_path.endswith(".pdf"):
                export_path += ".pdf"

            self.app.export_requested(ExportRequested(export_path))  # type: ignore
        self.dismiss()


class GitVisualizerApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_tab", "Toggle Tab"),
        ("x", "export_graphs", "Export Data"),
    ]

    def __init__(self, repository: Repository):
        super().__init__()
        self.repository = repository
        self.current_branch: Branch

    def compose(self) -> ComposeResult:
        # ==========================
        # BRANCH TREE AND STATS
        # ==========================
        tree = Tree("Branches", id="branch_tree")
        tree.root.expand()

        locals = tree.root.add("Local")
        remotes = tree.root.add("Remote")

        locals.expand()
        remotes.expand()

        self.setup_tree_branches(locals, remotes)

        stats = Vertical(
            Static(f"📁 Files: {self.repository.total_files}", id="stat_files"),
            Static(f"📦 Ignored: {self.repository.ignored}", id="stat_ignored"),
            Static(f"📄 Lines of Code (LOC): {self.repository.loc}", id="stat_lines"),
            Static(
                f"🪝 Hooks: {self.repository.hooks if self.repository.hooks else 'None'}",
                id="stat_hooks",
            ),
            id="stats_header",
        )

        branch_tree_and_stats = Vertical(tree, stats, id="left_column")
        yield branch_tree_and_stats

        # ===========================
        # DataTable and Details
        # ===========================

        data_table = DataTable(
            name="data_table",
            id="data_table",
            show_header=True,
            show_row_labels=True,
            cursor_type="row",
        )

        details_plots_column = Vertical(
            data_table,
            Static("Select a commit to see details", id="details"),
        )

        # ==========================
        # PLOTS AND Analytics
        # ==========================

        plots = Vertical(
            PlotextPlot(id="plot_user_commits"),
            PlotextPlot(id="time_series_plot"),
            PlotextPlot(id="added_deleted_lines"),
            id="plots_column",
        )

        # ==========================
        # TABS
        # ==========================
        with TabbedContent(initial="CommitsTab"):
            with TabPane("Commits", id="CommitsTab"):
                yield details_plots_column
            with TabPane("Stats", id="StatsTab"):
                yield plots

        yield Footer()

    def on_mount(self) -> None:
        # self.query_one(Tabs).focus()
        table = self.query_one(DataTable)
        table.add_columns(
            *(
                "Hash",
                "Author",
                "Email",
                "Date",
                "Message",
            )
        )

        # TODO:
        plot = self.query_one("#plot_user_commits", PlotextPlot)
        plot.plt.title("Commits per User")
        plot.plt.xlabel("User")
        plot.plt.ylabel("Number of Commits")
        plot.plt.grid(True)
        plot.plt.bar([], [])  # Initial empty bar chart
        plot.refresh()

        plot = self.query_one("#time_series_plot", PlotextPlot)
        plot.plt.title("Commits over Time")

        plot.plt.grid(True)
        plot.plt.bar([], [])  # Initial empty bar chart
        plot.refresh()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node: TreeNode = event.node
        branch = node.data
        if not isinstance(branch, Branch):
            return

        self.current_branch = branch
        table = self.query_one("#data_table", DataTable)
        table.clear()

        for hash, commit in branch.commits.items():
            table.add_row(
                hash[:7],
                commit.author_name,
                commit.author_email,
                commit.date.strftime("%Y-%m-%d %H:%M:%S"),
                commit.message[:70],
                key=hash,
            )

        self.setup_user_commit_plot(
            list(branch.user_commits.keys()), list(branch.user_commits.values())
        )
        self.setup_time_series_plot(
            list(branch.day_commits.keys()), list(branch.day_commits.values())
        )
        self.setup_added_delete_plot()

    def setup_added_delete_plot(self):
        pass

    def setup_time_series_plot(self, labels=[], values=[]) -> None:
        """Erzeugt oder aktualisiert das Balkendiagramm mit neuen Daten."""
        plot = self.query_one("#time_series_plot", PlotextPlot)
        plt = plot.plt
        plt.clear_data()
        # plt.data_form = "%d/%m/%Y"
        # plt.plot(labels, values, marker="dot")

        num_points = len(values)
        if num_points == 0:
            plot.refresh()
            return

        x = list(
            range(num_points)
        )  # Cant use labels directly due to a issue in the textualize package
        plt.plot(x, values, color="cyan")
        ticks = min(10, num_points)

        positions = [int(i * (num_points - 1) / (ticks - 1)) for i in range(ticks)]
        tick_labels = [labels[i] for i in positions]
        plt.xticks(positions, tick_labels)

        # TODO: Einbauen, dass Y-Achsen keine Floats sind

        plot.refresh()

    def setup_user_commit_plot(self, labels: list[str], values: list[int]) -> None:
        """Erzeugt oder aktualisiert das Balkendiagramm mit neuen Daten."""
        plot = self.query_one("#plot_user_commits", PlotextPlot)
        plt = plot.plt
        plt.clear_data()
        # plt = self.query_one(PlotextPlot).plt             # löscht alte Daten
        plt.bar(labels, values)  # setzt neue Balken
        plot.refresh()

    def on_data_table_row_highlighted(self, event) -> None:
        """
        Wird aufgerufen, wenn man in der Tabelle eine Zeile markiert.
        """
        if self.current_branch is None:
            return

        full_hash = event.row_key
        commit = self.current_branch.commits.get(full_hash)

        if commit is None:
            return

        details = self.query_one("#details")

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
            f"[b]Changed files:[/b]\n"
            + ("\n".join(f"- {f.path}" for f in changed) or "–")
        )

    def setup_tree_branches(self, locals, remotes):
        for branch_name, branch in self.repository.branches.items():
            # Wähle den richtigen Eltern-Knoten
            parent: TreeNode = remotes if branch.is_remote else locals
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
            category_node = parent.add(str(category))
            category_node.expand()
            category_node.add_leaf(branch_name, branch)

    def action_toggle_tab(self) -> None:
        """An action to the activated tab."""
        content = self.query_one(TabbedContent)
        if content.active is None:
            return
        elif content.active == "CommitsTab":
            content.active = "StatsTab"
        elif content.active == "StatsTab":
            content.active = "CommitsTab"

    def action_export_graphs(self) -> None:
        """Öffnet das Export-Dialogfenster."""
        self.push_screen(ExportDialog())

    def export_requested(self, event: ExportRequested) -> None:
        if not self.current_branch:
            self.notify("First select a Branch", timeout=3)
            return
        filename = event.filename
        create_dashboard_pdf(self.current_branch, filename)
        self.notify(f"Exported to {filename}", timeout=3)


def node_exists_by_label(parent: TreeNode, label: str) -> bool:
    return any(child.label == label for child in parent.children)
