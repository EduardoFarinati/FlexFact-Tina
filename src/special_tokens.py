import re


IGNORE_AFTER = "X"
"""Ignore everything after X in a given name."""

COMMENT = ";"
"""Adding ; to the start of a name means it is ignored and the transition is enabled."""

IGNORE_AFTER_RE = re.compile(rf"{IGNORE_AFTER}.*")
"""Pattern to remove everything after IGNORE_AFTER token in a given name."""


def strip_name(name: str) -> str:
    """Remove everything after IGNORE_AFTER token in a given name."""
    return IGNORE_AFTER_RE.sub("", name)
