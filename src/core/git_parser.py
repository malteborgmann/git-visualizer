import subprocess
from datetime import datetime, timezone
from typing import List, Dict

from core.models import Commit, Branch, Repository # Ensure models.py is in the same directory

def _run_git_command(command: List[str], repo_path: str) -> str:
    """Executes a Git command in the specified repository path and returns its output."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8' # Important for correct character encoding
        )
        return result.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError("Git command not found. Please ensure Git is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        error_message = f"Git command failed with error: {e.stderr.strip()}"
        if "not a git repository" in e.stderr.lower() or \
           "fatal: Invalid gitfile format" in e.stderr.lower() or \
           "detected dubious ownership in repository at" in e.stderr.lower(): # The latter for workarounds in CI systems
             # Try passing the path directly to git if -C causes issues
            try:
                git_dir_arg = f"--git-dir={repo_path}/.git"
                work_tree_arg = f"--work-tree={repo_path}"
                base_command = ["git", git_dir_arg, work_tree_arg]
                
                # Test if it is a bare repo
                is_bare_check = subprocess.run(base_command + ["rev-parse", "--is-bare-repository"],
                                               capture_output=True, text=True, check=False, encoding='utf-8')
                if is_bare_check.stdout.strip() == "true":
                     base_command = ["git", f"--git-dir={repo_path}"] # For bare repos, work-tree is not necessary

                result = subprocess.run(
                    base_command + command,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='utf-8'
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as e2:
                error_message = f"Git command failed: {e.stderr.strip()}. Secondary attempt failed: {e2.stderr.strip()}"
                raise ValueError(f"The path '{repo_path}' is not a valid Git repository or cannot be accessed. Error: {error_message}")
        raise RuntimeError(error_message)

def parse_commits(repo_path: str) -> Dict[str, Commit]:
    """Parses all commits from the repository."""
    commits_data: Dict[str, Commit] = {}
    commit_separator = "---GIT_COMMIT_SEPARATOR---"
    field_separator = "<FIELD_SEP>"
    
    # %H: Hash, %an: Author name, %ae: Author email, %ct: Committer date (Unix timestamp), %B: Full commit message, %P: Parent hashes
    log_format = f"%H{field_separator}%an{field_separator}%ae{field_separator}%ct{field_separator}%B{field_separator}%P"

    raw_log_output = _run_git_command(
        ["log", "--all", f"--pretty=format:{log_format}{commit_separator}"],
        repo_path
    )

    if not raw_log_output:
        return {}

    raw_commits = raw_log_output.split(commit_separator)

    for raw_commit_entry in raw_commits:
        if not raw_commit_entry.strip():
            continue

        parts = raw_commit_entry.strip().split(field_separator)
        if len(parts) != 6: # Expects 6 parts based on log_format
            # print(f"Skipping malformed commit entry: {'|'.join(parts)}") # For debugging
            continue

        commit_hash, author_name, author_email, committer_timestamp_str, message, parent_hashes_str = parts

        # Get numstat for this specific commit
        # `git log -1 --numstat --pretty=format: <hash>` outputs only the numstat lines
        numstat_output = _run_git_command(
            ["log", "-1", commit_hash, "--numstat", "--pretty=format:"],
            repo_path
        )

        lines_added = 0
        lines_deleted = 0
        
        numstat_lines = numstat_output.splitlines()
        for line in numstat_lines:
            line = line.strip()
            if not line:
                continue
            
            stat_parts = line.split('\t')
            if len(stat_parts) == 3:
                added_str, deleted_str, _ = stat_parts
                if added_str != '-': # Binary files are marked with '-'
                    lines_added += int(added_str)
                if deleted_str != '-':
                    lines_deleted += int(deleted_str)
        
        try:
            committer_timestamp = int(committer_timestamp_str)
            commit_date = datetime.fromtimestamp(committer_timestamp, tz=timezone.utc)
        except ValueError:
            # Fallback or error handling if timestamp is incorrect
            commit_date = datetime.now(timezone.utc) # Or None, or raise Error
            # print(f"Warning: Could not parse timestamp for commit {commit_hash}")

        parents = parent_hashes_str.split() if parent_hashes_str else []

        commits_data[commit_hash] = Commit(
            hash=commit_hash,
            author_name=author_name.strip(),
            author_email=author_email.strip(),
            date=commit_date,
            message=message.strip(),
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            parents=parents
        )
    return commits_data

def parse_branches(repo_path: str) -> Dict[str, Branch]:
    """Parses all local and remote branches."""
    branches_data: Dict[str, Branch] = {}
    field_separator = "<FIELD_SEP>"

    # Local branches
    # %(refname:short) gives the short name of the branch
    # %(objectname) gives the commit hash the branch points to
    try:
        raw_local_branches = _run_git_command(
            ["branch", f"--format=%(refname:short){field_separator}%(objectname)"],
            repo_path
        )
        if raw_local_branches:
            for line in raw_local_branches.splitlines():
                if not line.strip():
                    continue
                name, head_hash = line.strip().split(field_separator)
                branches_data[name] = Branch(name=name, head_commit_hash=head_hash, is_remote=False)
    except RuntimeError as e:
        print(f"Could not parse local branches: {e}") # Non-critical, maybe no branches

    # Remote branches
    try:
        raw_remote_branches = _run_git_command(
            ["branch", "-r", f"--format=%(refname:short){field_separator}%(objectname)"],
            repo_path
        )
        if raw_remote_branches:
            for line in raw_remote_branches.splitlines():
                if not line.strip() or "HEAD ->" in line: # Ignore HEAD -> origin/main
                    continue
                name, head_hash = line.strip().split(field_separator)
                branches_data[name] = Branch(name=name, head_commit_hash=head_hash, is_remote=True)
    except RuntimeError as e:
        print(f"Could not parse remote branches: {e}") # Non-critical, maybe no remotes
        
    return branches_data

def load_repository_data(repo_path: str) -> Repository:
    """Loads all relevant data from the Git repository."""
    # The validity of the repo is checked by _run_git_command and is_valid_git_repo (in main)
    
    commits = parse_commits(repo_path)
    branches = parse_branches(repo_path)
    
    return Repository(path=repo_path, commits=commits, branches=branches) 