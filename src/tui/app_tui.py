from textual.app import App, ComposeResult
from textual.widgets import Tree, LoadingIndicator, Static, DataTable
from core.models import Repository, Branch
from textual.widgets.tree import TreeNode

class GitVisualizerApp(App):

    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def __init__(self, repository: Repository):
        super().__init__()
        self.repository = repository
        self.current_branch: Branch = None

    def compose(self) -> ComposeResult:
        tree = Tree("Branches", id="branch_tree")
        tree.root.expand()
        locals = tree.root.add("Local")
        remotes = tree.root.add("Remote")

        locals.expand()
        remotes.expand()
        
        
        for branch_name, branch in self.repository.branches.items():
            if branch.is_remote:
                remotes.add_leaf(branch_name, branch)
            else:
                locals.add_leaf(branch_name, branch)
        
        yield tree
        
        yield DataTable(name="data_table", id="data_table", show_header=True, show_row_labels=True, cursor_type="row")
        yield Static("Select a commit to see details", id="details")
        

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*(
            "Hash",
            "Author",
            "Email",
            "Date",
            "Message",
        ))

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node: TreeNode = event.node
        branch = node.data
        if not isinstance(branch, Branch):
            return

        self.current_branch = branch
        table = self.query_one(DataTable)
        table.clear()

        for hash, commit in branch.commits.items():
            table.add_row(
                hash[:7],
                commit.author_name,
                commit.author_email,
                commit.date.strftime("%Y-%m-%d %H:%M:%S"),
                commit.message[:70],
                key=hash  # speichern wir den vollen Hash als Schlüssel
            )

    def on_data_table_row_highlighted(self, event) -> None:
        """
        Wird aufgerufen, wenn man in der Tabelle eine Zeile markiert.
        """
        if self.current_branch is None:
            return

        # Ausgewählte Zeile per key abfragen:
        full_hash = event.row_key  # wir haben den vollen Hash als key gesetzt
        commit = self.current_branch.commits.get(full_hash)

        if commit is None:
            return
        

        details = self.query_one(Static)
        # Prüfe, ob commit.added, .deleted, .changed existieren:
        added   = str(commit.lines_added)
        deleted = str(commit.lines_deleted)
        changed = commit.changed_files

        details.update(
            f"[b]Commit:[/b] {commit.hash}\n"
            f"[b]Author:[/b] {commit.author_name}\n"
            f"[b]Date:[/b] {commit.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"[b]Message:[/b]\n{commit.message}\n\n"
            f"[b]Added:[/b] {added}\n"
            f"[b]Deleted:[/b] {deleted}\n"
            f"[b]Changed files:[/b]\n" +
            ("\n".join(f"- {f.path}" for f in changed) or "–")
        )

        




"""
# git_visualizer.py
from textual.app import App, ComposeResult
from textual.widgets import Tree, DataTable, Static
from textual.widgets.tree import TreeNode
from core.models import Repository

class GitVisualizerApp(App):

    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def __init__(self, repository: Repository):
        super().__init__()
        self.repository = repository
        self.current_branch = None  # merken, welche Branch ausgewählt ist

    def compose(self) -> ComposeResult:
        # Links: Branch-Tree
        yield Tree("Branches", id="branch_tree")

        # Mitte: Commit-Tabelle
        yield DataTable(id="data_table", show_header=True, show_row_labels=True)

        # Rechts: Detail-Panel
        yield Static("Select a commit to see details", id="details")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        # === Hier werden die Spalten definiert ===
        table.add_columns(
            "Hash",
            "Author",
            "Date",
            "Message"
        )

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node: TreeNode = event.node
        branch = node.data

        # Nur fortfahren, wenn es ein Branch-Objekt mit commits ist
        if branch is None or not hasattr(branch, "commits"):
            return

        self.current_branch = branch

        table = self.query_one(DataTable)
        table.clear()

        # === Hier werden die Zeilen (Commits) hinzugefügt ===
        for full_hash, commit in branch.commits.items():
            table.add_row(
                full_hash[:7],                            # Hash (abgekürzt)
                commit.author_name,                       # Author
                commit.date.strftime("%Y-%m-%d %H:%M:%S"),# Datum
                commit.message[:70]                       # gekürzte Message
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if self.current_branch is None:
            return

        table = event.sender  # das DataTable-Widget
        row = table.get_row(event.row_key)
        short_hash = row[0]  # abgekürzter Hash aus der ersten Spalte

        # Volle Hash-ID anhand der Kürzel finden
        full_hash = next(h for h in self.current_branch.commits if h.startswith(short_hash))
        commit = self.current_branch.commits[full_hash]

        details = self.query_one(Static, id="details")
        # === Hier füllen wir das Detail-Panel mit allen Infos ===
        details.update(
            f"[b]Commit:[/b] {full_hash}\n"
            f"[b]Author:[/b] {commit.author_name}\n"
            f"[b]Date:[/b] {commit.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"[b]Message:[/b]\n{commit.message}\n\n"
            f"[b]Added:[/b] {commit.added}\n"
            f"[b]Deleted:[/b] {commit.deleted}\n"
            f"[b]Changed files:[/b]\n" +
            "\n".join(f"- {fname}" for fname in commit.changed)
        )

if __name__ == "__main__":
    # Beispiel: Repository initialisieren und App starten
    repo = Repository.load_from_path("/path/to/your/.git")
    app = GitVisualizerApp(repo)
    app.run()"""