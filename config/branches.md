# Branching Conventions Guide

This document outlines common Git branching conventions, naming patterns, and workflows used in software development teams.

## 1. Main Branches

- **main** (or **master**): Always reflect a production-ready state. Every commit in `main` should be deployable.
- **develop** (optional): Integration branch for features; contains the latest delivered development changes for the next release.

## 2. Supporting Branches

Supporting branches are used to develop features, prepare releases, and fix bugs. They exist as long as they’re needed.

| Branch Type | Prefix        | Purpose                                      | Naming Pattern                       |
|-------------|---------------|----------------------------------------------|--------------------------------------|
| Feature     | `feature/`    | New features or enhancements                 | `feature/<ticket>-<short-desc>`      |
| Bugfix      | `bugfix/`     | Non-critical bug fixes (post-release)        | `bugfix/<ticket>-<short-desc>`       |
| Hotfix      | `hotfix/`     | Critical fixes in production                 | `hotfix/<version>-<short-desc>`      |
| Release     | `release/`    | Prepare for a new production release         | `release/<version>`                  |
| Experiment  | `experiment/` | Prototype or spike work                      | `experiment/<short-desc>`            |

### Examples

- `feature/123-add-login-form`
- `bugfix/456-fix-nullpointer`
- `hotfix/1.2.1-fix-crash`
- `release/2.0.0`
- `experiment/ui-optimization`

## 3. Workflow Overview

1. **Branch off**: Developers branch off from `develop` (or `main` if no `develop` branch) for features.
2. **Work & Commit**: Make incremental commits to the feature branch.
3. **Pull Request**: Open a PR into `develop` (or `main`) when the work is ready.
4. **Review & Merge**: After code review and CI passing, merge back into the target branch.
5. **Delete Branch**: Clean up by deleting the remote branch after merge.
6. **Release**: When `develop` is stable, branch `release/x.y.z` to finalize version, bump metadata, then merge into both `main` and `develop` (to carry over any changes).
7. **Hotfix**: For production issues, branch from `main` as `hotfix/x.y.z`, fix, then merge into both `main` and `develop`.

## 4. Best Practices

- Keep branch names short but descriptive.
- Include ticket or issue ID if available.
- Use hyphens (-) as separators, not underscores.
- Reference the branch in commit messages and PR titles.
- Delete branches promptly after merge to keep the repository clean.

## 5. Tips for Teams

- **Consistency**: Agree on a naming scheme and enforce it via CI or Git hooks.
- **Automation**: Automate version bumps in release branches.
- **Documentation**: Document the workflow in the project’s README.
- **Tools**: Use branch protections to prevent direct pushes to `main` or `develop`.

