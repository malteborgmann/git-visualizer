import json
import os
import pytest
from src.utils.branch_json_utils import classify_branch

CONFIG_DATA = {
    "feature": {
        "pattern": ".*feature/.*",
        "description": "Branches for new features and enhancements",
    },
    "bugfix": {
        "pattern": ".*bugfix/.*",
        "description": "Branches for non-critical bug fixes",
    },
    "hotfix": {
        "pattern": ".*hotfix/.*",
        "description": "Branches for critical production fixes",
    },
    "release": {
        "pattern": ".*release/.*",
        "description": "Branches for preparing new releases",
    },
}


def test_classify_branch():
    test_cases = {
        "feature/new-ui": "feature",
        "origin/feature/xyz": "feature",
        "bugfix/123-fix": "bugfix",
        "hotfix/v2.0.1-critical": "hotfix",
        "release/3.0.0": "release",
        "docs/readme": None,
    }

    for branch, expected in test_cases.items():
        expected = expected.capitalize() if expected else None
        result = classify_branch(branch, CONFIG_DATA)
        assert result == expected, (
            f"Branch '{branch}' sollte '{expected}' sein, got '{result}'"
        )
