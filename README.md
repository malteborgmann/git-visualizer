# git-visualizer

A console-based Python application to visualize and analyze local Git repositories.  
Features include commit statistics, ASCII branch diagrams, author mapping, branch categorization, and pre-commit hook detection.  
Built for the YZV 104E programming course.

## Features

- ASCII-based branch and merge visualization
- Commit details with change statistics (lines of code added/removed)
- Local and remote branch analysis
- Author and date filtering
- Pre-commit hook detection
- Interactive TUI powered by [Textual](https://github.com/Textualize/textual)

## Installation

### 1. Clone the repository
```
git clone https://github.com/malteborgmann/git-visualizer.git
cd git-visualizer
```

### 2. I always recommend to use a venv but thats optional
```
python3 -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
```

### 3. Installing dependencies
```
pip3 install -r requirements.txt
```

### 4. Run
```
python3 main.py
```

### HELP
```
python3 main.py --help
```
