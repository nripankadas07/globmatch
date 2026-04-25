"""Basic pattern matching: literals, ``*``, ``?``, path semantics."""

from __future__ import annotations

import pytest

from globmatch import match


@pytest.mark.parametrize(
    "pattern, text, expected",
    [
        ("", "", True),
        ("", "x", False),
        ("abc", "abc", True),
        ("abc", "abd", False),
        ("abc", "abcx", False),
        ("a?c", "abc", True),
        ("a?c", "ac", False),
        ("a?c", "a/c", False),
        ("*", "anything", True),
        ("*", "", True),
        ("*", "a/b", False),
        ("a*c", "abc", True),
        ("a*c", "abbbbc", True),
        ("a*c", "ac", True),
        ("a*c", "a/c", False),
        ("*.py", "main.py", True),
        ("*.py", "test.txt", False),
    ],
)
def test_literal_and_wildcard_match(pattern, text, expected):
    assert match(pattern, text) is expected


@pytest.mark.parametrize(
    "pattern, text, expected",
    [
        ("**", "anything", True),
        ("**", "a/b/c", True),
        ("**.py", "pkg/deep/mod.py", True),
        ("src/**/*.py", "src/pkg/mod.py", True),
        ("src/**/*.py", "src/mod.py", True),
        ("src/**/*.py", "src/a/b/c/mod.py", True),
        ("src/**/*.py", "other/mod.py", False),
        ("src/*/mod.py", "src/pkg/mod.py", True),
        ("src/*/mod.py", "src/a/b/mod.py", False),
    ],
)
def test_globstar_vs_single_star_path_semantics(pattern, text, expected):
    assert match(pattern, text) is expected


def test_escape_of_metacharacter():
    assert match(r"a\*b", "a*b") is True
    assert match(r"a\*b", "aXb") is False
    assert match(r"a\?b", "a?b") is True


def test_empty_match_everything():
    assert match("*", "") is True
