from textual.app import App, ComposeResult
from textual.widgets import Tree, LoadingIndicator, Static, DataTable, Label, TextArea, Tabs, TabbedContent, TabPane
from textual.scroll_view import ScrollView
from textual.containers import Vertical, ScrollableContainer, VerticalScroll
from textual_plotext import PlotextPlot

from src.core.models import Repository, Branch
from textual.widgets.tree import TreeNode


class GitVisualizerApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, repository: Repository):
        super().__init__()
        self.repository = repository
        self.current_branch: Branch = None

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
            Static(f"🪝 Hooks: {self.repository.hooks if self.repository.hooks else 'None'}",id="stat_hooks",),
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
            PlotextPlot(id="plot", name="plotext_plot"),
            id="plots_column",
        )

        



        # ==========================
        # TABS
        # ==========================
        with TabbedContent(initial="jessica"):
            with TabPane("Commits", id="CommitsTab"):
                yield details_plots_column
            with TabPane("Stats", id="StatsTab"):
                yield plots


    def on_mount(self) -> None:
        #self.query_one(Tabs).focus()
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
        self.plot = self.query_one(PlotextPlot)
        self.plot.plt.title("Commits per User")

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs."""
        print(f"Tab activated: {event.tab.id}")
        l = self.query_one(Label)
        if event.tab.id == "one":
            l.visible = True
        elif event.tab.id == "two":
            l.visible = False
       

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node: TreeNode = event.node
        branch = node.data
        if not isinstance(branch, Branch):
            return

        self.current_branch = branch
        table = self.query_one("#data_table")
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

        self.setup_plot(branch.user_commits.keys(), branch.user_commits.values())

    def setup_plot(self, labels: list[str], values: list[int]) -> None:
        """Erzeugt oder aktualisiert das Balkendiagramm mit neuen Daten."""

        plot = self.plot
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



def node_exists_by_label(parent: TreeNode, label: str) -> bool:
    return any(child.label == label for child in parent.children)
