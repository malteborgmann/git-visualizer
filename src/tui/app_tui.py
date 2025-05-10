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
        
        yield DataTable(name="data_table", id="data_table", show_header=True, show_row_labels=True)
        

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*(
            "Hash",
            "Author",
            "Date",
            "Message",
            "Lines Added",
            "Lines Deleted",
            "Files Changed"
        ))

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        branch = node.data

        # Stelle sicher, dass es sich wirklich um ein Branch-Objekt handelt
        if branch is None or not hasattr(branch, "commits"):
            return

        table = self.query_one(DataTable)
        table.clear()

        for commit_hash, commit in branch.commits.items():
            table.add_row(
                commit_hash[:7],
                commit.author_name,
                commit.date.strftime("%Y-%m-%d %H:%M:%S"),
                commit.message,
                str(commit.lines_added),
                str(commit.lines_deleted),
                str(len(commit.changed_files))
            )

        




