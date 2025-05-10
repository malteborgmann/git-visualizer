from textual.app import App, ComposeResult
from textual.widgets import Tree, LoadingIndicator, Static, DataTable
from core.models import Repository, Branch
from textual.widgets.tree import TreeNode


class GitVisualizerApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [("q", "quit", "Quit")]

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
            # Wähle den richtigen Eltern-Knoten
            parent: TreeNode = remotes if branch.is_remote else locals
            category = branch.category  # z.B. "feature", "bugfix" etc.

            if category is None:
                parent.add_leaf(branch_name, branch)
                continue
            
            exists = False
            for child in parent.children:
                if str(child.label.plain) == str(category):
                    child.add_leaf(branch_name, branch)
                    exists = True
                    continue
            if exists:
                continue
            category_node = parent.add(str(category))
            category_node.expand()
            category_node.add_leaf(branch_name, branch)

        yield tree

        yield DataTable(
            name="data_table",
            id="data_table",
            show_header=True,
            show_row_labels=True,
            cursor_type="row",
        )
        yield Static("Select a commit to see details", id="details")

    def on_mount(self) -> None:
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
                key=hash,
            )

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

        details = self.query_one(Static)

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

def node_exists_by_label(parent: TreeNode, label: str) -> bool:
    return any(child.label == label for child in parent.children)
