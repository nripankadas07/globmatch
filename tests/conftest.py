"""Force pytest to put its tmpdirs under /tmp to avoid the mounted
workspace cleanup loop documented in the Night 19 learnings."""

import os


def pytest_configure(config):
    if any(part == "mnt" for part in os.getcwd().split(os.sep)):
        config.option.basetemp = "/tmp/pytest-run/globmatch"
