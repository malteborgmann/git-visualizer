from textual.app import App, ComposeResult
from textual.widgets import Tree
from core.models import Repository


class GitVisualizerApp(App):

    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def __init__(self, repository: Repository):
        super().__init__()
        self.repository = repository

    def compose(self) -> ComposeResult:
        tree = Tree("Branches")
        tree.root.expand()
        locals = tree.root.add("Local")
        remotes = tree.root.add("Remote")

        locals.expand()
        remotes.expand()
        
        
        for branch_name, branch in self.repository.branches.items():
            if branch.is_remote:
                remotes.add_leaf(branch_name)
            else:
                locals.add_leaf(branch_name)
        
        yield tree
        pass


        

