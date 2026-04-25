"""Implementation of globmatch — fnmatch + extglob + POSIX classes + globstar."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

__all__ = ["CompiledGlob", "GlobError", "compile", "filter_names", "match", "translate"]

_POSIX = {
    "alnum": r"A-Za-z0-9", "alpha": r"A-Za-z", "blank": r" \t",
    "cntrl": r"\x00-\x1f\x7f", "digit": r"0-9", "graph": r"\x21-\x7e",
    "lower": r"a-z", "print": r"\x20-\x7e", "punct": r"!-/:-@\[-`\{-~",
    "space": r" \t\r\n\v\f", "upper": r"A-Z", "xdigit": r"0-9A-Fa-f",
}


class GlobError(ValueError):
    """Raised on malformed pattern or non-string input."""


def _translate(pattern: str) -> str:
    """Translate pattern to a regex string anchored at both ends."""
    if not isinstance(pattern, str):
        raise GlobError("pattern must be a string")
    out = []
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == "*":
            if i + 1 < n and pattern[i+1] == "*":
                # ** or **/
                if i + 2 < n and pattern[i+2] == "/":
                    out.append(r"(?:.*/)?")
                    i += 3
                else:
                    out.append(r".*")
                    i += 2
            else:
                out.append(r"[^/]*")
                i += 1
        elif c == "?":
            out.append(r"[^/]")
            i += 1
        elif c == "\\":
            if i + 1 >= n:
                raise GlobError("dangling escape")
            out.append(re.escape(pattern[i+1]))
            i += 2
        elif c == "[":
            j = i + 1
            if j >= n:
                raise GlobError("unclosed character class")
            negated = False
            if pattern[j] in "!^":
                negated = True
                j += 1
            if j >= n or pattern[j] == "]":
                raise GlobError("empty or unclosed character class")
            cls = []
            while j < n and pattern[j] != "]":
                if pattern.startswith("[:", j):
                    end = pattern.find(":]", j + 2)
                    if end == -1:
                        raise GlobError("unclosed POSIX class")
                    name = pattern[j+2:end]
                    if name not in _POSIX:
                        raise GlobError(f"unknown POSIX class: {name}")
                    cls.append(_POSIX[name])
                    j = end + 2
                elif pattern[j] == "\\" and j + 1 < n:
                    cls.append(re.escape(pattern[j+1]))
                    j += 2
                else:
                    cls.append(re.escape(pattern[j]))
                    j += 1
            if j >= n:
                raise GlobError("unclosed character class")
            out.append("[" + ("^" if negated else "") + "".join(cls) + "]")
            i = j + 1
        elif c in "?*+@!" and i + 1 < n and pattern[i+1] == "(":
            # Extglob group
            j = i + 2
            depth = 1
            while j < n and depth > 0:
                if pattern[j] == "(":
                    depth += 1
                elif pattern[j] == ")":
                    depth -= 1
                if depth > 0:
                    j += 1
            if depth != 0:
                raise GlobError("unclosed extglob group")
            inner = pattern[i+2:j]
            alts = "|".join(_translate(a) for a in inner.split("|"))
            if c == "@":
                out.append(f"(?:{alts})")
            elif c == "?":
                out.append(f"(?:{alts})?")
            elif c == "*":
                out.append(f"(?:{alts})*")
            elif c == "+":
                out.append(f"(?:{alts})+")
            else:  # !
                out.append(rf"(?:(?!(?:{alts})(?:$|/))[^/])*")
            i = j + 1
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out)


@dataclass(frozen=True)
class CompiledGlob:
    pattern: str
    case_sensitive: bool
    _re: object

    def match(self, text: str) -> bool:
        if not isinstance(text, str):
            raise GlobError("text must be a string")
        return self._re.match(text) is not None

    def filter(self, names: Iterable[str]) -> List[str]:
        return [n for n in names if self.match(n)]


def compile(pattern: str, *, case_sensitive: bool = True) -> CompiledGlob:
    body = _translate(pattern)
    flags = 0 if case_sensitive else re.IGNORECASE
    return CompiledGlob(pattern, case_sensitive, re.compile("^" + body + "$", flags))


def match(pattern: str, text: str, *, case_sensitive: bool = True) -> bool:
    return compile(pattern, case_sensitive=case_sensitive).match(text)


def filter_names(names: Iterable[str], pattern: str, *, case_sensitive: bool = True) -> List[str]:
    return compile(pattern, case_sensitive=case_sensitive).filter(names)


def translate(pattern: str, *, case_sensitive: bool = True) -> str:
    body = _translate(pattern)
    prefix = "(?i)" if not case_sensitive else ""
    return f"{prefix}^{body}$"
